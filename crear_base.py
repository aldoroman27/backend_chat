import chromadb
import requests
from bs4 import BeautifulSoup
import os 


client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="empresa_knowledge")

def web_scraping(url):
    print("Analizando Web...")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        textos = []
        for tag in soup.find_all(['p','h1','h2', 'h3', 'li']):
            texto_limpio = tag.get_text().strip()
            if len(texto_limpio) > 20: #Ignoramos textos muy cortos
                textos.append(texto_limpio)
        return textos
    except Exception as e:
        print(f"Error durante el proceso: {e}")
        return []
    
urls = [
    "https://midogroup.mx/",
    "https://midogroup.mx/quienes-somos/",
    "https://midogroup.mx/servicios/",
    "https://midogroup.mx/contacto/"
]

print("Iniciando la vectorizacíon....")
id_contador = 0

for url in urls:
    contenido = web_scraping(url)
    if contenido:
        ids = [f"id_{id_contador + i}" for i in range(len(contenido))]
        metadatas = [{"source":url} for _ in range(len(contenido))]

        collection.add(
            documents=contenido,
            metadatas=metadatas,
            ids=ids
        )
        id_contador += len(contenido)
        print(f"Guardados {len(contenido)} fragmentos de {url}")

print(f"LISTO, base de datos vectorial creada correctamente con {collection.count()} documentos")