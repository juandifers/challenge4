# app/pipeline.py
import re, unicodedata
from app.schema import SimplifyResult
from app.llm import chat, chat_json
from app.checks import rule_checks
from app.semantic import similarity
from app.docTR import procesar_documento  # Importa tu extractor de texto
from app.llm import llamar_a_ollama     # Importa tu lógica de LLM
import io

SIMPLIFY_PROMPT = """Eres un editor legal.
Reescribe el texto en lenguaje claro sin cambiar significado.
No cambies importes, fechas, nombres, órganos, artículos ni condiciones.
Frases cortas. Devuelve SOLO el texto simplificado.
"""

JUDGE_PROMPT = """Compara ORIGINAL vs CLARO y devuelve SOLO JSON:
{"verdict":"equivalent|minor_diffs|mismatch","issues":[],"changed_numbers":[],"changed_dates":[],"changed_parties":[],"negation_flip":false}
Criterio: mismo significado y mismos valores; estilo puede cambiar.
"""

def _clean(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("\xa0"," ")
    return re.sub(r"[ \t]+"," ", s).strip()

def judge_equivalence(original: str, simplified: str) -> dict:
    user = f"ORIGINAL:\n<<<\n{original}\n>>>\nCLARO:\n<<<\n{simplified}\n>>>"
    # Judge with OLLAMA (local)
    return chat_json(JUDGE_PROMPT, user, provider="ollama")

def process_text(text: str) -> tuple[SimplifyResult, bool]:
    original = _clean(text)
    # Simplify with OPENAI (ChatGPT)
    simplified = chat(SIMPLIFY_PROMPT, original, provider="openai").strip()

    checks, details = rule_checks(original, simplified)
    sim = round(similarity(original, simplified), 3)
    judge = judge_equivalence(original, simplified)

    payload = SimplifyResult(
        original=original,
        simplified=simplified,
        checks=checks,
        details=details,
        similarity=sim,
        judge=judge
    )

    ok = all(v for k,v in checks.items() if k!="negation_flip") \
         and not checks.get("negation_flip") \
         and sim >= 0.80 \
         and judge.get("verdict") in ("equivalent","minor_diffs")

    return payload, bool(ok)

def ejecutar_pipeline(file_bytes: bytes, file_type: str, user_question: str) -> str:
    """
    Función principal que orquesta todo el proceso.
    1. Extrae texto del documento.
    2. Construye el prompt.
    3. Llama al LLM.
    4. Devuelve la respuesta.
    """
    
    # --- 1. Extraer texto del documento ---
    document_content = ""
    try:
        if file_type == "application/pdf":
            # Llamamos a la función en docTR.py
            document_content = procesar_documento(file_bytes)
        elif file_type == "text/plain":
            # Los TXT los leemos directamente
            document_content = file_bytes.decode("utf-8")
        else:
            raise Exception(f"Tipo de archivo no soportado: {file_type}")
    except Exception as e:
        raise Exception(f"Error en la extracción de texto: {e}")

    # --- 2. Construir el prompt final ---
    final_prompt = f"""
    **Instrucción:** {user_question}

    **Documento a procesar:**
    ---
    {document_content}
    ---
    """

    # --- 3. Llama al LLM ---
    try:
        # Llamamos a la función en llm.py
        response = llamar_a_ollama(final_prompt)
        return response
    except Exception as e:
        raise Exception(f"Error al llamar al LLM: {e}")