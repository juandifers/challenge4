import streamlit as st
import ollama
import io
from pypdf import PdfReader  # Importante: necesitarás instalar pypdf

# Título y configuración de la página
st.title("Challenge 4 - Justice Made Clear")
st.caption("Usando Streamlit y Ollama (Llama 2)")

# --- 1. Widget para subir archivos ---
# Añadimos el file_uploader para permitir PDF y TXT
uploaded_file = st.file_uploader(
    "Adjunta un documento PDF:",
    type=["pdf"]
)

# --- 2. Área de texto para el prompt del usuario ---
# (Mantenemos tu lógica de session_state)
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

def actualizar_prompt():
    """Callback para actualizar el prompt en el session_state."""
    st.session_state.prompt = st.session_state.input_prompt

# El prompt ahora pide una acción sobre el documento
prompt = st.text_area(
    "Escribe tu pregunta (ej: 'Simplifica el documento adjunto'):",
    height=100,
    key="input_prompt",
    on_change=actualizar_prompt
)

# --- 3. Lógica del botón Enviar (Actualizada) ---
if st.button("Enviar"):
    user_question = st.session_state.prompt
    document_content = ""

    # Validar que el usuario haya escrito una pregunta
    if not user_question:
        st.warning("Por favor, escribe una pregunta (ej: 'Simplifica este documento').")
    else:
        st.info("Procesando... Por favor, espera.")

        # --- Lógica para procesar el archivo subido ---
        if uploaded_file is not None:
            try:
                st.info(f"Leyendo el archivo: {uploaded_file.name}...")
                
                if uploaded_file.type == "application/pdf":
                    # Usar io.BytesIO para leer el archivo en memoria
                    file_stream = io.BytesIO(uploaded_file.getvalue())
                    pdf_reader = PdfReader(file_stream)
                    
                    # Extraer texto de todas las páginas
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            document_content += text + "\n"
                
                elif uploaded_file.type == "text/plain":
                    # Decodificar el archivo de texto
                    document_content = uploaded_file.getvalue().decode("utf-8")
                
                st.success("Archivo leído con éxito.")

            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
                st.stop()  # Detener la ejecución si el archivo falla

        # --- Construir el prompt final para Ollama ---
        final_prompt = ""
        if document_content:
            # Si hay un documento, lo combinamos con la pregunta
            final_prompt = f"""
            **Instrucción:** {user_question}

            **Documento a procesar:**
            ---
            {document_content}
            ---
            """
        else:
            # Si no hay documento, solo se envía la pregunta
            final_prompt = user_question

        # --- Llamar a Ollama ---
        try:
            st.info("Generando respuesta de Ollama...")
            response = ollama.chat(model='llama2', messages=[
                {'role': 'user', 'content': final_prompt}
            ])
            
            st.success("Respuesta generada:")
            st.write(response['message']['content'])

        except Exception as e:
            st.error(f"Error al contactar con Ollama: {e}")
            st.error("Asegúrate de que la aplicación Ollama esté ejecutándose localmente.")