# ingest_chroma.py
# Lee el JSON de trámites, limpia el HTML y lo carga en una base de datos ChromaDB.

import json
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# --- 1. Configuración ---
JSON_FILE_PATH = "tramites_extraidos.json"
CHROMA_DB_PATH = "tramites_chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def clean_html(html_content):
    """Usa BeautifulSoup para limpiar etiquetas HTML y devolver solo el texto."""
    if html_content and isinstance(html_content, str) and '<' in html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    return html_content if html_content else "No disponible"

def load_and_prepare_documents():
    """Carga los trámites desde el JSON y los prepara como documentos de LangChain."""
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{JSON_FILE_PATH}'.")
        return []

    documents = []
    for tramite in data:
        # Limpiamos los campos que contienen HTML
        requisitos_clean = clean_html(tramite.get("Requisitos"))
        como_hacer_tramite_clean = clean_html(tramite.get("Como_Hacer_Tramite"))
        base_legal_clean = clean_html(tramite.get("Base_Legal"))
        ubicacion_horarios_clean = clean_html(tramite.get("Ubicacion_Horarios"))

        # Creamos un único texto descriptivo para cada trámite.
        # Esto será lo que ChromaDB indexará y buscará.
        page_content = f"""
Nombre del Trámite: {tramite.get("Nombre_Tramite", "No disponible")}
Institución Responsable: {tramite.get("Institucion_Responsable", "No disponible")}
Descripción: {tramite.get("Descripcion", "No disponible")}
¿A quién está dirigido?: {tramite.get("A_Quien_Dirigido", "No disponible")}
¿Qué obtendré?: {tramite.get("Que_Obtendre", "No disponible")}
Requisitos: {requisitos_clean}
Pasos a seguir: {como_hacer_tramite_clean}
Costo: {tramite.get("Costo", "No disponible")}
Canales de Atención: {tramite.get("Canales_Atencion", "No disponible")}
Ubicación y Horarios: {ubicacion_horarios_clean}
Base Legal: {base_legal_clean}
        """.strip()

        # Creamos el objeto Document de LangChain
        doc = Document(
            page_content=page_content,
            metadata={
                "source": tramite.get("URL_Fuente", ""),
                "nombre_tramite": tramite.get("Nombre_Tramite", "")
            }
        )
        documents.append(doc)
    
    print(f"Se han preparado {len(documents)} documentos a partir del archivo JSON.")
    return documents

def main():
    """Función principal que orquesta la creación de la base de datos vectorial."""
    print("Iniciando la creación de la base de datos ChromaDB...")
    
    # 1. Cargar y preparar los documentos
    documents = load_and_prepare_documents()
    if not documents:
        return

    # 2. Crear los embeddings y almacenar en ChromaDB
    print("Creando embeddings y guardando en ChromaDB (esto puede tardar)...")
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Creamos la base de datos a partir de los documentos
    vector_store = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    vector_store.persist()
    print(f"¡Proceso completado! Se ha guardado la base de datos en '{CHROMA_DB_PATH}'.")

if __name__ == "__main__":
    main()
