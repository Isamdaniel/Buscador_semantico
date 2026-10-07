import json
with open("cache_embeddings.json","r",encoding="utf-8") as f:
    cache=json.load(f)
print(len(cache))