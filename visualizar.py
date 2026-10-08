# Este script se va a utilizar como primera validación visual de que los embeddings generados tienen sentido. Voy a escoger 3 documentos en cada categoría y voy a mapearlos en un mapa de calor.
# En principio, aquellos documentos que pertenecen a la misma categoría deben de salir con colores más intensos mientras que categorías diferentes tienen menos similitud.

# Se importan las librerías necesarias.

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import voyageai

from embeddings import generar_embeddings_corpus, cargar_corpus

# En primer lugar voy a escoger los ids que quiero. Esto lo voy a hacer manualmente para tener un control total.

#Obtengo todos los documentos del corpues
documentos=cargar_corpus()

def claves_a_usar(documentos: list[dict])->list[str]: # Se define esta función de la manera que se ve más abajo para que únicamente escoja los tres primeros índices. Si quiesemos otros tendría que modificarla
    inds_categoria={}
    for documento in documentos: #Por cada valor de la lista (un diccionario) hacemos
        categoria=documento["categoria"]  # Escogemos la categoria 
        idss=documento["id"] # Escogemos su id
        if categoria not in inds_categoria: # Si su categoria no está en el diccionario, lo introducimos como clae con una lista vacia
            inds_categoria[categoria]=[] 
        if len(inds_categoria[categoria]) < 3: # Si el tamaño de la lista es menor a 3, introducimos su id
            inds_categoria[categoria].append(idss)
    # Como quiero una lista plana de solo ids, elimino todas las claves y lo convierto en lista
    # ids_doc=list(inds_categoria.values()) # Este método me da una lista de listas, no una lista plana. Lo dejo porque he caido en el erro y me sirve para tenerlo en cuenta

    #generamos una lista vacia
    indices=[]
    for i in inds_categoria.values():
        indices.extend(i) # "Para cada lista de IDs que haya en el diccionario, añade todos sus elementos a indices.

    return indices

def obtener_vectores(indices_escogidos: list[str],diccionario_vect: dict)-> list[list[float]]:
    lista_vectores=[] # Lista donde vamos a guardar los vectores
    for ide in indices_escogidos: #Por cada id de los que queremos ver
        vector=diccionario_vect[ide] # Vamos coger el vector que queremos asociado al id
        lista_vectores.append(vector) # Lo añadimos a la lista 
    return lista_vectores

#Definimos la función que realiza la simiilitud del coseno de dos vectores gracias a la definición del prodcuto escalar
def similitud_coseno(vector1, vector2)-> float: 
    return np.dot(vector1,vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))

def matriz_similitudes(lista_vectores):
    dimensiones=len(lista_vectores)
    n=np.zeros((dimensiones,dimensiones)) # Matriz de 0 del mismo tamaño que la longitud de los vectores
    for i in range(len(lista_vectores)):
        for j in range(len(lista_vectores)):
            n[i][j]=similitud_coseno(lista_vectores[i],lista_vectores[j])
    return n

# Con todo esto, ya podemos dibujar la figura.

#Ejecutamos todo y después dibujamos.

indices_a_usar=claves_a_usar(documentos)
#Tenemos que obtener el diccionario de vectores, para eso llamamos a la función que tenemos definida en embeddings.py 
cliente = voyageai.Client()
corpus = cargar_corpus()
diccionario_vect=generar_embeddings_corpus(documentos, "solo_respuesta",cliente, "voyage-4-lite", "document")
lista_vectores=obtener_vectores(indices_a_usar,diccionario_vect)

matriz_a_mapear=matriz_similitudes(lista_vectores)

plt.figure(figsize=(12,10))
plt.title("Mapa de calor de los embeddings de los 3 primeros id por categoria")
sns.heatmap(data=matriz_a_mapear,annot=True,xticklabels=indices_a_usar,yticklabels=indices_a_usar)
plt.xlabel("Ids")
plt.ylabel("Embeddings")
plt.savefig("assets/mapa_calor.png")
plt.show()


