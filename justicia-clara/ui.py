import streamlit as st
import io
from pathlib import Path
from pypdf import PdfReader
from app.pipeline import process_text
from app.ocr import run_doctr_bytes

# Page config
st.set_page_config(page_title="Justicia Clara", layout="wide")

st.title("🔍 Justicia Clara")
st.caption("Simplificación de textos legales en lenguaje claro")

# Ensure data/raw directory exists
raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

# Tabs for different input methods
tab1, tab2 = st.tabs(["📄 PDF", "📝 Texto"])

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF, using OCR if text layer is empty."""
    try:
        file_stream = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(file_stream)
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # If no text extracted, try OCR
        if not text.strip():
            st.info("No se encontró texto en el PDF. Intentando OCR...")
            text = run_doctr_bytes(file_bytes, filetype="pdf")
        
        return text
    except Exception as e:
        st.error(f"Error al procesar PDF: {e}")
        return ""

# Tab 1: PDF Upload
with tab1:
    st.header("📄 Procesamiento de PDF")
    
    # File upload - saves to data/raw
    uploaded_file = st.file_uploader(
        "Sube un PDF (se guardará en data/raw/)",
        type=["pdf"],
        help="El archivo se guardará automáticamente en data/raw/ y se procesará"
    )
    
    # Save uploaded file to data/raw
    if uploaded_file is not None:
        file_path = raw_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.success(f"✅ Archivo guardado en: {file_path}")
        st.session_state['file_uploaded'] = True
    
    # Auto-process first file in data/raw
    pdf_files = sorted(list(raw_dir.glob("*.pdf")), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if pdf_files:
        # Get the first (most recent) file
        first_file = pdf_files[0]
        
        st.info(f"📁 Procesando: **{first_file.name}** (archivo más reciente en data/raw/)")
        
        # Auto-process on page load or when file is uploaded
        if 'processed_file' not in st.session_state or st.session_state.get('processed_file') != first_file.name or st.session_state.get('file_uploaded', False):
            with st.spinner("🔄 Procesando PDF..."):
                # Read file
                with open(first_file, "rb") as f:
                    file_bytes = f.read()
                
                # Extract text
                with st.spinner("📖 Extrayendo texto del PDF..."):
                    text = extract_text_from_pdf(file_bytes)
                
                if text:
                    st.success(f"✅ Texto extraído ({len(text)} caracteres)")
                    
                    # Process through pipeline
                    with st.spinner("🤖 Simplificando con LLM..."):
                        result, ok = process_text(text)
                    
                    # Save result
                    output_dir = Path("data/outputs")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / f"{first_file.stem}_result.json"
                    
                    import json
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
                    
                    st.session_state['processed_file'] = first_file.name
                    st.session_state['result'] = result
                    st.session_state['ok'] = ok
                    st.session_state['output_file'] = str(output_file)
                    st.session_state['file_uploaded'] = False
                else:
                    st.error("❌ No se pudo extraer texto del PDF")
                    st.session_state['processed_file'] = None
        
        # Display results if available
        if 'result' in st.session_state and st.session_state.get('result'):
            result = st.session_state['result']
            ok = st.session_state.get('ok', False)
            
            st.divider()
            st.subheader("📊 Resultados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Estado", "✅ Aprobado" if ok else "❌ Rechazado")
                st.metric("Similitud", f"{result.similarity:.3f}")
            
            with col2:
                checks_pass = all(v for k, v in result.checks.items() if k != "negation_flip")
                st.metric("Verificación", "✅ Pass" if checks_pass else "❌ Fail")
                st.metric("Negación", "✅ OK" if not result.checks.get("negation_flip") else "❌ Cambiada")
            
            # Show simplified text
            st.subheader("📝 Texto Simplificado")
            st.text_area("", result.simplified, height=400, key="simplified_pdf")
            
            # Show details
            with st.expander("📊 Detalles de Validación"):
                st.json({
                    "checks": result.checks,
                    "details": result.details,
                    "judge": result.judge
                })
            
            # Show original (collapsed)
            with st.expander("📄 Texto Original"):
                st.text_area("", result.original, height=300, key="original_pdf")
            
            if 'output_file' in st.session_state:
                st.success(f"💾 Resultado guardado en: {st.session_state['output_file']}")
    else:
        st.warning("⚠️ No hay archivos PDF en data/raw/. Sube un PDF para comenzar.")

# Tab 2: Text Input
with tab2:
    st.header("Ingresar Texto")
    text_input = st.text_area(
        "Pega el texto legal aquí",
        height=300,
        help="Ingresa el texto legal que deseas simplificar"
    )
    
    if st.button("Procesar Texto", type="primary"):
        if not text_input.strip():
            st.warning("Por favor, ingresa algún texto")
        else:
            with st.spinner("Simplificando texto..."):
                result, ok = process_text(text_input)
            
            # Display results
            st.subheader("Resultado")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Estado", "✅ Aprobado" if ok else "❌ Rechazado")
                st.metric("Similitud", f"{result.similarity:.3f}")
            
            with col2:
                st.metric("Verificación", "✅ Pass" if all(v for k, v in result.checks.items() if k != "negation_flip") else "❌ Fail")
                st.metric("Negación", "✅ OK" if not result.checks.get("negation_flip") else "❌ Cambiada")
            
            # Show simplified text
            st.subheader("Texto Simplificado")
            st.text_area("", result.simplified, height=300, key="simplified_text")
            
            # Show details
            with st.expander("📊 Detalles de Validación"):
                st.json({
                    "checks": result.checks,
                    "details": result.details,
                    "judge": result.judge
                })
            
            # Show original (collapsed)
            with st.expander("📄 Texto Original"):
                st.text_area("", result.original, height=200, key="original_text")
