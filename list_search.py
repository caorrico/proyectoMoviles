# scraper.py
# Versión definitiva basada en el análisis técnico.
# Implementa una estrategia híbrida: rastreo completo + búsqueda por palabras clave.

import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote

# --- 1. Configuración Global ---
BASE_URL = "https://www.gob.ec"
LIST_URL_TEMPLATE = f"{BASE_URL}/tramites/lista?page={{page}}"
SEARCH_URL_TEMPLATE = f"{BASE_URL}/tramites/buscar?search_api_fulltext={{keyword}}&page={{page}}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Palabras clave para asegurar la cobertura de trámites no listados
SEARCH_KEYWORDS = [
    "cédula", "pasaporte", "licencia", "matrícula", "impuesto", "registro",
    "certificado", "permiso", "visa", "jubilación", "salud", "educación",
    "vivienda", "trabajo", "ACESS", "IESS", "SRI", "notaría", "judicial",
    "extranjeros", "naturalización", "defunción", "matrimonio", "divorcio"
]

# --- 2. Funciones de Extracción de URLs ---

def get_urls_from_page(driver, url, url_set):
    """Obtiene todas las URLs de trámites de una única página y las añade a un set."""
    try:
        driver.get(url)
        # Aumentamos la espera para sitios con mucho JS
        time.sleep(4) 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Selectores combinados para manejar inconsistencias en el HTML
        links = soup.select('h3.field-content a, div.listing-boxes-text h3 a')
        
        if not links:
            return False # Indica que no se encontraron más enlaces

        found_new = False
        for link in links:
            if link.has_attr('href'):
                full_url = BASE_URL + link['href']
                if full_url not in url_set:
                    url_set.add(full_url)
                    found_new = True
        
        print(f"Encontradas {len(links)} URLs. Total acumulado: {len(url_set)}")
        # Si no encontramos ninguna URL nueva, asumimos que hemos llegado al final de la paginación
        return found_new
    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        return True # Continuamos aunque esta página falle

# --- 3. Función de Extracción de Detalles (Basada en el Blueprint) ---

def scrape_tramite_details(tramite_url):
    """Extrae los detalles de una página de trámite individual usando los selectores del informe."""
    print(f"Extrayendo: {tramite_url.split('/')[-1]}")
    try:
        response = requests.get(tramite_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Funciones de ayuda para una extracción segura y limpia
        def get_text_safely(selector):
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else "No disponible"

        def get_html_safely(selector):
            element = soup.select_one(selector)
            return str(element) if element else "No disponible"
            
        def get_link_safely(selector):
            element = soup.select_one(selector)
            return element['href'] if element and element.has_attr('href') else "No disponible"

        # Mapeo directo desde la Tabla 3.3 del informe de investigación
        tramite_data = {
            "Nombre_Tramite": get_text_safely("h1.page-header"),
            "Institucion_Responsable": get_text_safely(".field--name-field-institucion-responsable .field--item a"),
            "URL_Fuente": tramite_url,
            "Descripcion": get_text_safely(".field--name-field-descripcion .field--item"),
            "A_Quien_Dirigido": get_text_safely("div.field--name-field-a-quien-esta-dirigido-"),
            "Que_Obtendre": get_text_safely("div.panel-success .panel-body"), # Selector adaptado
            "Requisitos": get_html_safely("div.field--name-field-requisitos .field--item"),
            "Como_Hacer_Tramite": get_html_safely("div.field--name-field-procedimiento .field--item"),
            "Costo": get_text_safely("div.field--name-field-costo p"),
            "Horario_Atencion": get_text_safely("div.field--name-field-horario .field--item"),
            "URL_Tramite_En_Linea": get_link_safely(".links--tramite-en-linea a")
        }
        
        return tramite_data

    except requests.exceptions.RequestException as e:
        print(f"  -> Error al extraer detalles de {tramite_url}: {e}")
        return None

# --- 4. Orquestador Principal ---

if __name__ == "__main__":
    print("Configurando el navegador Selenium para la recolección exhaustiva...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    all_urls = set()

    # FASE 1: RASTREO COMPLETO DE LA LISTA PRINCIPAL
    print("\n=== INICIANDO FASE 1: RASTREO DE LISTA COMPLETA ===")
    for i in range(500): # Límite de seguridad alto
        if not get_urls_from_page(driver, LIST_URL_TEMPLATE.format(page=i), all_urls):
            break

    # FASE 2: BÚSQUEDA DIRIGIDA POR PALABRAS CLAVE
    print("\n=== INICIANDO FASE 2: BÚSQUEDA POR PALABRAS CLAVE ===")
    for keyword in SEARCH_KEYWORDS:
        print(f"\n--- Buscando trámites para la palabra clave: '{keyword}' ---")
        for i in range(20): # Límite de páginas por búsqueda
            url = SEARCH_URL_TEMPLATE.format(keyword=quote(keyword), page=i)
            if not get_urls_from_page(driver, url, all_urls):
                break
    
    driver.quit()
    final_urls = list(all_urls)
    print(f"\nRecolección HÍBRIDA finalizada. Total de URLs únicas encontradas: {len(final_urls)}")

    # FASE 3: EXTRACCIÓN DE DETALLES
    if final_urls:
        all_tramites = []
        for i, url in enumerate(final_urls):
            print(f"--- Procesando Trámite {i+1}/{len(final_urls)} ---")
            details = scrape_tramite_details(url)
            if details:
                all_tramites.append(details)
            time.sleep(0.2)

        output_filename = "tramites_extraidos_COMPLETO.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_tramites, f, ensure_ascii=False, indent=4)
        
        print(f"\n¡PROCESO COMPLETADO! Se han guardado {len(all_tramites)} trámites en '{output_filename}'.")
