import chromadb
# chromadb es la librería que nos da acceso a la base de datos vectorial.
# La usamos para crear un cliente persistente, crear/recuperar colecciones,
# y para las operaciones de insertar (upsert) y consultar (query) vectores.
import voyageai
# Cliente de la API de Voyage, con la que generamos los embeddings (vectores)
# a partir de texto en español. Lo necesitamos aquí porque, antes de poder
# ingestar nada en Chroma, tenemos que convertir el corpus en vectores.

from embeddings import cargar_corpus, generar_embeddings_corpus
def crear_coleccion(cliente,nombre_documentos: str):
     # Una "colección" en Chroma es el equivalente a una tabla: un conjunto organizado de vectores, sus textos asociados y sus metadatos.
    # Usamos get_or_create_collection en vez de create_collection a secas porque create_collection lanza un error si la colección ya existe
    # (por ejemplo, si volvemos a ejecutar este script una segunda vez). get_or_create_collection la crea si no existe, o la recupera tal cual si ya estaba creada de antes — así el script es seguro de repetir.
    
    # metadata={"hnsw:space": "cosine"} configura la métrica de distancia
    # que Chroma va a usar internamente para comparar vectores. Por defecto
    # Chroma no usa coseno, así que lo forzamos explícitamente, tal como
    # pide el enunciado del proyecto (comparar por "ángulo" entre vectores, no por distancia euclídea

    documentos_energia=cliente.get_or_create_collection(name=nombre_documentos,metadata={"hnsw:space":"cosine"}) # Esta línea crea (o recupera) la colección dentro de la base de datos de chroma
    return documentos_energia

def ingesta(coleccion,documentos,diccionario):
     # Esta función "rellena" la colección vacía (o la actualiza) con el contenido real de nuestro corpus: cada documento necesita un id, un texto legible, su vector ya calculado, y sus metadatos.
    # Chroma espera estos cuatro elementos como LISTAS PARALELAS (misma posición = mismo documento), no documento a documento, así que primero construimos las cuatro listas completas y luego hacemos  una única llamada a upsert con todas juntas.
    # Preparamos 4 listas vacías que es lo que espera más adelante nuestra función upsert

    lista_ids=[]
    lista_textos=[]
    lista_embeddings=[]
    lista_metadatos=[]
    # Para obtener los distintos valores, realizo un bucle que recorra y vaya añadiendo cada valor por iteración
    for documento in documentos:
        # El id es el identificador único que nosotros mismos asignamos al generar el corpus (ej. "solar_003"). Chroma lo usa para saber si un documento es nuevo (insert) o ya existe (update).
        lista_ids.append(documento["id"]) 

        # Guardamos la RESPUESTA como texto asociado al vector, porque es el contenido que queremos que el buscador devuelva como resultado útil para quien pregunte (la pregunta es solo el "gancho" de entrada, no lo que queremos recuperar)
        lista_textos.append(documento["respuesta"]) 

        # El vector de este documento no lo calculamos aquí: ya viene calculado de antemano (con caché) en el diccionario id->vector que generamos con generar_embeddings_corpus. Solo lo buscamos por su id.
        lista_embeddings.append(diccionario[documento["id"]]) 

          # Los metadatos son la información adicional que Chroma puede usar luego para FILTRAR búsquedas (por ejemplo, "solo categoría solar"), sin tener que calcular similitud con el texto en sí.
        lista_metadatos.append({"categoria":documento["categoria"],"fuente":documento["fuente"],"año":documento["año"]}) # Incluye el resto de metadata, categoria,metadata, fuente y anio

    # Una vez que están todas las listas generadas llamamos una sola vez para actualizar los valores de la colección
    coleccion.upsert(
        ids=lista_ids,
        documents=lista_textos,
        embeddings=lista_embeddings,
        metadatas=lista_metadatos
    )
        # upsert = "update" + "insert": si el id ya existe en la colección,actualiza esa entrada; si no existe, la crea. 
if __name__=="__main__":
    cliente1=voyageai.Client()
    corpus=cargar_corpus()
    vectores=generar_embeddings_corpus(corpus,"solo_respuesta",cliente1,"voyage-4-lite","document")
    cliente=chromadb.PersistentClient(path="chroma_db") #Creamos una instancia persistente de Chroma que guarda en disco, y path es el directorio donde se van a guardar los datos
    coleccion=crear_coleccion(cliente,"documentos_energia") # Ponemos ese nombre porque se espera un string dentro de .get_or_create_collection

    # Llamamos a la ingesta para actualice nuestra coleccion
    ingesta(coleccion,corpus,vectores)

    # Comprobamos con count si efectivamente tenemos 72 valores
    print(coleccion.count())

