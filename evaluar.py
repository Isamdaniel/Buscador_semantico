# Este script me va a servir para evaluar el funcionamiento de mi buscador semántico y el buscador por palabras clave
# Importamos las funciones que necsitamos para este script
import json
from baseline import buscador_keywords
from buscador import buscar
# Se cargan las preguntas de prueba

with open("data/preguntas_prueba.json","r",encoding="utf-8") as f:
    preguntas=json.load(f)
# Creo una lista de evaluación de los distintos textos


# Definimos la función que nos va a dar la posición del acierto:

def posicion_acierto(id_encontrados,id_esperado):
    for indice, indice_actual in enumerate(id_encontrados,start=1):
        if indice_actual==id_esperado:
            return indice
    return None # No se encontro posición 

# Se construye ahora la función Recall@k que nos responderá a la pregunta: ¿el documento esperado apareció entre los primeros k resultados?

def recall(ids_encontrados,id_esperado, k):
    posicion=posicion_acierto(ids_encontrados,id_esperado)
    if posicion != None and posicion <=k:
        return 1
    else:
        return 0
    
def mrr(ids_encontrados,id_esperado,k): # Esta función nos devuelve cuán pronto se ha encontrado la respuesta
    pos=posicion_acierto(ids_encontrados,id_esperado)
    if pos is not None and pos <=k:
        return 1/pos
    else:
        return 0


def evaluar(preguntas,nombre_coleccioon,k):
    # Creo una lista de evaluación de los distintos textos
    lista_ev=[]


    for item in preguntas:
        resultado_clave=buscador_keywords(item["pregunta"],k,None)
        resultado_semantico=buscar(item["pregunta"],k,None,nombre_coleccioon)

        #Ahora cogemos cada id de la busqueda de resultado clave
        id_clave=[]
        for keys in resultado_clave:
            id_clave.append(keys["id"])
        id_semantico=[]
        for keys in resultado_semantico:
            id_semantico.append(keys["id"])
        entrada={
            "pregunta":item["pregunta"],
            "id_esperado":item["id_esperado"],
            "tipo":item["tipo"],
            "id_clave":id_clave,
            "id_semantico":id_semantico,
         }

        lista_ev.append(entrada)
    for valor in lista_ev:
    #Calculamos recall
        valor["recall@1_clave"]=recall(valor["id_clave"],valor["id_esperado"],1)
        valor["recall@1_semantico"]=recall(valor["id_semantico"],valor["id_esperado"],1)
        valor["recall@3_clave"]=recall(valor["id_clave"],valor["id_esperado"],3)
        valor["recall@3_semantico"]=recall(valor["id_semantico"],valor["id_esperado"],3)

        # Calculamos MRR@K
        valor["mrr@k_clave"]=mrr(valor["id_clave"],valor["id_esperado"],3)
        valor["mrr@k_semantico"]=mrr(valor["id_semantico"],valor["id_esperado"],3)

        # Ahora vamos a calcular el promedio final sobre todo el conjunto de preguntas
        #Inicializamos 2 variables donde vamos a guardar la suma:
    suma_re1_clave=0
    suma_re1_semantico=0
    suma_re3_clave=0
    suma_re3_semantico=0
    suma_mrr_clave=0
    suma_mrr_semantico=0

    for valores in lista_ev: #Volvemos a recorrer toda la lista 
        suma_re1_clave+=valores["recall@1_clave"]
        suma_re1_semantico+=valores["recall@1_semantico"]
        suma_re3_clave+=valores["recall@3_clave"]
        suma_re3_semantico+=valores["recall@3_semantico"]
        suma_mrr_clave+=valores["mrr@k_clave"]
        suma_mrr_semantico+=valores["mrr@k_semantico"]

    recalk_clave1_prom=suma_re1_clave/len(lista_ev)
    recalk_semantico1_prom=suma_re1_semantico/len(lista_ev)
    recallk_clave3_prom=suma_re3_clave/len(lista_ev)
    recallk_semantico3_prom=suma_re3_semantico/len(lista_ev)
    mrr_clave_prom=suma_mrr_clave/len(lista_ev)
    mrr_semantico_prom=suma_mrr_semantico/len(lista_ev)


    #Ahora quiero calcular estas mismas métricas haciendo una diferenciación por el tipo de pregunta que se realice fácil/difícil
    sumas = {
        "global": {"re1_clave": 0, "re1_semantico": 0, "re3_clave": 0, "re3_semantico": 0, "mrr_clave": 0, "mrr_semantico": 0},
        "facil": {"re1_clave": 0, "re1_semantico": 0, "re3_clave": 0, "re3_semantico": 0, "mrr_clave": 0, "mrr_semantico": 0},
        "dificil": {"re1_clave": 0, "re1_semantico": 0, "re3_clave": 0, "re3_semantico": 0, "mrr_clave": 0, "mrr_semantico": 0},
    }
    contadores = {"global": 0, "facil": 0, "dificil": 0}
    for terminos in lista_ev:
        sumas["global"]["re1_clave"] += terminos["recall@1_clave"]
        sumas[terminos["tipo"]]["re1_clave"] += terminos["recall@1_clave"]
        sumas["global"]["re1_semantico"] += terminos["recall@1_semantico"]
        sumas[terminos["tipo"]]["re1_semantico"] += terminos["recall@1_semantico"]
        sumas["global"]["re3_semantico"] += terminos["recall@3_semantico"]
        sumas[terminos["tipo"]]["re3_semantico"] += terminos["recall@3_semantico"]
        sumas["global"]["re3_clave"] += terminos["recall@3_clave"]
        sumas[terminos["tipo"]]["re3_clave"] += terminos["recall@3_clave"]
        contadores["global"]+=1
        contadores[terminos["tipo"]]+=1
        sumas["global"]["mrr_clave"] += terminos["mrr@k_clave"]
        sumas[terminos["tipo"]]["mrr_clave"] += terminos["mrr@k_clave"]
        sumas["global"]["mrr_semantico"] += terminos["mrr@k_semantico"]
        sumas[terminos["tipo"]]["mrr_semantico"] += terminos["mrr@k_semantico"]

    #Una vez que tenemos todo diferenciado por categoria de dificultad de pregunta calculamos el promedio

    

    promedios= {
        "global": {"re1_clave": 0, "re1_semantico": 0, "re3_clave": 0, "re3_semantico": 0, "mrr_clave": 0, "mrr_semantico": 0},
        "facil": {"re1_clave": 0, "re1_semantico": 0, "re3_clave": 0, "re3_semantico": 0, "mrr_clave": 0, "mrr_semantico": 0},
        "dificil": {"re1_clave": 0, "re1_semantico": 0, "re3_clave": 0, "re3_semantico": 0, "mrr_clave": 0, "mrr_semantico": 0},
    }

    for grupo in sumas: # Accedemos a cada clave del diccionario sumas
        for metrica in sumas[grupo]: # Accedemos a a cada valor dentro de la key grupo
            promedios[grupo][metrica]=sumas[grupo][metrica]/contadores[grupo]

    return lista_ev, promedios

if __name__=="__main__":
    lista_ev, promedios = evaluar(preguntas, "documentos_energia", 3)
    
    resultado_final = {"detalle": lista_ev, "promedios": promedios}
    with open("data/resultados_evaluacion.json", "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=2)
    print(lista_ev,promedios)






        




