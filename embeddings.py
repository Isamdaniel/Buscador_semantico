# Se importa lo necesario:
import voyageai # Para hacer conexión con el cliente
import json # Para cargar los datos que hemos creado en el corpus
import hashlib # Para darle una etiqueta única a cada texto
import os # Para que acceda al sistema y compruebe su existencia
import time 

# En primer lugar, definimos una ruta para el cache. Esto nos sirve para ver si ya existen embeddings generados y no tengamos que volver a solicitarlos por medio de API

RUTA_CACHE= "cache/cache_embeddings.json"
TAMANO_LOTE=15
# Definimos la función que nos va a permitir cargar este mismo cache

def cargar_cache()-> dict:
    if os.path.exists(RUTA_CACHE):
        with open(RUTA_CACHE,"r",encoding="utf-8") as archivo:
            return json.load(archivo) # En caso de que exista el archivo de Caché, lo recuperamos.
    else:
        return {} # Si no existe, devuelve un diccionario vacío

    
# Definimos la función que nos permite guardar el caché 

def guardar_cache(cache:dict) -> None:
    with open(RUTA_CACHE,"w",encoding="utf-8") as archivo:
        json.dump(cache, archivo)  # Esta función no ponemos return porque lo único que queremos es que vaya guardando los datos, no queremos que los devuelva


# Definimos la función que nos permite obtener el hash de cada texto

def clave_texto(texto:str)-> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# Definimos una función que defina el texto exacto que le vamos a mandar a VOYAGE para que realice los embeddings.

def construir_texto(documento: dict, modo: str)->str:
    if modo=="solo_pregunta":
        return documento["pregunta"]
    elif modo=="solo_respuesta":
        return documento["respuesta"]
    elif modo=="pregunta_respuesta":
        return documento["pregunta"]+" "+ documento["respuesta"]
    else:
        raise ValueError("No se conoce este modo")
    

# Definimos la funcón que nos va a generar los embeddings. Estos los vamos a hacer con uso del cache para no realizar llamadas extras en caso de que no sea necesario

def embed_con_cache(textos: list[str], cliente, model, input_type):
    # En primer lugar, cargamos el caché existente
    cache=cargar_cache()
    # Preparo una lista del mismo tamaño que el tamaño de textos de entrada para más adelante ir guardando los vectores
    resultado_final=[None]*len(textos)
    # Preparo una lista de elemntos vacíos para guardar aquellos textos que están pendientes ya que no están en el cache y el índice al que corresponden
    textos_pendientes=[]
    indices_pendientes=[]

    #Ahora se recorren los textos de entrada y el índice que ocupan
    for i, texto in enumerate(textos):
        #Calculamos su huella digital, HASH
        clave=clave_texto(texto)
        if clave in cache:
            resultado_final[i]=cache[clave] # Si esta clave ya existe en el cache, colocamos el vector generado en la posición correspondiente
        else:
            textos_pendientes.append(texto) # Si no existe la añado en la lista de pendientes
            indices_pendientes.append(i) # Añadimos también su índice
    if textos_pendientes:
        for inicio in range(0,len(textos_pendientes), TAMANO_LOTE):
            fin =inicio+TAMANO_LOTE # Definimos un número de textos para no consumir demasiados tokens por llamada
            lote_textos=textos_pendientes[inicio:fin] # Los lotes e indices que vamos a ir usando en cada llamada a la API
            lote_indices=indices_pendientes[inicio:fin]
            respuesta=cliente.embed(lote_textos,model=model, input_type=input_type) # Si la lista de textos pendientes tiene algún elemento todavía, realizamos la llamada a la API para que calcule su vector
            for indice_original, vector in zip(lote_indices, respuesta.embeddings): # Dame cada índice original junto con el embedding que corresponde a ese índice.
                clave=clave_texto(textos[indice_original]) # Calcula de nuevo la huella digital del texto que estaba en esa posición original
                cache[clave]=vector # Guardamos el vector en el diccionario caché con ese HASH
                resultado_final[indice_original]=vector # Guardamos el vector en la posición correspondiente de la lista de resultados
            guardar_cache(cache)
            time.sleep(20) # Número de segundos de diferencia entre una llamada a la API y otra para que no salte error por usar API gratuita
    return resultado_final

def cargar_corpus()-> list[dict]: # Función para cargar todo el corpus del proyecto
    with open("data/documentos.json","r",encoding="utf-8") as f:
        return json.load(f)

def generar_embeddings_corpus(lista_docs, modo, cliente,modelo,input_type):
    # Preparo una lista de documentos vacíos donde voy a ir acumulando los textos a embebber, uno por cada documento, en el mismo orden
    lista_final=[]
    for documento in lista_docs:
        lista_final.append(construir_texto(documento,modo)) # Añado el tipo de documento que quiero a la lista
    lista_vectores=embed_con_cache(lista_final,cliente,modelo,input_type)
    diccionario_vectores={}
    for documento, vector in zip(lista_docs,lista_vectores):
        diccionario_vectores[documento["id"]]=vector

    return diccionario_vectores

if __name__ == "__main__":
    cliente = voyageai.Client()
    corpus = cargar_corpus()
    vectores = generar_embeddings_corpus(corpus, "solo_respuesta", cliente, "voyage-4-lite", "document")
    print("Documentos procesados:", len(vectores))
    # Para ver un vector de ejemplo y confirmar su dimensionalidad:
    primer_id = list(vectores.keys())[0]
    print("Ejemplo de id:", primer_id, "- dimensiones del vector:", len(vectores[primer_id]))

     





