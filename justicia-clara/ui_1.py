import streamlit as st
import io
# Importamos ÚNICAMENTE la función principal del pipeline
from app.pipeline import ejecutar_pipeline

# Título y configuración de la página
st.title("Challenge 4 - Justice Made Clear")
st.caption("Usando Streamlit y Ollama (Llama 2)")

# --- 1. Widget para subir archivos ---
uploaded_file = st.file_uploader(
    "Adjunta un documento (PDF o TXT):",
    type=["pdf", "txt"]
)

# --- 2. Área de texto para el prompt del usuario ---
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

def actualizar_prompt():
    """Callback para actualizar el prompt en el session_state."""
    st.session_state.prompt = st.session_state.input_prompt

prompt = st.text_area(
    "Escribe tu pregunta (ej: 'Simplifica el documento adjunto'):",
    height=100,
    key="input_prompt",
    on_change=actualizar_prompt
)

# --- 3. Lógica del botón Enviar (Totalmente actualizada) ---
if st.button("Procesar y Enviar"):
    user_question = st.session_state.prompt

    if not user_question:
        st.warning("Por favor, escribe una pregunta (ej: 'Simplifica este documento').")
    elif uploaded_file is None:
        st.warning("Por favor, adjunta un documento PDF o TXT.")
    else:
        st.info("Ejecutando pipeline... Por favor, espera.")

        try:
            # Obtenemos los bytes del archivo subido
            file_bytes = uploaded_file.getvalue()
            file_type = uploaded_file.type
            
            # --- AQUÍ LLAMAMOS AL PIPELINE ---
            # Le pasamos los bytes del archivo y la pregunta.
            # Toda la lógica de extracción y LLM ocurre en el backend.
            final_result = ejecutar_pipeline(file_bytes, file_type, user_question)
            
            st.success("Respuesta generada:")
            st.write(final_result)

        except Exception as e:
            st.error(f"Error al ejecutar el pipeline: {e}")
            if "ollama" in str(e).lower():
                st.error("Asegúrate de que la aplicación Ollama esté ejecutándose.")
            
# --- 4. Botón de Descarga Eliminado ---
# Ya no es necesario, el texto se pasa directamente al pipeline.