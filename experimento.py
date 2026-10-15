import json
from embeddings import cargar_corpus, generar_embeddings_corpus
from almacen import crear_coleccion, ingesta
from evaluar import evaluar
import chromadb
import voyageai

if __name__=="__main__":
    #Se carga el corpus
    documentos=cargar_corpus()
    with open("data/preguntas_prueba.json", "r", encoding="utf-8") as f:
        preguntas = json.load(f)
    # Se crean los dos clientes de voyageai y chormadb
    cliente_emb=voyageai.Client()
    cliente_cb=chromadb.PersistentClient(path="chroma_db")
    # Realizamos el experimento para solo pregunta
    embeddings=generar_embeddings_corpus(documentos, "solo_pregunta", cliente_emb, "voyage-4-lite", "document")
    creacion=crear_coleccion(cliente_cb,"documentos_energia_solo_pregunta")
    ingesta1=ingesta(creacion,documentos,embeddings)
    lista_solo_pregunta,resultados_solo_pregunta=evaluar(preguntas,"documentos_energia_solo_pregunta",3)

    diccionario_solo_pregunta={
        "informacion":lista_solo_pregunta,
        "promedios_solo_pregunta":resultados_solo_pregunta
    }
    with open("data/resultados_solo_pregunta.json","w",encoding="utf-8") as archivo:
        json.dump(diccionario_solo_pregunta,archivo, ensure_ascii=False, indent=2)



    # Realizamos el experimento con pregunta + respuesta
    embeddings2=generar_embeddings_corpus(documentos, "pregunta_respuesta", cliente_emb, "voyage-4-lite", "document")
    creacion2=crear_coleccion(cliente_cb,"documentos_energia_pregunta_respuesta")
    ingesta2=ingesta(creacion2,documentos,embeddings2)
    lista_pregunta_respuesta, resultados_pregunta_respuesta=evaluar(preguntas,"documentos_energia_pregunta_respuesta",3)

    diccionario_pregunta_respuesta={
        "informacion":lista_pregunta_respuesta, 
        "promedios_pregunta_respuesta":resultados_pregunta_respuesta
}

    with open("data/resultados_pregunta_respuesta.json","w",encoding="utf-8") as archivo2:
        json.dump(diccionario_pregunta_respuesta,archivo2,ensure_ascii=False,indent=2)

    





    