# En este script se crea un buscador por palabras clave en lugar de manera semántica
import json

def buscador_keywords(pregunta: str , k:int,categoria:str|None=None)-> list[dict]:
    with open("data/documentos.json","r",encoding="utf-8") as f:
            documentos=json.load(f)
    palabras=pregunta.lower().split() # Convertimos en una lista de str las palabras de la pregunta
    resultados=[]

    for documento in documentos : # Recorremos cada diccionario dentro de la lista. Por tanto, documento es un diccionario

        if categoria==documento["categoria"] or categoria is None:
            contador=0
            palabras_respuesta=documento["respuesta"].lower().split()

            for palabra in palabras:
                if palabra in palabras_respuesta:
                    contador+=1

            resultado={"similitud":contador, "texto":documento["respuesta"],"categoria":documento["categoria"], "id":documento["id"] }

            resultados.append(resultado)

    resultados_ordenados=sorted(resultados,key= lambda resultado:resultado["similitud"],reverse=True)

    resultados_finales = resultados_ordenados[:k]
  
         
         
    return resultados_finales

if __name__=="__main__":
    resultado=buscador_keywords("¿El gas influye en la electricidad?",3,None)
    print(resultado)
    


    
           


            

            


   