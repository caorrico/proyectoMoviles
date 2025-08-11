# scraper.py
# Este script extrae información de trámites del portal gob.ec.

import requests
from bs4 import BeautifulSoup
import json
import time

# URL base para el listado de trámites
BASE_URL = "https://www.gob.ec"
LIST_URL = f"{BASE_URL}/tramites/lista"

# Nos disfrazamos de un navegador común para evitar ser bloqueados.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_tramite_urls(max_pages=5):
    """
    Navega por el listado de trámites y recopila las URLs individuales.
    
    Args:
        max_pages (int): El número máximo de páginas a procesar. 
                         Usa un número pequeño para pruebas.
    
    Returns:
        list: Una lista de URLs de trámites individuales.
    """
    tramite_urls = []
    print(f"Iniciando recolección de URLs de trámites...")

    for page_num in range(1, max_pages + 1):
        page_url = f"{LIST_URL}?page={page_num}"
        print(f"Procesando página: {page_url}")

        try:
            response = requests.get(page_url, headers=HEADERS, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Selector para los enlaces de la lista de trámites
            links = soup.select('div.listing-boxes-text h3 a')
            
            if not links:
                print("No se encontraron más enlaces en esta página. Terminando recolección.")
                break

            for link in links:
                full_url = BASE_URL + link['href']
                tramite_urls.append(full_url)
            
            print(f"Encontradas {len(links)} URLs en la página {page_num}.")
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Error al acceder a {page_url}: {e}")
            break

    print(f"Recolección finalizada. Total de URLs encontradas: {len(tramite_urls)}")
    return tramite_urls

def scrape_tramite_details(tramite_url):
    """
    Extrae los detalles de una página de trámite individual.

    Args:
        tramite_url (str): La URL de la página del trámite.

    Returns:
        dict: Un diccionario con la información estructurada del trámite.
    """
    print(f"\nExtrayendo detalles de: {tramite_url}")
    try:
        response = requests.get(tramite_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Funciones auxiliares mejoradas ---
        def get_text_safely(selector):
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else "No disponible"
        
        def get_html_content_safely(selector):
            element = soup.select_one(selector)
            return ' '.join(str(element).split()) if element else "No disponible"

        # --- Lógica corregida para "Canales de Atención" ---
        canales_atencion = "No disponible"
        # Buscamos todos los párrafos
        for p in soup.find_all('p'):
            # Buscamos si dentro del párrafo hay una etiqueta <strong>
            strong_tag = p.find('strong')
            if strong_tag and 'Canales de atención:' in strong_tag.get_text():
                # Si la encontramos, limpiamos el texto y lo guardamos
                canales_atencion = p.get_text(strip=True).replace("Canales de atención:", "").strip()
                break

        # --- Extracción con selectores corregidos y lógica mejorada ---
        tramite_data = {
            "Nombre_Tramite": get_text_safely("h1.page-header"),
            "Institucion_Responsable": get_text_safely("div.alert-info").replace("Información proporcionada por:", "").strip(),
            "URL_Fuente": tramite_url,
            "Descripcion": get_text_safely("div#description"),
            "A_Quien_Dirigido": get_text_safely("h3#beneficiary + ul") + " " + get_text_safely("h3#beneficiary + ul + p"),
            "Que_Obtendre": get_text_safely("div.panel-success .panel-body"),
            "Requisitos": get_html_content_safely("h3#requirements ~ div, h3#requirements ~ p, h3#requirements ~ ul"),
            "Como_Hacer_Tramite": get_html_content_safely("div.tab-content"),
            "Costo": get_text_safely("h3#money + p"),
            "Canales_Atencion": canales_atencion,
            "Ubicacion_Horarios": get_html_content_safely("h3#location + p"),
            "Base_Legal": get_html_content_safely("div#panel-legal"),
            "Fecha_Actualizacion": get_text_safely("div.text-right > p").replace("Fecha de última actualización:", "").strip()
        }
        
        return tramite_data

    except requests.exceptions.RequestException as e:
        print(f"Error al extraer detalles de {tramite_url}: {e}")
        return None

if __name__ == "__main__":
    # Para la prueba, solo procesamos la primera página.
    urls = get_tramite_urls(max_pages=1)

    if urls:
        all_tramites = []
        # Para la prueba, solo extraemos los 5 primeros trámites.
        for url in urls[:20]: 
            details = scrape_tramite_details(url)
            if details:
                all_tramites.append(details)
            time.sleep(1) # Pausa entre peticiones

        # Guardamos los resultados en un archivo JSON.
        output_filename = "tramites_extraidos.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_tramites, f, ensure_ascii=False, indent=4)
        
        print(f"\n¡Proceso completado! Se han guardado {len(all_tramites)} trámites en '{output_filename}'.")
