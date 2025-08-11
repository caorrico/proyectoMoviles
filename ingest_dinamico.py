# ingest_dinamico.py
# Versión dinámica que acepta múltiples archivos JSON, los une,
# elimina duplicados y los carga en ChromaDB en un solo paso.

import json
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil
import argparse
import sys

# --- 1. Configuración ---
CHROMA_DB_PATH = "tramites_chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def clean_html(html_content):
    if html_content and isinstance(html_content, str) and '<' in html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    return str(html_content).strip() if html_content else "No disponible"

def load_and_prepare_documents(json_files):
    """Carga trámites desde una lista de archivos JSON, los une, y los prepara."""
    
    tramites_unicos = {} # Usamos un diccionario para la deduplicación
    print("Iniciando carga y unificación de archivos JSON...")

    for file_path in json_files:
        try:
            print(f"-> Leyendo archivo: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                tramites = json.load(f)
                for tramite in tramites:
                    if isinstance(tramite, dict):
                        url = tramite.get("URL_Fuente")
                        if url and url not in tramites_unicos:
                            tramites_unicos[url] = tramite
                    else:
                        print(f"  -> Advertencia: Elemento no válido (no es un diccionario) en {file_path}. Saltando.")
        except FileNotFoundError:
            print(f"  -> Error: No se encontró el archivo '{file_path}'. Saltando.")
        except json.JSONDecodeError:
            print(f"  -> Error: El archivo '{file_path}' no es un JSON válido. Saltando.")
    
    lista_unificada = list(tramites_unicos.values())
    if not lista_unificada:
        print("Error Crítico: No se pudo cargar ningún trámite válido de los archivos proporcionados.")
        sys.exit(1)

    print(f"\nSe cargaron un total de {len(lista_unificada)} trámites únicos.")
    
    documents = []
    for tramite in lista_unificada:
        cleaned_text = {k: clean_html(v) for k, v in tramite.items()}
        page_content = f"""
**Trámite:** {cleaned_text.get('Nombre_Tramite', 'N/A')}
**Institución Responsable:** {cleaned_text.get('Institucion_Responsable', 'N/A')}
**Descripción General:** {cleaned_text.get('Descripcion', 'N/A')}
**¿A quién está dirigido?** {cleaned_text.get('A_Quien_Dirigido', 'N/A')}
**Requisitos:** {cleaned_text.get('Requisitos', 'N/A')}
**¿Cómo hago el trámite? (Procedimiento):** {cleaned_text.get('Como_Hacer_Tramite', 'N/A')}
**Costo:** {cleaned_text.get('Costo', 'N/A')}
**URL de la Fuente Oficial:** {cleaned_text.get('URL_Fuente', 'N/A')}
        """.strip()

        doc = Document(
            page_content=page_content,
            metadata={"source": cleaned_text.get('URL_Fuente', 'N/A')}
        )
        documents.append(doc)
    
    print(f"Se han preparado {len(documents)} documentos para ser ingresados a la base de datos.")
    return documents

def main():
    parser = argparse.ArgumentParser(
        description="Ingesta datos de uno o más archivos JSON de trámites en ChromaDB.",
        epilog="Ejemplo: python ingest_dinamico.py file1.json file2.json"
    )
    # --- CAMBIO CLAVE: nargs='+' permite uno o más argumentos ---
    parser.add_argument(
        "json_files", 
        nargs='+',
        help="Ruta a uno o más archivos JSON de trámites para ingestar."
    )
    args = parser.parse_args()
    
    print(f"Iniciando la ingesta de datos en ChromaDB...")
    print(f"Archivos a procesar: {', '.join(args.json_files)}")

    if os.path.exists(CHROMA_DB_PATH):
        print(f"Eliminando la base de datos antigua en '{CHROMA_DB_PATH}'.")
        shutil.rmtree(CHROMA_DB_PATH)
    
    documents = load_and_prepare_documents(args.json_files)
    if not documents:
        print("No hay documentos para procesar. Finalizando.")
        return

    print(f"Creando embeddings... (puede tardar varios minutos)")
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    Chroma.from_documents(
        documents=documents, 
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    print(f"¡Proceso completado! Se ha guardado la base de datos vectorial en '{CHROMA_DB_PATH}'.")

if __name__ == "__main__":
    main()