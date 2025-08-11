# scraper_final.py
# Versión final y más robusta.
# Implementa "esperas explícitas" para manejar contenido dinámico de forma confiable.

import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# <-- CAMBIO: Importaciones necesarias para las esperas inteligentes ---
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# --- Fin del Cambio ---
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
from bs4 import BeautifulSoup

BASE_URL = "https://www.gob.ec"
SEARCH_URL_TEMPLATE = f"{BASE_URL}/tramites/buscar?search_api_fulltext={{keyword}}"
URLS_CHECKPOINT_FILE = "urls_encontradas.json"
TRAMITES_OUTPUT_FILE = "tramites_extraidos_COMPLETO.json"

def setup_driver():
    """Configura e inicializa el driver de Selenium."""
    print("Configurando el navegador Selenium...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(45)
    return driver

def get_tramite_urls(driver, keywords, max_pages_per_keyword=20):
    """Navega por los resultados de búsqueda y recopila URLs de forma robusta."""
    tramite_urls = set()
    print(f"Iniciando recolección de URLs basada en palabras clave...")

    for keyword in keywords:
        print(f"\n--- Buscando trámites para la palabra clave: '{keyword}' ---")
        for page_num in range(max_pages_per_keyword):
            encoded_keyword = quote(keyword)
            search_url = f"{SEARCH_URL_TEMPLATE.format(keyword=encoded_keyword)}&page={page_num}"
            
            print(f"Procesando página de resultados: {page_num + 1}...")
            
            try:
                driver.get(search_url)
                
                # --- CAMBIO CRUCIAL: Espera Inteligente ---
                # En lugar de time.sleep(), esperamos hasta 15 segundos a que el primer resultado aparezca.
                wait = WebDriverWait(driver, 15)
                # Usamos un selector más específico que coincide con el HTML que mostraste.
                selector_resultados = "div.recent-listing-box-container-item h3.field-content a"
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_resultados)))
                # --- Fin del Cambio ---

                links = driver.find_elements(By.CSS_SELECTOR, selector_resultados)
                
                if not links:
                    print(f"No se encontraron más enlaces para '{keyword}'. Pasando a la siguiente palabra clave.")
                    break

                found_new = False
                for link in links:
                    full_url = link.get_attribute('href')
                    if full_url and full_url.startswith(BASE_URL) and full_url not in tramite_urls:
                        tramite_urls.add(full_url)
                        found_new = True
                
                print(f"Encontradas {len(links)} URLs potenciales. Total acumulado: {len(tramite_urls)}")
                if not found_new and page_num > 0:
                    print("Parece que no hay URLs nuevas en esta página, terminando con esta palabra clave.")
                    break

            except TimeoutException:
                # Esto ahora significa que después de 15 segundos, la página realmente no cargó resultados.
                print(f"Timeout esperando resultados para '{keyword}' en la página {page_num + 1}. Pasando a la siguiente.")
                break
            except Exception as e:
                print(f"Error inesperado al procesar la página {page_num + 1} para '{keyword}': {e}")
                continue

    print(f"\nRecolección finalizada. Total de URLs únicas encontradas: {len(tramite_urls)}")
    return list(tramite_urls)

# (La función scrape_tramite_details y el resto del script no necesitan cambios)
def scrape_tramite_details(driver, tramite_url):
    """Extrae los detalles de una página de trámite individual usando Selenium."""
    print(f"Extrayendo: {tramite_url.split('/')[-1]}")
    try:
        driver.get(tramite_url)
        time.sleep(1) # Pequeña espera para asegurar que todo cargue
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        def get_text_safely(selector):
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else "No disponible"

        def get_section_content_as_text(section_id):
            start_tag = soup.find('h3', id=section_id)
            if not start_tag: return "No disponible"
            
            content_html = []
            for sibling in start_tag.find_next_siblings():
                if sibling.name == 'h3' and sibling.has_attr('id'):
                    break
                content_html.append(str(sibling))
            
            return BeautifulSoup("".join(content_html), "html.parser").get_text(separator='\n', strip=True).strip()

        tramite_data = {
            "Nombre_Tramite": get_text_safely("h1.page-header"),
            "Institucion_Responsable": get_text_safely("div.gob-entidade a"),
            "URL_Fuente": tramite_url,
            "Descripcion": get_section_content_as_text("description"),
            "A_Quien_Dirigido": get_section_content_as_text("beneficiary"),
            "Que_Obtendre": get_text_safely("div.panel-success .panel-body"),
            "Requisitos": get_section_content_as_text("requirements"),
            "Como_Hacer_Tramite": get_section_content_as_text("steps"),
            "Costo": get_text_safely("div#money div.field-item"),
            "Ubicacion_Horarios": get_section_content_as_text("location"),
            "Base_Legal": get_text_safely("div#panel-legal div.field-item"),
            "Fecha_Actualizacion": get_text_safely("div.view-mode-full div.text-right > p, div.field--name-field-fecha-de-actualizacion .field__item").replace("Fecha de última actualización:", "").strip(),
            "Canales_Atencion": get_text_safely("div.field--name-field-canales-de-atencion-ciud .field__item")
        }
        
        return tramite_data

    except Exception as e:
        print(f"  -> Error CRÍTICO al extraer detalles de {tramite_url}: {e}")
        return None

if __name__ == "__main__":
    SEARCH_KEYWORDS = [
        "cédula", "pasaporte", "licencia", "matrícula", "impuesto", "registro",
        "certificado", "permiso", "visa", "jubilación", "salud", "educación",
        "vivienda", "trabajo", "ACESS", "IESS", "SRI", "notaría", "judicial",
        "extranjeros", "naturalización", "defunción", "matrimonio", "divorcio"
    ]

    all_urls = []
    if os.path.exists(URLS_CHECKPOINT_FILE):
        print(f"Se encontró el archivo '{URLS_CHECKPOINT_FILE}'. ¿Desea reanudar usando estas URLs? (s/n)")
        choice = input().lower()
        if choice == 's':
            with open(URLS_CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                all_urls = json.load(f)
            print(f"Se cargaron {len(all_urls)} URLs. Saltando la fase de recolección.")
        else:
            print("Se ignorará el archivo existente. Recolectando URLs desde cero.")
            # Borramos el archivo para que no vuelva a preguntar si se interrumpe
            os.remove(URLS_CHECKPOINT_FILE) 

    driver = setup_driver()
    
    if not all_urls:
        all_urls = get_tramite_urls(driver, keywords=SEARCH_KEYWORDS)
        with open(URLS_CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_urls, f, ensure_ascii=False, indent=4)
        print(f"\nSe han guardado {len(all_urls)} URLs en '{URLS_CHECKPOINT_FILE}' como punto de control.")

    if all_urls:
        all_tramites = []
        # --- MEJORA: Cargar trámites ya procesados para no repetir trabajo ---
        if os.path.exists(TRAMITES_OUTPUT_FILE):
            print(f"Cargando {len(all_tramites)} trámites previamente extraídos de '{TRAMITES_OUTPUT_FILE}'...")
            with open(TRAMITES_OUTPUT_FILE, 'r', encoding='utf-8') as f:
                try:
                    all_tramites = json.load(f)
                except json.JSONDecodeError:
                    all_tramites = []
        
        processed_urls = {tramite['URL_Fuente'] for tramite in all_tramites}
        urls_to_process = [url for url in all_urls if url not in processed_urls]

        print(f"URLs totales: {len(all_urls)}. Ya procesadas: {len(processed_urls)}. Pendientes: {len(urls_to_process)}.")

        for i, url in enumerate(urls_to_process):
            print(f"\n--- Procesando Trámite {i+1}/{len(urls_to_process)} (Global {len(processed_urls) + i + 1}/{len(all_urls)}) ---")
            details = scrape_tramite_details(driver, url)
            if details and details["Nombre_Tramite"] != "No disponible":
                all_tramites.append(details)
            
            if (i + 1) % 10 == 0 and all_tramites: # Guardado progresivo
                 print(f"Guardando progreso... {len(all_tramites)} trámites guardados.")
                 with open(TRAMITES_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(all_tramites, f, ensure_ascii=False, indent=4)
        
        with open(TRAMITES_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_tramites, f, ensure_ascii=False, indent=4)
        
        print(f"\n¡PROCESO COMPLETADO! Se han guardado {len(all_tramites)} trámites en '{TRAMITES_OUTPUT_FILE}'.")

    driver.quit()