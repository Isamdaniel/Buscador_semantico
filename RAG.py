# En este script se crean las funciones necesarias y se ejecutrán para ya con todo montado, poder hacer uso de RAG

import chromadb
import json
from embeddings import embed_con_cache
from almacen import ingesta, crear_coleccion
from buscador import buscar
import voyageai
import anthropic

# Creamos la función que nos de la respuesta a la pregunta citando que documentos usó extrayendo las mejores k respuestas
MENSAJE_SIN_INFO="No tengo información suficiente para responder a esta pregunta con los documentos disponibles"

def generar_respuesta(pregunta:str, k:int,umbral:float)-> tuple[str, list[dict]]:
    # En primer lugar, creamos los clientes que vamos a utilizar
    resultados=buscar(pregunta,k,None,nombre_coleccioon="documentos_energia_pregunta_respuesta") # Con esto ya tengo los textos más relevantes
    if resultados==[] or resultados[0]["similitud"]<umbral: # Escogemos el primer término como umbral porque va a ser el que mayor similitud de los k documentos escogidos

        return MENSAJE_SIN_INFO, resultados
    else:
        # Ahora voy a crear un string que sea la concatenación de todos los ids más texto para pasarselo al mensaje
        contexto=""
        for clave in resultados:
            contexto = contexto + f"[DOCUMENTO id: {clave['id']}]\n{clave['texto']}\n\n"
            # Estos textos ahora hay que pasarselos junto con la pregunta para que anthropic genere una respuesta

        mensaje_usuario=f"""Contexto:
        ---
        {contexto}
        ---
        Pregunta: {pregunta}"""

        cliente=anthropic.Anthropic()

        mensaje=cliente.messages.create(
            model="claude-haiku-4-5", #Se utiliza un método más potente para que de mejores respuestas
            max_tokens=10000,
            system= 'Eres un asistente que responde preguntas sobre el sector energético, basándote EXCLUSIVAMENTE en el contexto proporcionado a continuación. No uses conocimiento propio que no esté en el contexto.'
                'Si el contexto no es suficiente, responde: No tengo información suficiente'
                'Al final de tu respuesta indica qué documentos usaste, citando sus ids entre corchetes, por ejemplo: [solar_001, almacenamiento_003]',
            messages=[{
                "role":"user" ,"content":mensaje_usuario
                }]

            )

        for block in mensaje.content:
            if block.type=="text":
                respuesta=block.text
        return respuesta, resultados

if __name__=="__main__":
    respuesta,resultados=generar_respuesta("En que se basan las energías limpias?",3,0.3)
    print(respuesta,resultados)