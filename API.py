# En este script vamos a realizar una API con FastAPi.

# En primer lugar importamos lo necesario de las librerías nuevas
# python -m uvicorn API:app --reload
# Documentación interactiva: http://127.0.0.1:8000/docs
from fastapi import FastAPI ,HTTPException
from pydantic import BaseModel
import json

# Importamos las funciones que necesitamos del resto del proyecto
from RAG import generar_respuesta, MENSAJE_SIN_INFO
from evaluar import evaluar
from embeddings import cargar_corpus
from buscador import buscar
from embeddings import embed_con_cache, construir_texto
from almacen import ingesta, crear_coleccion
import chromadb
import voyageai


# Creamos la aplicación.

app=FastAPI()

# Vamos en primer lugar a crear el primer get. Este nos va a devolver/leer los documentos de generación del corpus. 
# 
# Para ello vamos a definir en primer lugar la clase de estos documentos

class documentos_corpus(BaseModel): #Al heredar Base Model, pydantic nos permite validar que los objetos tengan tipo correcto, y permite convertirlo directamente a un JSON. 
    pregunta: str
    respuesta: str
    id: str
    categoria: str 
    fuente:str
    año:int

# Definimos una clase para el buscador y otra para su salida
class preguntas_buscadas(BaseModel):
   pregunta: str
   k: int
   categoria: str | None = None
   nombre_coleccioon: str

class preguntas_encontradas(BaseModel):
   id: str
   texto: str
   similitud: float
   categoria: str

class generacion_respuesta(BaseModel):
   pregunta:str
   k:int
   umbral:float
class texto_RAG(BaseModel):
   texto: str

class textos_basados_RAG(BaseModel):
   id: str
   texto: str
   similitud: float
   categoria: str

class documento_nuevo(BaseModel):
   pregunta: str
   respuesta: str
   categoria: str
   fuente: str
   año: int

#Esta clase incluye nones en todo porque si actualizamos el documento no tiene porque cambiar todo
class documento_actualizado(BaseModel):
    pregunta: str | None = None
    respuesta: str | None = None
    categoria: str | None = None
    fuente: str | None = None
    año: int | None = None

@app.get("/documentos")

def documentos():
    preguntas=cargar_corpus()
    preguntas_corpus=[]
    for pregunta in preguntas:
        objeto=documentos_corpus(pregunta=pregunta["pregunta"], respuesta=pregunta["respuesta"], id=pregunta["id"], categoria=pregunta["categoria"], fuente=pregunta["fuente"], año=pregunta["año"])
        preguntas_corpus.append(objeto)
    return preguntas_corpus

                                
# Se define ahora la búsqueda de la pregunta en función de un id

@app.get("/documentos/buscar")

def filtrar_docs_particular(pregunta: str | None = None, respuesta: str | None = None, id: str | None = None, categoria: str | None = None, fuente: str | None = None, año: int | None = None):
    preguntas_corpus=cargar_corpus()
    resultado=[]
    for ejemplo in preguntas_corpus:
       if (
            (pregunta is  None or ejemplo["pregunta"] == pregunta)
            and (respuesta is  None or ejemplo["respuesta"] == respuesta)
            and (id is  None or ejemplo["id"] == id)
            and (categoria is  None or ejemplo["categoria"] == categoria)
            and (fuente is  None or ejemplo["fuente"] == fuente)
            and (año is  None or ejemplo["año"] == año)
         ):
        
         resultado.append(ejemplo)

    return resultado

@app.post("/documentos/buscador")

def filtrar_parecidos(peticion: preguntas_buscadas):
   resultados_parecidos=buscar(peticion.pregunta, peticion.k, peticion.categoria, peticion.nombre_coleccioon )
   presentacion_resultados=[]
   for valor in resultados_parecidos:
      objeto=preguntas_encontradas(id=valor["id"], texto=valor["texto"], similitud=valor["similitud"], categoria=valor["categoria"])
      presentacion_resultados.append(objeto)

   return presentacion_resultados
      
@app.post("/documentos/RAG")

def respuesta_RAG(peticion: generacion_respuesta):
   respuesta_del_RAG,documentos=generar_respuesta(peticion.pregunta, peticion.k, peticion.umbral) # Esto es una tupla (str, list[dict])
   objeto=texto_RAG(texto=respuesta_del_RAG)
   documentos_usados=[]
   for valor in documentos:
      informacion=textos_basados_RAG(id=valor["id"], texto=valor["texto"], similitud=valor["similitud"], categoria=valor["categoria"])
      documentos_usados.append(informacion)
   return objeto, documentos_usados
      
@app.post("/documentos")

def crear_documento(peticion: documento_nuevo):
   corpus_actual=cargar_corpus()
   # Paso 2: contar cuántos documentos ya hay de esa categoría
   numero_mas_alto = -1
   for doc in corpus_actual:
      if doc["categoria"] == peticion.categoria:
         numero_de_ese_id = int(doc["id"].split("_")[-1])
         if numero_de_ese_id > numero_mas_alto:
             numero_mas_alto = numero_de_ese_id

   siguiente_numero = numero_mas_alto + 1
   nuevo_id = f"{peticion.categoria}_{siguiente_numero:03d}"
  

   # Paso 4: construir el diccionario completo del nuevo documento
   nuevo_documento = {
      "id": nuevo_id,
      "pregunta": peticion.pregunta,
      "respuesta": peticion.respuesta,
      "categoria": peticion.categoria,
      "fuente": peticion.fuente,
      "año": peticion.año
   }

     #construir el texto a embeber, con el mismo modo que tu mejor colección
   texto_a_embeber = construir_texto(nuevo_documento, "pregunta_respuesta")

    #  generar su embedding (una llamada, un solo texto dentro de una lista)
   cliente_voyage = voyageai.Client()
   vector = embed_con_cache([texto_a_embeber], cliente_voyage, "voyage-4-lite", "document")[0]

    # : crear/recuperar la colección de Chroma e ingestar este único documento
   cliente_chroma = chromadb.PersistentClient(path="chroma_db")
   coleccion = crear_coleccion(cliente_chroma, "documentos_energia_pregunta_respuesta")
   ingesta(coleccion, [nuevo_documento], {nuevo_id: vector})

    # : actualizar documentos.json en disco
   corpus_actual.append(nuevo_documento)
   with open("data/documentos.json", "w", encoding="utf-8") as f:
      json.dump(corpus_actual, f, ensure_ascii=False, indent=2)

    #  devolver el documento creado
   return documentos_corpus(**nuevo_documento)


@app.delete("/documentos/{id_documento}")
def borrar_documento(id_documento: str):
    # Paso 1: cargar el corpus actual
    corpus = cargar_corpus()

    # Paso 2: comprobar si existe un documento con ese id
    existe = False
    for doc in corpus:
        if doc["id"] == id_documento:
            existe = True

    if not existe:
        raise HTTPException(status_code=404, detail=f"No existe ningún documento con id {id_documento}")

    # Paso 3: borrarlo de Chroma
    cliente_chroma = chromadb.PersistentClient(path="chroma_db")
    coleccion = crear_coleccion(cliente_chroma, "documentos_energia_pregunta_respuesta")
    coleccion.delete(ids=[id_documento])

    # Paso 4: construir un nuevo corpus SIN ese documento, y guardarlo
    nuevo_corpus = []
    for doc in corpus:
        if doc["id"] != id_documento:
            nuevo_corpus.append(doc)

    with open("data/documentos.json", "w", encoding="utf-8") as f:
        json.dump(nuevo_corpus, f, ensure_ascii=False, indent=2)

    # Paso 5: devolver confirmación
    return {"mensaje": f"Documento {id_documento} eliminado correctamente"} 

   
@app.put("/documentos/{id_documento}")
def actualizar_documento(id_documento: str, peticion: documento_actualizado):
    corpus = cargar_corpus()

    # Paso 1: localizar el documento existente
    documento_existente = None
    for doc in corpus:
        if doc["id"] == id_documento:
            documento_existente = doc

    if documento_existente is None:
        raise HTTPException(status_code=404, detail=f"No existe ningún documento con id {id_documento}")

    # Paso 2: guardar pregunta/respuesta originales, para saber si cambian de verdad
    pregunta_original = documento_existente["pregunta"]
    respuesta_original = documento_existente["respuesta"]

    # Paso 3: aplicar solo los campos que el cliente envió (los que no envió quedan igual)
    if peticion.pregunta is not None:
        documento_existente["pregunta"] = peticion.pregunta
    if peticion.respuesta is not None:
        documento_existente["respuesta"] = peticion.respuesta
    if peticion.categoria is not None:
        documento_existente["categoria"] = peticion.categoria
    if peticion.fuente is not None:
        documento_existente["fuente"] = peticion.fuente
    if peticion.año is not None:
        documento_existente["año"] = peticion.año

    # Paso 4: ¿cambió el texto relevante para el embedding?
    texto_cambio = (documento_existente["pregunta"] != pregunta_original) or \
                   (documento_existente["respuesta"] != respuesta_original)

    if texto_cambio:
        texto_a_embeber = construir_texto(documento_existente, "pregunta_respuesta")
        cliente_voyage = voyageai.Client()
        vector = embed_con_cache([texto_a_embeber], cliente_voyage, "voyage-4-lite", "document")[0]

        cliente_chroma = chromadb.PersistentClient(path="chroma_db")
        coleccion = crear_coleccion(cliente_chroma, "documentos_energia_pregunta_respuesta")
        ingesta(coleccion, [documento_existente], {id_documento: vector})
    # Si el texto no cambió, NO llamamos a Voyage ni reingestamos — ahorra una llamada innecesaria

    # Paso 5: guardar el corpus actualizado en disco
    with open("data/documentos.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    return documentos_corpus(**documento_existente)
            
    
        
