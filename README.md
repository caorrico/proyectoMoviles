# asistente_MIES

Este proyecto es un asistente virtual que responde preguntas sobre los servicios del MIES (Ministerio de Inclusión Económica y Social de Ecuador). Utiliza un modelo de lenguaje de Groq para dar respuestas rápidas y precisas.

## Configuración Inicial

1.  **Instalar dependencias:**
    Abre una terminal y ejecuta el siguiente comando para instalar todas las librerías necesarias:
    ```bash
    pip install fastapi uvicorn[standard] pandas pypdf langchain langchain-community chromadb sentence-transformers
    ```

## Pasos para Ejecutar el Proyecto

### 1. Obtén tu Clave de API Gratuita de Groq

1.  Ve a la página de Groq: [https://console.groq.com/keys](https://console.groq.com/keys)
2.  Regístrate con tu cuenta de Google. Es gratis.
3.  Una vez dentro, haz clic en el botón **+ Create API Key**.
4.  Dale un nombre (ej: "chatbot-mies") y haz clic en **Create**.
5.  **¡MUY IMPORTANTE!** Se te mostrará tu clave secreta una sola vez. Cópiala inmediatamente y guárdala en un lugar seguro.

### 2. Instala las Nuevas Librerías

Detén tu servidor (con `CTRL+C`) y ejecuta este comando en tu terminal (con el `venv` activado) para instalar las librerías necesarias:

```bash
pip install langchain-groq python-dotenv
```

-   `langchain-groq`: Permite a LangChain comunicarse con la API de Groq.
-   `python-dotenv`: Una utilidad para manejar claves secretas de forma segura.

### 3. Crea un Archivo para tu Clave Secreta

En la carpeta de tu proyecto, al mismo nivel que `main.py`, crea un nuevo archivo llamado `.env`. Dentro de ese archivo, escribe lo siguiente, reemplazando `TU_API_KEY_DE_GROQ` con la clave que acabas de copiar:

```
GROQ_API_KEY="TU_API_KEY_DE_GROQ"
```

### 4. Actualiza tu `main.py`

Ahora, reemplaza todo el contenido de tu archivo `main.py` con la versión final que utiliza Groq en lugar de Ollama.

### ¡A Probar la Velocidad de la Luz!

1.  Asegúrate de haber guardado el archivo `.env` con tu clave.
2.  Inicia el servidor con el comando de siempre:

    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
3.  Ve a [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) y haz la misma pregunta.
