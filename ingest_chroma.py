# ingest_chroma_mejorado.py
# Lee el JSON, limpia CADA campo que pueda tener HTML y lo carga en ChromaDB
# con un formato mucho más rico y estructurado.

import json
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

# --- 1. Configuración ---
JSON_FILE_PATH = "tramites_extraidos_COMPLETO.json"
CHROMA_DB_PATH = "tramites_chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def clean_html(html_content):
    """
    Usa BeautifulSoup para limpiar etiquetas HTML de un texto.
    Si el contenido no es HTML o está vacío, lo devuelve formateado.
    """
    if html_content and isinstance(html_content, str) and '<' in html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        # Utiliza separador para mantener saltos de línea lógicos y strip=True para limpiar espacios
        return soup.get_text(separator="\n", strip=True)
    # Si no es HTML, asegúrate de que sea una cadena de texto limpia
    return str(html_content).strip() if html_content else "No disponible"

def load_and_prepare_documents():
    """Carga los trámites desde el JSON y los prepara como documentos de LangChain."""
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                print(f"Advertencia: El archivo '{JSON_FILE_PATH}' está vacío.")
                return []
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{JSON_FILE_PATH}'. Asegúrate de haber ejecutado el scraper primero.")
        return []
    except json.JSONDecodeError:
        print(f"Error: El archivo '{JSON_FILE_PATH}' no es un JSON válido.")
        return []

    documents = []
    print(f"Procesando {len(data)} trámites desde el archivo JSON...")

    for tramite in data:
        # --- MODIFICADO: Limpieza individual y exhaustiva de cada campo ---
        # Se limpian todos los campos que potencialmente contienen HTML o necesitan formateo.
        
        # Diccionario para almacenar los textos limpios y evitar repeticiones de .get()
        cleaned_text = {
            "Nombre_Tramite": tramite.get("Nombre_Tramite", "No disponible"),
            "Institucion_Responsable": tramite.get("Institucion_Responsable", "No disponible"),
            "URL_Fuente": tramite.get("URL_Fuente", "No disponible"),
            "Descripcion": clean_html(tramite.get("Descripcion")),
            "A_Quien_Dirigido": clean_html(tramite.get("A_Quien_Dirigido")),
            "Que_Obtendre": clean_html(tramite.get("Que_Obtendre")),
            "Requisitos": clean_html(tramite.get("Requisitos")),
            "Como_Hacer_Tramite": clean_html(tramite.get("Como_Hacer_Tramite")),
            "Costo": clean_html(tramite.get("Costo")),
            "Ubicacion_Horarios": clean_html(tramite.get("Ubicacion_Horarios")),
            "Base_Legal": clean_html(tramite.get("Base_Legal")),
            "Fecha_Actualizacion": tramite.get("Fecha_Actualizacion", "No disponible"),
            "Canales_Atencion": clean_html(tramite.get("Canales_Atencion"))
        }

        # --- MODIFICADO: Formato de `page_content` mucho más completo y legible ---
        # Se estructura la información con títulos claros para que el LLM pueda entender
        # el contexto de cada pieza de información.
        page_content = f"""
**Trámite:** {cleaned_text['Nombre_Tramite']}
**Institución Responsable:** {cleaned_text['Institucion_Responsable']}

**Descripción General:**
{cleaned_text['Descripcion']}

**¿A quién está dirigido?**
{cleaned_text['A_Quien_Dirigido']}

**¿Qué obtendré si completo el trámite?**
{cleaned_text['Que_Obtendre']}

**Requisitos:**
{cleaned_text['Requisitos']}

**¿Cómo hago el trámite? (Procedimiento):**
{cleaned_text['Como_Hacer_Tramite']}

**Costo:**
{cleaned_text['Costo']}

**Canales de Atención:**
{cleaned_text['Canales_Atencion']}

**Ubicación y Horarios de Atención:**
{cleaned_text['Ubicacion_Horarios']}

**Base Legal:**
{cleaned_text['Base_Legal']}

**URL de la Fuente Oficial:**
{cleaned_text['URL_Fuente']}

**Fecha de Última Actualización de la Información:**
{cleaned_text['Fecha_Actualizacion']}
        """.strip()

        # Creamos el objeto Document de LangChain
        doc = Document(
            page_content=page_content,
            metadata={
                "source": cleaned_text['URL_Fuente'],
                "nombre_tramite": cleaned_text['Nombre_Tramite']
            }
        )
        documents.append(doc)
    
    print(f"Se han preparado {len(documents)} documentos para ser ingresados a la base de datos.")
    return documents

def main():
    """Función principal que orquesta la creación de la base de datos vectorial."""
    print("Iniciando la ingesta de datos en ChromaDB...")

    if os.path.exists(CHROMA_DB_PATH):
        print(f"Eliminando la base de datos antigua en '{CHROMA_DB_PATH}' para asegurar una carga limpia.")
        shutil.rmtree(CHROMA_DB_PATH)
    
    # 1. Cargar y preparar los documentos
    documents = load_and_prepare_documents()
    if not documents:
        print("No hay documentos para procesar. Finalizando.")
        return

    # 2. Crear los embeddings y almacenar en ChromaDB
    print(f"Creando embeddings con el modelo '{EMBEDDING_MODEL}'...")
    print("Este proceso puede tardar varios minutos, por favor espera...")
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    vector_store = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    print(f"¡Proceso completado! Se ha guardado la base de datos vectorial en '{CHROMA_DB_PATH}'.")

if __name__ == "__main__":
    main()