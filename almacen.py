import chromadb
import voyageai


from embeddings import cargar_corpus, generar_embeddings_corpus
def crear_coleccion(cliente,nombre_documentos: str):
    documentos_energia=cliente.get_or_create_collection(name=nombre_documentos,metadata={"hnsw:space":"cosine"}) # Esta línea crea (o recupera) la colección dentro de la base de datos de chroma
    return documentos_energia

def ingesta(coleccion,documentos,diccionario):
    # Preparamos 4 listas vacías que es lo que espera más adelante nuestra función upsert
    lista_ids=[]
    lista_textos=[]
    lista_embeddings=[]
    lista_metadatos=[]
    # Para obtener los distintos valores, realizo un bucle que recorra y vaya añadiendo cada valor por iteración
    for documento in documentos:
        lista_ids.append(documento["id"]) # Obtiene el id del texto
        lista_textos.append(documento["respuesta"]) #Obtiene la respuesta generada por el LLM
        lista_embeddings.append(diccionario[documento["id"]]) # Obtiene el vector en función de su id
        lista_metadatos.append({"categoria":documento["categoria"],"fuente":documento["fuente"],"año":documento["año"]}) # Incluye el resto de metadata, categoria,metadata, fuente y anio

    # Una vez que están todas las listas generadas llamamos una sola vez para actualizar los valores de la colección
    coleccion.upsert(
        ids=lista_ids,
        documents=lista_textos,
        embeddings=lista_embeddings,
        metadatas=lista_metadatos
    )
     
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

