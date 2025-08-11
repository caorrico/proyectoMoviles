# main.py
# Versión 4.0: Implementa Reescritura de Consultas (Query Rewriting) para una búsqueda
# semántica de alta precisión y actualiza las librerías a la versión moderna.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
# --- CAMBIO: Importaciones modernas para Chroma y Embeddings ---
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# --- Fin del Cambio ---
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# --- 1. Configuración ---
CHROMA_DB_PATH = "tramites_chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama3-8b-8192"

# --- 2. Modelo de Datos ---
class ChatQuery(BaseModel):
    query_text: str

# --- 3. Inicialización de FastAPI ---
app = FastAPI(
    title="Asistente Inteligente de Trámites Ecuador",
    description="Un servicio de chat que utiliza reescritura de consultas para mejorar la precisión de la búsqueda.",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Lógica del Chatbot ---

# --- NUEVO: Plantilla para reescribir la pregunta del usuario ---
REWRITE_PROMPT_TEMPLATE = """
Tu tarea es tomar la siguiente pregunta de un usuario y reescribirla como una consulta de búsqueda optimizada y formal, como si fuera el título de un documento oficial del gobierno de Ecuador.
Concéntrate en las palabras clave y el objetivo del trámite. No respondas la pregunta, solo reescríbela.

Pregunta Original: "{question}"
Consulta Optimizada:
"""

# --- PROMPT FINAL MEJORADO ---
RESPONSE_PROMPT_TEMPLATE = """
Eres un asistente virtual experto en trámites del gobierno de Ecuador. Tu misión es dar respuestas claras y directas basadas ÚNICAMENTE en la información de los siguientes documentos.

**Contexto (Documentos Encontrados):**
{context}

**Instrucciones:**
1.  Analiza el contexto para responder a la **Pregunta Original del Ciudadano**.
2.  Si encuentras la respuesta, sintetiza la información clave: requisitos, pasos y costos.
3.  Si la pregunta pide un enlace (link) y está en el contexto, inclúyelo de forma clara.
4.  Si el contexto no contiene la respuesta, di amablemente: "Disculpa, no encontré información precisa sobre tu consulta en la base de datos. Te recomiendo visitar el portal oficial de gob.ec para más detalles."
5.  Siempre finaliza tu respuesta con la frase: "Recuerda verificar la información en la fuente oficial."

**Pregunta Original del Ciudadano:**
{question}

**Tu Respuesta Detallada:**
"""

rag_chain = None

@app.on_event("startup")
async def startup_event():
    global rag_chain
    
    print("Cargando la base de datos ChromaDB...")
    if not os.path.exists(CHROMA_DB_PATH):
        print(f"Error Crítico: El directorio '{CHROMA_DB_PATH}' no existe. Ejecuta el script de ingesta primero.")
        return

    try:
        # --- CAMBIO: Usamos las clases modernas ---
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
        # --- Fin del Cambio ---
        
        retriever = db.as_retriever(search_kwargs={'k': 4}) # Aumentamos a 4 para más contexto
        
        llm = ChatGroq(model=GROQ_MODEL)
        
        # --- NUEVO: Cadena de Reescritura ---
        rewrite_prompt = ChatPromptTemplate.from_template(REWRITE_PROMPT_TEMPLATE)
        query_rewriter = rewrite_prompt | llm | StrOutputParser()
        
        # --- CADENA RAG COMPLETA Y MEJORADA ---
        def retrieve_docs(query):
            """Función que reescribe la pregunta y luego busca en la DB."""
            print(f"Pregunta original: '{query}'")
            rewritten_query = query_rewriter.invoke({"question": query})
            print(f"Pregunta reescrita: '{rewritten_query}'")
            return retriever.invoke(rewritten_query)

        response_prompt = ChatPromptTemplate.from_template(RESPONSE_PROMPT_TEMPLATE)

        rag_chain = (
            {
                "context": RunnablePassthrough() | retrieve_docs,
                "question": RunnablePassthrough()
            }
            | response_prompt
            | llm
            | StrOutputParser()
        )
        print("¡Servicio de Chatbot listo y optimizado con Reescritura de Consultas!")
    except Exception as e:
        print(f"Error fatal durante la inicialización: {e}")
        rag_chain = None

# --- 5. Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Asistente Inteligente de Trámites. Usa el endpoint /chat."}

@app.post("/chat")
async def handle_chat(query: ChatQuery):
    if not rag_chain:
        raise HTTPException(status_code=503, detail="El servicio de Chatbot no está inicializado.")

    response = rag_chain.invoke(query.query_text)
    
    return {"response": response}

# --- 6. Ejecución ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)