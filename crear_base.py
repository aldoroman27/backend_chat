import chromadb
import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURACIÓN ---
client = chromadb.PersistentClient(path="chroma_db")
# Borramos y creamos de nuevo la colección para empezar limpio
try:
    client.delete_collection(name="empresa_knowledge")
except:
    pass 
collection = client.get_or_create_collection(name="empresa_knowledge")


urls = [
    "https://midogroup.mx/",
    "https://midogroup.mx/quienes-somos/",
    "https://midogroup.mx/servicios/",
    "https://midogroup.mx/contacto/"
]
# --- FUNCIÓN DE SCRAPING ROBUSTA ---
def scrapear_web(url):
    print(f"------------------------------------------------")
    print(f"Intentando leer: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}") # 200 es OK, 403 es prohibido
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Eliminar scripts y estilos (La basura invisible)
        for script in soup(["script", "style", "meta", "noscript", "header", "footer"]):
            script.decompose()

        # 2. Estrategia "Fuerza Bruta" (Agarra todo el texto del body)
        # get_text con separador ayuda a que no se peguen las palabras
        texto_sucio = soup.get_text(separator='\n')
        
        # 3. Limpieza línea por línea
        lineas_limpias = []
        for linea in texto_sucio.splitlines():
            texto = linea.strip()
            # Guardamos si tiene más de 15 letras (bajé el filtro para que agarre más cosas)
            if len(texto) > 15:
                lineas_limpias.append(texto)
        
        print(f"Se encontraron {len(lineas_limpias)} fragmentos de texto útiles.")
        return lineas_limpias

    except Exception as e:
        print(f"Error leyendo la web: {e}")
        return []

# --- PROCESO PRINCIPAL ---
print("Iniciando extracción de datos...")

count = 0
for url in urls:
    contenido = scrapear_web(url)
    
    if contenido:
        # Generamos IDs únicos simples
        ids = [f"{url}_frag_{i}" for i in range(len(contenido))]
        metadatas = [{"source": url} for _ in range(len(contenido))]
        
        collection.add(
            documents=contenido,
            metadatas=metadatas,
            ids=ids
        )
        count += len(contenido)
    else:
        print("No se pudo sacar nada de esta URL (o estaba vacía).")

print(f"\nTERMINADO: Se guardaron {count} fragmentos en la base de datos.")
