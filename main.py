# main.py
# Versión unificada y final que usa ChromaDB directamente para la búsqueda semántica.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os
from dotenv import load_dotenv

# Cargar las variables de entorno (nuestra clave de API de Groq)
load_dotenv()

# --- 1. Configuración ---
CHROMA_DB_PATH = "tramites_chroma_db"  # Asegúrate de que esta carpeta exista
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama3-8b-8192"

# --- 2. Modelo de Datos para la API de Chat ---
class ChatQuery(BaseModel):
    query_text: str

# --- 3. Inicialización de la Aplicación FastAPI ---
app = FastAPI(
    title="Chatbot de Trámites Ecuador (con ChromaDB)",
    description="Servicio autónomo que responde preguntas usando una base de datos vectorial.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Lógica del Chatbot ---

# Plantilla del Prompt para la respuesta final
RESPONSE_PROMPT_TEMPLATE = """
Eres un asistente virtual amigable y servicial del gobierno de Ecuador. Tu única función es responder preguntas sobre trámites basándote estrictamente en la información que te proporciono a continuación. Responde en español, de forma clara y concisa. Si la información no contiene la respuesta, di amablemente que no encontraste los detalles sobre esa consulta específica.

**Información de Trámites Relevantes que encontré:**
{context}

---

**Pregunta del Ciudadano:**
{question}

**Tu Respuesta:**
"""

# Variable global para la cadena RAG
rag_chain = None

@app.on_event("startup")
async def startup_event():
    """Al iniciar el servidor, carga la base de datos y prepara la cadena de RAG."""
    global rag_chain
    
    print("Cargando la base de datos ChromaDB...")
    if not os.path.exists(CHROMA_DB_PATH):
        print(f"Error: La carpeta de la base de datos '{CHROMA_DB_PATH}' no fue encontrada.")
        print("Por favor, asegúrate de ejecutar primero el script 'ingest_chroma.py'.")
        return

    try:
        embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
        db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
        
        # Creamos un "retriever" que buscará los 3 documentos más relevantes
        retriever = db.as_retriever(search_kwargs={'k': 3})
        
        model = ChatGroq(model=GROQ_MODEL)
        prompt = ChatPromptTemplate.from_template(RESPONSE_PROMPT_TEMPLATE)
        
        # Definimos la cadena de RAG (Retrieval-Augmented Generation)
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        print("¡Servicio de Chatbot listo y conectado a ChromaDB!")
    except Exception as e:
        print(f"Error fatal al inicializar el servicio: {e}")
        rag_chain = None

# --- 5. Definición de los Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Chatbot de Trámites de Ecuador. Usa /docs para interactuar."}

@app.post("/chat")
async def handle_chat(query: ChatQuery):
    """
    Maneja una pregunta del usuario, la procesa y devuelve una respuesta conversacional.
    """
    if not rag_chain:
        raise HTTPException(status_code=503, detail="El servicio de Chatbot no está inicializado correctamente. Revisa los logs del servidor.")

    print(f"Pregunta recibida: '{query.query_text}'")
    
    # Invocamos la cadena RAG directamente con la pregunta del usuario
    response = rag_chain.invoke(query.query_text)
    
    print(f"Respuesta generada: '{response}'")
    return {"response": response}

# --- 6. Punto de Entrada para Ejecutar el Servidor ---
if __name__ == "__main__":
    import uvicorn
    # Ejecutamos este único servicio
    uvicorn.run(app, host="0.0.0.0", port=8001)
