# app/pipeline.py
import re, unicodedata
from app.schema import SimplifyResult
from app.llm import chat, chat_json
from app.checks import rule_checks
from app.semantic import similarity

SIMPLIFY_PROMPT = """Eres un lingüista-jurista y redactor claro con 15+ años de experiencia. Vas a procesar un archivo .txt o .json que contiene el texto completo o estructurado de una sentencia o resolución judicial española (p. ej., Juzgado de Primera Instancia). Tu misión tiene dos partes: (A) verificar formalmente la sentencia con un checklist oficial y (B) producir una versión simplificada fiel al sentido jurídico, aplicando la guía de redacción.

Contexto estratégico
- La ciudadanía espera entender con facilidad los documentos judiciales relevantes para su vida.
- Operadores jurídicos y la Administración buscan maximizar la transparencia, reducir reclamaciones por falta de claridad y aumentar la confianza pública.
- La IA puede simplificar sentencias y autos siguiendo reglas oficiales, adaptando el contenido sin perder el sentido jurídico.
Objetivo del sistema: generar versiones simplificadas de documentos judiciales y verificar su corrección formal.
Meta: simplificar sin perder el sentido jurídico.

Alcance de entrada
- Si el archivo es .txt, analiza todo el texto.
- Si el archivo es .json, revisa los valores de cada clave para localizar encabezado, partes, antecedentes, fundamentos, fallo, costas, recursos y protección de datos (p. ej., "fundamentos": "...", "fallo": "...").

Reglas de exactitud y fidelidad
1) No inventes datos. Si falta información, marca [DATO NO DISPONIBLE].
2) Conserva hechos, pretensiones, fundamentos y parte dispositiva. No alteres el alcance de la resolución, importes, fechas ni consecuencias jurídicas.
3) Mantén las referencias legales (artículos, leyes, jurisprudencia). Explícalas en lenguaje llano y colócalas preferentemente al final de la frase/párrafo.
4) Si detectas contradicciones o lagunas, señálalas explícitamente.

PARTE A — Verificación formal (Checklist oficial de 8 puntos)
Comprueba, uno por uno, los siguientes elementos esenciales y evalúa su estado como Presente / Ausente / Parcial, añadiendo un comentario breve o el fragmento detectado:
1. Encabezado institucional:
   - Roj / ECLI
   - Id Cendoj
   - Órgano judicial (Juzgado de Primera Instancia nº __)
   - Sede y sección
   - Fecha de la resolución
   - Nº de recurso y resolución
   - Tipo de procedimiento
   - Nombre del ponente o juez
   - Tipo de resolución (sentencia, auto, etc.)
2. Identificación de las partes:
   - Demandante, demandado, procuradores, abogados, representación/apoderamiento
3. Antecedentes de hecho:
   - Exposición del proceso (demanda, contestación, audiencia previa), hechos y pruebas, cumplimiento de prescripciones legales
4. Fundamentos de derecho:
   - Estructura numerada (PRIMERO, SEGUNDO…)
   - Citas normativas (CC, LEC, Ley de Usura, TRLGDCU, Dir. 93/13/CEE…)
   - Jurisprudencia (TS, AP, TJUE)
   - Aplicación razonada al caso
5. Decisión o fallo:
   - Epígrafe “FALLO”
   - Decisión (estimación/desestimación)
   - Consecuencias jurídicas (nulidad, condena, restitución…)
   - Indicación sobre ejecución o liquidación
6. Costas procesales: pronunciamiento claro
7. Recursos:
   - Si es firme o recurrible, plazo y órgano competente
8. Cláusula de protección de datos:
   - Advertencia sobre anonimización y difusión de datos personales

Salida requerida para la PARTE A (en Markdown):
- Tabla con 3 columnas exactamente:
  | 🟩 Elemento | 🟨 Estado (Presente / Ausente / Parcial) | 🟥 Comentarios o fragmento detectado / faltante |
- Después de la tabla, añade:
  Sección: **Elementos no estándar detectados**
  ➡️ Enumera cualquier contenido impropio o inusual (datos personales sin ocultar, leyes extranjeras, estructuras no típicas, etc.).
- Si todos los elementos están presentes y completos:
  ✅ Indica: “Cumple con todos los requisitos formales de una sentencia española.”

PARTE B — Versión simplificada con guía de redacción (9 puntos)
Produce una versión clara y comprensible para cualquier ciudadano, SIN perder el sentido jurídico. Aplica estrictamente estos 9 puntos:
1) Enumeraciones: usa series para ítems simples y listas para ítems complejos; numera cuando el orden o la cantidad importen (la parte dispositiva siempre numerada).
2) Mayusculismo: evita mayúsculas expresivas; usa minúsculas normativas (“juzgado”, salvo inicio de enunciado).
3) Fechas y plazos: estilo “En [Ciudad], a 1 de febrero de 2023”; expresa plazos preferentemente en cifras (p. ej., 10 días). No uses MAYÚSCULAS sostenidas para enfatizar; usa negrita cuando sea relevante.
4) Reubicación de información: acerca cada dato al bloque que afecta (p. ej., nº de cuenta junto al requerimiento de pago); referencias legales al final de la frase/párrafo para no romper la lectura.
5) Formas de tratamiento: “Sr./Sra.” para personas intervinientes; “Don/Doña” sólo para magistratura o LAJ. Evita fórmulas arcaicas.
6) Terminología: sustituye tecnicismos por términos comunes o explícalos (p. ej., “enervación del desahucio” → “paralizar el desahucio”).
7) Extensión de oraciones: evita oraciones > 40 palabras; divide y dosifica la información.
8) Orden oracional: prioriza Sujeto + Verbo + Objeto; evita inversiones innecesarias.
9) Futuro de subjuntivo: reemplázalo por presente/condicional (“tuviere”, “tratare” → formas actuales).

Controles de calidad para la PARTE B
- Lenguaje español (ES), tono respetuoso y directo; explica latinismos si aparecen.
- Coherencia terminológica en todo el texto.
- No cambies importes, fechas, partes ni efectos jurídicos.
- Señala contradicciones o vacíos en una nota final, sin suplirlos con invenciones.

Estructura obligatoria de salida para la PARTE B (en este orden, en Markdown):
A. Resumen ejecutivo (5–8 líneas, sin jerga)
B. Partes y rol procesal
C. Hechos: probados vs. controvertidos
D. Fundamentos jurídicos (explicados en llano, con referencias al final)
E. Parte dispositiva (lista numerada)
F. Fechas y plazos clave (tabla: concepto | fecha/plazo | cómputo | efecto)
G. Qué debe hacer la persona afectada (viñetas accionables)
H. Glosario (término técnico → explicación común)
I. Notas de reubicación y coherencia (qué moviste y por qué)

Formato global de la respuesta
- Devuelve SIEMPRE las dos secciones, en este orden:
  1) **VALIDACIÓN FORMAL (Checklist de 8 puntos)** con la tabla y la sección “Elementos no estándar detectados” (+ la indicación final de cumplimiento si procede).
  2) **VERSIÓN SIMPLIFICADA (con los 9 puntos aplicados)** siguiendo los apartados A–I.
- Todo en Markdown. No incluya código ni JSON salvo que la entrada venga en JSON (en cuyo caso puedes citar claves).
"""

JUDGE_PROMPT = """[SYSTEM]
Eres un Validador de Simplificación Jurídica. Tu tarea es EVALUAR (no reescribir) si una versión simplificada de un documento judicial:
(1) mantiene el MISMO SENTIDO JURÍDICO del original; y
(2) cumple con 9 criterios de redacción jurídica clara.
Devuelve EXCLUSIVAMENTE un JSON válido que siga el esquema indicado. No incluyas texto adicional, explicaciones fuera del JSON ni formato Markdown.

[USER]
# CONTEXTO DEL RETO
Hoy en día, los ciudadanos esperan poder entender fácilmente cualquier documento judicial relevante para su vida. Los operadores jurídicos y la administración buscan maximizar la transparencia, reducir reclamaciones por falta de claridad y aumentar la confianza pública. La IA puede simplificar sentencias y autos siguiendo reglas oficiales, adaptando el contenido sin perder el sentido jurídico.
Objetivo: generar versiones simplificadas de documentos judiciales con IA y recomendaciones de simplificación.
Meta: simplificar sin perder el sentido jurídico.

# ENTRADAS
Documento_original (texto completo):
{{DOCUMENTO_ORIGINAL}}

Salida_simplificada_GPT (JSON o texto estructurado):
{{SALIDA_SIMPLIFICADA_JSON}}

Guia_9_puntos (si no se provee, usa la lista por defecto):
{{GUIA_9_PUNTOS_OPCIONAL}}

# GUIA DE 9 PUNTOS (por defecto, si no se envía una guía propia)
1) Lenguaje llano y cotidiano; definir términos jurídicos imprescindibles.
2) Idea principal y decisión judicial claras al inicio (resumen/antecedentes/resultado).
3) Estructura lógica con títulos y un solo tema por párrafo.
4) Frases concisas, voz activa y sujeto explícito; evitar subordinadas largas.
5) Coherencia factual y temporal (nombres, fechas, plazos, cuantías) sin contradicciones.
6) Evitar latinismos, jerga y siglas; si aparecen, explicar la primera vez.
7) Uso de listas y numeración para condiciones, requisitos y efectos; evitar bloques densos.
8) Tono neutral y preciso; sin opiniones ni consejos no contenidos en el original.
9) Accesibilidad y claridad para público general; evitar ambigüedades; incluir glosario si procede.

# PROCEDIMIENTO DE VALIDACIÓN (PASO A PASO)
A. Extrae del Documento_original las PROPOSICIONES JURÍDICAS CLAVE:
   - Hechos relevantes
   - Partes y roles procesales
   - Pretensiones/objeto
   - Fundamentos jurídicos (normas/doctrina citadas)
   - Decisión/fallo y sus efectos
   - Plazos, cuantías, obligaciones, prohibiciones, recursos
B. Alinea cada proposición con su correspondiente en la Salida_simplificada_GPT y marca su estado:
   - "conservada", "parcial", "omitida", "distorsionada" o "inventada"
C. Señala cualquier cambio de sentido (p. ej., inversión de cargas, modificación de plazos/montos, ampliación/restricción de derechos, atribución de hechos a partes incorrectas).
D. Evalúa el cumplimiento de los 9 puntos (usa evidencia breve y, si aplica, fragmentos cortos).
E. Calcula puntajes:
   - equivalencia_juridica.puntaje_0_100 (pondera: fallo/efectos 35%, fundamentos 25%, hechos 20%, plazos/montos/condiciones 20%)
   - guia_clara.puntaje_0_100 (cada punto ~11.1%; marca “crítica” cuando compromete la comprensión)
F. Define riesgo_juridico: "bajo" (≥90), "medio" (70–89), "alto" (<70) según equivalencia.
G. Veredicto:
   - "ACEPTAR" si equivalencia ≥90 y hay ≥8/9 puntos cumplidos (sin fallas críticas).
   - "RECHAZAR" en caso contrario.
H. Propón correcciones puntuales SOLO como sugerencias (no reescribas el documento completo).

# ESQUEMA DE SALIDA (DEVUELVE SOLO ESTE JSON)
{
  "veredicto": "ACEPTAR" | "RECHAZAR",
  "equivalencia_juridica": {
    "puntaje_0_100": number,
    "riesgo_juridico": "bajo" | "medio" | "alto",
    "resumen": "string breve",
    "proposiciones": [
      {
        "tipo": "hecho|parte|pretension|fundamento|fallo|plazo|monto|obligacion|prohibicion|recurso|otro",
        "original": "string (cita breve o paráfrasis fiel)",
        "simplificado": "string (fragmento correspondiente)",
        "estado": "conservada|parcial|omitida|distorsionada|inventada",
        "nota": "string opcional sobre el desajuste"
      }
    ],
    "alertas_cambio_sentido": [
      "string (p.ej., 'plazo reducido de 30 a 10 días')"
    ]
  },
  "guia_clara": {
    "puntaje_0_100": number,
    "chequeos": [
      {
        "punto": 1,
        "nombre": "Lenguaje llano y definiciones",
        "cumple": true | false,
        "severidad": "menor" | "critica",
        "evidencia": "string breve",
        "sugerencia": "string accionable"
      }
      // ... puntos 2 a 9 con mismo formato
    ]
  },
  "hallucinations": [
    "string (elementos no presentes en el original que aparecen en la salida)"
  ],
  "omisiones_relevantes": [
    "string (elementos del original que faltan en la salida y afectan el sentido)"
  ],
  "consistencia_y_datos": {
    "fechas": "ok|inconsistentes",
    "montos": "ok|inconsistentes",
    "nombres_partes": "ok|inconsistentes",
    "referencias_normativas": "ok|inconsistentes"
  },
  "sugerencias_de_correccion": [
    "string (cambio concreto para alinear sentido o cumplir guía)"
  ],
  "metadatos": {
    "modelo_validador": "nombre_del_modelo_ollama",
    "fecha_validacion": "YYYY-MM-DD",
    "version_esquema": "1.0.0"
  }
}

# REGLAS
- NO reescribas por completo la salida; limita las "sugerencias_de_correccion" a ajustes puntuales.
- Cita fragmentos muy breves cuando sirvan como evidencia.
- Si la Salida_simplificada_GPT no es JSON, intenta parsearla; si es imposible, pon veredicto "RECHAZAR" y explica en "resumen".
- Devuelve SOLO el JSON anterior, sin texto adicional."""

def _clean(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("\xa0"," ")
    return re.sub(r"[ \t]+"," ", s).strip()

def judge_equivalence(original: str, simplified: str) -> dict:
    """
    Judge equivalence with optimizations for speed:
    - Truncates text to reduce context
    - Uses smaller context window
    - Samples text for very long documents
    """
    # More aggressive truncation for speed (2000 chars = ~500 tokens each)
    MAX_LENGTH = 2000  # Reduced from 8000 for faster processing
    
    # For very long texts, sample beginning and end
    if len(original) > MAX_LENGTH * 2:
        orig_sample = original[:MAX_LENGTH] + "\n[... texto intermedio omitido ...]\n" + original[-MAX_LENGTH:]
        simp_sample = simplified[:MAX_LENGTH] + "\n[... texto intermedio omitido ...]\n" + simplified[-MAX_LENGTH:]
    else:
        orig_sample = original[:MAX_LENGTH] + "..." if len(original) > MAX_LENGTH else original
        simp_sample = simplified[:MAX_LENGTH] + "..." if len(simplified) > MAX_LENGTH else simplified
    
    # Replace placeholders in the prompt with actual content
    prompt = JUDGE_PROMPT.replace("{{DOCUMENTO_ORIGINAL}}", orig_sample)
    prompt = prompt.replace("{{SALIDA_SIMPLIFICADA_JSON}}", simp_sample)
    prompt = prompt.replace("{{GUIA_9_PUNTOS_OPCIONAL}}", "")  # Use default guide
    
    # The prompt is now complete, so we pass empty user message
    user = ""  # All content is in the system prompt now
    
    try:
        # Judge with OLLAMA (local) - use smaller context
        return chat_json(prompt, user, provider="ollama", num_ctx=2048)
    except Exception as e:
        # Fallback if Ollama fails (timeout, connection error, etc.)
        return {
            "veredicto": "RECHAZAR",
            "equivalencia_juridica": {
                "puntaje_0_100": 0,
                "riesgo_juridico": "alto",
                "resumen": f"Error en validación: {str(e)}",
                "proposiciones": [],
                "alertas_cambio_sentido": []
            },
            "guia_clara": {
                "puntaje_0_100": 0,
                "chequeos": []
            },
            "hallucinations": [],
            "omisiones_relevantes": [],
            "consistencia_y_datos": {
                "fechas": "unknown",
                "montos": "unknown",
                "nombres_partes": "unknown",
                "referencias_normativas": "unknown"
            },
            "sugerencias_de_correccion": [],
            "metadatos": {
                "modelo_validador": "ollama_error",
                "fecha_validacion": "unknown",
                "version_esquema": "1.0.0"
            }
        }

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

    # OK if all checks pass AND similarity OK AND judge approves
    # New judge schema uses "veredicto": "ACEPTAR" | "RECHAZAR"
    judge_verdict = judge.get("veredicto", judge.get("verdict", "RECHAZAR"))  # Support both old and new schema
    judge_ok = judge_verdict in ("ACEPTAR", "equivalent", "minor_diffs")  # Support both formats
    
    # Also check equivalence score if available (new schema)
    equiv_score = judge.get("equivalencia_juridica", {}).get("puntaje_0_100", 100)
    if isinstance(equiv_score, (int, float)) and equiv_score < 90:
        judge_ok = False
    
    ok = all(v for k,v in checks.items() if k!="negation_flip") \
         and not checks.get("negation_flip") \
         and sim >= 0.80 \
         and judge_ok

    return payload, bool(ok)
