# Este script sirve para crear unas pocas preguntas que estén fuera del dominio de los documentos que ya tenemos.
import json

preguntas=[
    {"id":"fd001","pregunta":"¿Cuánto tiempo hay que cocer un huevo para que quede duro?","tema":"cocina"},
    {"id":"fd002","pregunta":"¿Cuántos jugadores tiene un equipo de fútbol en el campo?","tema":"deporte"},
    {"id":"fd003","pregunta":"¿En qué año terminó la Segunda Guerra Mundial?","tema":"historia"},
    {"id":"fd004","pregunta": "¿Es Rusia el país más grande del mundo?","tema":"geografía"},
    {"id":"fd005","pregunta":"¿Cuáles son los síntomas del resfriado común?","tema":"medicina"},
    {"id":"fd006","pregunta":"¿Cómo se riega un cactus en verano?","tema":"jardinería"},
    {"id":"fd007","pregunta":"¿Qué diferencia hay entre un virus y una bacteria?","tema":"biología"},
    {"id":"fd008","pregunta":"¿El electrón es un leptón?","tema":"física"}
    ]

# Una vez que tenemos las preguntas generadas vamos a guardarlas como un archivo json
with open("data/preguntas_fuera_dominio.json","w",encoding="utf-8") as archivo:
    json.dump(preguntas,archivo,ensure_ascii=False, indent=2)