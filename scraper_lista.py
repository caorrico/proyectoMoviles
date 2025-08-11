# scraper.py
# Versión final y robusta con Selenium para extraer TODOS los trámites de gob.ec.

import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.gob.ec"
LIST_URL = f"{BASE_URL}/tramites/lista"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_tramite_urls(max_pages=500):
    """Navega por el listado de trámites usando un navegador real (Selenium) y recopila todas las URLs."""
    print("Configurando el navegador Selenium...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en segundo plano sin abrir una ventana
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Instala y configura el driver de Chrome automáticamente
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    tramite_urls = set()
    print(f"Iniciando recolección de URLs de trámites...")

    for page_num in range(max_pages):
        page_url = f"{LIST_URL}?page={page_num}"
        print(f"Procesando página de listado: {page_num + 1}")

        try:
            driver.get(page_url)
            # Esperamos a que el contenido dinámico cargue
            time.sleep(3) 

            # Pasamos el HTML renderizado a BeautifulSoup para parsearlo
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            links = soup.select('h3.field-content a, div.listing-boxes-text h3 a')

            if not links:
                print("No se encontraron más enlaces. Terminando recolección.")
                break

            for link in links:
                if link.has_attr('href'):
                    full_url = BASE_URL + link['href']
                    tramite_urls.add(full_url)
            
            print(f"Encontradas {len(links)} URLs. Total acumulado: {len(tramite_urls)}")

        except Exception as e:
            print(f"Error al procesar la página {page_num + 1}: {e}")
            continue

    driver.quit() # Cerramos el navegador
    print(f"Recolección finalizada. Total de URLs únicas encontradas: {len(tramite_urls)}")
    return list(tramite_urls)

def scrape_tramite_details(tramite_url):
    """Extrae los detalles de una página de trámite individual."""
    print(f"Extrayendo: {tramite_url.split('/')[-1]}")
    try:
        response = requests.get(tramite_url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        def get_text_safely(selector):
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else "No disponible"

        def get_section_content_as_text(section_id):
            start_tag = soup.find(id=section_id)
            if not start_tag: return "No disponible"
            content_html = []
            for sibling in start_tag.find_next_siblings():
                if (sibling.name == 'div' and 'panel' in sibling.get('class', [])) or \
                   (sibling.name == 'h3' and sibling.has_attr('id')):
                    break
                content_html.append(str(sibling))
            if content_html:
                return BeautifulSoup("".join(content_html), "html.parser").get_text(separator='\n', strip=True)
            return "No disponible"

        tramite_data = {
            "Nombre_Tramite": get_text_safely("h1.page-header"),
            "Institucion_Responsable": get_text_safely("div.alert-info a"),
            "URL_Fuente": tramite_url,
            "Descripcion": get_text_safely("div#description"),
            "A_Quien_Dirigido": get_section_content_as_text("beneficiary"),
            "Que_Obtendre": get_text_safely("div.panel-success .panel-body"),
            "Requisitos": get_section_content_as_text("requirements"),
            "Como_Hacer_Tramite": get_section_content_as_text("steps"),
            "Costo": get_section_content_as_text("money"),
            "Ubicacion_Horarios": get_section_content_as_text("location"),
            "Base_Legal": get_text_safely("div#panel-legal"),
            "Fecha_Actualizacion": get_text_safely("div.text-right > p").replace("Fecha de última actualización:", "").strip()
        }
        
        canales_atencion = "No disponible"
        for p_tag in soup.find_all('p'):
            if 'Canales de atención:' in p_tag.get_text():
                canales_atencion = p_tag.get_text(strip=True).replace('Canales de atención:', '').strip()
                break
        tramite_data["Canales_Atencion"] = canales_atencion
        
        return tramite_data

    except requests.exceptions.RequestException as e:
        print(f"  -> Error al extraer detalles de {tramite_url}: {e}")
        return None

if __name__ == "__main__":
    urls = get_tramite_urls(max_pages=500)

    if urls:
        all_tramites = []
        for i, url in enumerate(urls):
            print(f"--- Procesando Trámite {i+1}/{len(urls)} ---")
            details = scrape_tramite_details(url)
            if details:
                all_tramites.append(details)
            time.sleep(0.2) # Pausa mínima

        output_filename = "tramites_extraidos_LISTA.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_tramites, f, ensure_ascii=False, indent=4)
        
        print(f"\n¡PROCESO COMPLETADO! Se han guardado {len(all_tramites)} trámites en '{output_filename}'.")

