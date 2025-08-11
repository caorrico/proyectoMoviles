Chatbot de Trámites del Gobierno de Ecuador
Este proyecto es un asistente conversacional inteligente diseñado para responder preguntas de los ciudadanos sobre los trámites disponibles en el portal oficial gob.ec. Utiliza técnicas de web scraping para recolectar datos, una base de datos vectorial (ChromaDB) para búsqueda semántica y un Large Language Model (LLM a través de Groq) para generar respuestas en lenguaje natural.

Arquitectura Final
El proyecto sigue un flujo de tres pasos principales:

Scraping (Extracción): El script scraper.py navega por el portal gob.ec, extrae la información detallada de cada trámite y la guarda en tramites_extraidos.json.

Ingesta (Indexación): El script ingest_chroma.py lee el archivo JSON, limpia los datos y los convierte en vectores numéricos que se almacenan en una base de datos local de ChromaDB (tramites_chroma_db/).

Servicio (API Conversacional): El script main.py levanta un servidor FastAPI que expone un endpoint /chat. Este servicio utiliza la base de datos ChromaDB para encontrar los trámites más relevantes a la pregunta de un usuario y luego usa la API de Groq para generar una respuesta coherente y amable.

2. Actualiza tu requirements.txt
Asegúrate de que tu archivo requirements.txt contenga únicamente las librerías que la versión final del proyecto necesita.

# requirements.txt

# Para el Web Scraper
requests
beautifulsoup4

# Para la Ingesta y el Servidor del Chatbot
langchain
langchain-community
langchain-groq
sentence-transformers
chromadb
fastapi
uvicorn[standard]
python-dotenv

Puedes instalar todas estas dependencias con:

pip install -r requirements.txt

3. Cómo Ejecutar el Proyecto Completo
Sigue estos pasos en orden:

Paso A: Extraer los Datos (Solo si necesitas actualizarlos)
Este paso solo es necesario si quieres obtener la información más reciente de gob.ec.

python scraper.py

Esto generará (o actualizará) el archivo tramites_extraidos.json.

Paso B: Crear la Base de Datos Vectorial (Solo si los datos cambiaron)
Ejecuta este paso solo después de haber corrido el scraper.

python ingest_chroma.py

Esto creará (o actualizará) la carpeta tramites_chroma_db/.

Paso C: Iniciar el Servidor del Chatbot
Este es el paso principal para usar la aplicación.
Asegúrate de tener tu clave de Groq en un archivo .env.

uvicorn main:app --reload --port 8000

¡Y listo! Tu chatbot estará disponible y listo para responder preguntas en http://127.0.0.1:8000.