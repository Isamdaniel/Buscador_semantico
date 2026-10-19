# En este script se va a crear una función capaz de discernir realizando otra llamada a la API de Anthropic si la respuesta generada es fidedigna a los documentos o no.
# En primer lugar se realizan las importaciones necesarias
from RAG import generar_respuesta, MENSAJE_SIN_INFO
import anthropic


# Generamos la función que va a hacer de "juez" sobre la respuesta. 

def juez(pregunta:str,respuesta: str, documentos_fuente: list[dict],cliente) -> str:
    contexto=""
    for valores in documentos_fuente:
        contexto=contexto + f"[DOCUMENTO id:{valores['id']}]\n{valores['texto']}\n\n"
    # Se añade combinan la pregunta y respuesta:
    texto= f"""Pregunta: {pregunta}
    Documentos fuente:{contexto}
    Respuesta: {respuesta}
    """
    prompt=('Aquí tienes una pregunta, los documentos fuente y la respuesta generada. '
    'Juzga si la respuesta está fundamentada en los documentos, o si inventa/contradice algo. '
    'Responde ÚNICAMENTE CON UNA PALABRA  de la siguiente manera: fundamentada, parcialmente_fundamentada, no_fundamentada. '
    'No escribas ninguna frase,ni justificación, ni encabezados. Solo la palabra y EXCLUSIVAMENTE la palabra')
    mensaje=cliente.messages.create(
        model="claude-haiku-4-5",
        max_tokens=50, # He probado varios prompts y sigue devolviendome más de lo que debe. Por ello reduzco el número de tokens para forzar la salida que quiero
        system=prompt,
        messages= [{"role":"user", "content":texto}]

    )
    for bloque in mensaje.content:
        if bloque.type=="text":
            respuesta_juzgada=bloque.text
    return respuesta_juzgada

def evaluacion_rag(preguntas_dominio: dict,preguntas_sin_dominio:dict,k:int,umbral:float,cliente)-> list[dict]:
    # Creamos una lista donde vamos a guardar los resultados:
    lista_resultados=[]
    for item in preguntas_dominio:
        respuesta, resultados=generar_respuesta(item["pregunta"],k,umbral)
        if respuesta==MENSAJE_SIN_INFO:
            veredicto="fundamentada"
        else:
            veredicto=juez(item["pregunta"],respuesta,resultados,cliente)

        diccionario={"pregunta":item["pregunta"], "respuesta":respuesta, "veredicto":veredicto, "origen":"preguntas_dominio"}
        lista_resultados.append(diccionario)
    for valor in preguntas_sin_dominio:
        respuesta,resultados=generar_respuesta(valor["pregunta"],k,umbral)
        if respuesta==MENSAJE_SIN_INFO:
            veredicto="fundamentada"
        else:
            veredicto=juez(valor["pregunta"],respuesta,resultados,cliente)

        diccionario={"pregunta":valor["pregunta"], "respuesta":respuesta, "veredicto":veredicto, "origen":"preguntas_sin_dominio"}
        lista_resultados.append(diccionario)

    return lista_resultados

def resumen_rag(lista_resultados: list[dict])-> dict:
    origen={"preguntas_dominio":{"fundamentada":0,"parcialmente_fundamentada":0, "no_fundamentada":0},
            "preguntas_sin_dominio":{"fundamentada":0,"parcialmente_fundamentada":0, "no_fundamentada":0}
            }
    for resultado in lista_resultados:
        tipo=resultado["origen"]
        veredicto=resultado["veredicto"]
        origen[tipo][veredicto]+=1
    return origen

    
    


if __name__ == "__main__":
    import json
    
    with open("data/preguntas_prueba.json", "r", encoding="utf-8") as f:
        preguntas_dominio = json.load(f)
    with open("data/preguntas_fuera_dominio.json", "r", encoding="utf-8") as f:
        preguntas_sin_dominio = json.load(f)
    
    cliente = anthropic.Anthropic()
    resultados = evaluacion_rag(preguntas_dominio, preguntas_sin_dominio, 3, 0.3, cliente)
    resumen=resumen_rag(resultados)
    guardar_datos={"detalle":resultados,"resumen":resumen}
    with open("data/resultados_evalucion_rag.json","w",encoding="utf-8") as archivo:
        json.dump(guardar_datos,archivo,ensure_ascii=False, indent=2)
    print(resumen)