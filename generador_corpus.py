#Este script se va a utilizar para generar el corpus de documentos que voy a utilizar en el proyecto:buscador_semantico
import anthropic
import json
# Creamos conexión con el cliente:

def documentos(categorias:list[str]) ->  tuple[list[dict], list[dict]] : 
    cliente=anthropic.Anthropic() # La API key se introduce en la terminal 
    lista_dic=[]
    lista_errores=[]
    for categoria in categorias:
        message=cliente.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10000,
            system='Utiliza vocabulario tecnológico y preciso. '
            'Respuestas de entre 100 y 150 palabras. '
            'Genera 8-9 documentos distintos sobre el sector energético. '
            'Responde ÚNICAMENTE con una lista JSON válida, sin texto adicional, con este formato exacto: '
            '[{"pregunta": "...", "respuesta": "..."}, {"pregunta": "...", "respuesta": "..."}]',

            messages=[
                 {"role":"user",
                 "content": f"Genera un documento sobre {categoria}"  }
            ]
            )
        
        for block in message.content:
                if block.type=="text":
                     # Ahora tocamos el formato de la respuesta JSON para poder usar loads.
                     #Estas respuestas vienen dadas por ````json al inicio, ``` al final
                    if (block.text.startswith("```json")) or( block.text.endswith("```")):
                         respuesta_limpia=block.text.replace("```json","").replace("```","").strip()
                    else:
                         respuesta_limpia=block.text
                      #Esta respuesta limpia es una lista de 8 o 9 diccionarios con los valores pregunta: respuesta.
                    
                    try :
                         docs_categoria=json.loads(respuesta_limpia)
                         for indice,documento in enumerate(docs_categoria):
                              id_final=f"{categoria}_{indice:03d}"
                              documento_completo=documento|{"id":id_final,"categoria":categoria,"fuente":"generado_LLM_revisado", "año":2026}
                              lista_dic.append(documento_completo)
                              
                    except json.JSONDecodeError:
                       errores={"categoria":categoria, "respuesta_cruda":respuesta_limpia}
                       lista_errores.append(errores)

    return lista_dic, lista_errores

corpus,errores=documentos(["solar"])

with open("data/documentos.json", "w", encoding="utf-8") as el_archivo:
        json.dump(corpus, el_archivo, ensure_ascii=False, indent=2)

if errores:
    with open("data/errores_generacion.json", "w", encoding="utf-8") as el_archivo:
        json.dump(errores, el_archivo, ensure_ascii=False, indent=2)

                

