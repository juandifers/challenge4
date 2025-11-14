import io
from pypdf import PdfReader

def procesar_documento(file_bytes: bytes) -> str:
    """
    Toma los bytes de un archivo PDF y devuelve todo el texto extraído.
    Usa pypdf, que es ideal para PDFs digitales (no escaneados).
    
    Args:
        file_bytes: Los bytes crudos del archivo PDF (ej: de file_uploader.getvalue()).

    Returns:
        Un string con todo el texto del PDF.
    """
    try:
        pdf_stream = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_stream)
        
        texto_completo = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                texto_completo += text + "\n\n" 
                
        if not texto_completo:
            return "El PDF parece estar vacío o contener solo imágenes. No se pudo extraer texto digital."
            
        return texto_completo
        
    except Exception as e:
        print(f"Error al procesar PDF con pypdf: {e}")
        raise Exception(f"Error al leer el PDF: {e}")