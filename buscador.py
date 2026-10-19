# Importamos las librerias necesarias
import chromadb
import voyageai
from embeddings import embed_con_cache
from almacen import ingesta, crear_coleccion

# Vamos a crear la función buscar Para que cuando le pasemos una pregunta nos dice los k resultados más parecidos
# Vamos a crear una función que reciba un texto, k respuestas que nos de y la categoria para que filtre

def buscar(pregunta:str, k:int, categoria:str,nombre_coleccioon: str="documentos_energia") -> list[dict] :
    #En primer lugar esta pregunta la debe de convertir en vector usando la función de generador de embedding con cache
    vector=embed_con_cache([pregunta],cliente=voyageai.Client(),model="voyage-4-lite",input_type="query")[0] #Utilizamos esta función porque no tiene porque ser una pregunta del corpus, puede ser cualquier otra. Además pasamos [pregunta], porque debe de ser una lista de preguntas según hemos definido la función
    # Este vector que se genera, nos va a servir para psarselo a chroma y que nos de una búsqueda semántica en función de los k más parecidos que queremos
    cliente_chroma = chromadb.PersistentClient(path="chroma_db")
    coleccion=crear_coleccion(cliente_chroma,nombre_coleccioon)
    resultado_def=[] # Creamos una lista definitiva donde vamos a acumular los distitnos dics
    # Hacemos esta distinción por si no queremos hacer una distinción por categoría 
    if categoria != None:
        resultados_chroma=coleccion.query(
        query_embeddings=[vector], #Le pasamos el vector ya generado con voyageai. no tendría sentido pasarle pregunta porque entonces lo embeddiria chroma y no haríamos nada 
        n_results=k,
        where={"categoria":categoria}
         )
        
        for id_doc,documents,distances,metadatas in zip(resultados_chroma["ids"][0],resultados_chroma["documents"][0],resultados_chroma["distances"][0],resultados_chroma["metadatas"][0]): # Como resultado_chroma es una lista de listas, tenemos que acceder al primer elemento

            resultados={"id":id_doc,"texto":documents,"similitud":1-distances, "categoria":metadatas["categoria"]} # Ponemos 1-distances ya que con la métrica coseno chroma devueelve la distancia (más bajo=máscerca) pero yo quiero similitud (más alto=más parecido)
            resultado_def.append(resultados)

    else:
        resultados_chroma=coleccion.query(
                query_embeddings=[vector], #Le pasamos el vector ya generado con voyageai. no tendría sentido pasarle pregunta porque entonces lo embeddiria chroma y no haríamos nada 
                n_results=k,
        )
        for id_doc,documents,distances,metadatas in zip(resultados_chroma["ids"][0],resultados_chroma["documents"][0],resultados_chroma["distances"][0],resultados_chroma["metadatas"][0]):
            resultados={"id":id_doc,"texto":documents,"similitud":1-distances,"categoria":metadatas["categoria"]}
            resultado_def.append(resultados)

    return resultado_def
    

if __name__ == "__main__":
    resultados = buscar("¿cómo funcionan los paneles solares?", 3, "petroleo_gas","documentos_energia")
    for r in resultados:
        print(r["id"], round(r["similitud"], 3), r["categoria"])
        print(r, type(r))
        

