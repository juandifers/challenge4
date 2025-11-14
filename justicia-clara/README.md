# Justicia Clara - Simplificación de Textos Legales

Sistema para simplificar textos legales en español a lenguaje claro, manteniendo el significado original.

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Si necesitas CPU-only PyTorch (opcional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 2. Configuración

Crea un archivo `.env` en la raíz del proyecto:

```bash
# LLM Provider
MODEL_PROVIDER=ollama  # o "openai"

# OpenAI (si usas OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Ollama (si usas Ollama)
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Preparar Ollama (si usas Ollama)

```bash
# Asegúrate de que Ollama esté corriendo
ollama serve

# Descargar modelo (si no lo tienes)
ollama pull llama3
```

### 4. Ejecutar la UI

```bash
cd justicia-clara
streamlit run ui.py
```

La aplicación se abrirá en `http://localhost:8501`

## 📋 Uso

### Interfaz Web (Streamlit)

1. Abre la aplicación en tu navegador
2. Usa la pestaña **PDF** para subir un PDF
3. O usa la pestaña **Texto** para pegar texto directamente
4. Haz clic en "Procesar"
5. Revisa los resultados:
   - Estado de validación (Aprobado/Rechazado)
   - Similitud semántica
   - Texto simplificado
   - Detalles de validación

### CLI (próximamente)

```bash
python cli.py data/raw/sample.txt
```

## 🧪 Archivo de Prueba

Hay un archivo de ejemplo en `data/raw/sample.txt` que puedes usar para probar el sistema.

## 📁 Estructura del Proyecto

```
justicia-clara/
├── app/
│   ├── __init__.py
│   ├── schema.py       # Modelos Pydantic
│   ├── llm.py          # Integración LLM (Ollama/OpenAI)
│   ├── checks.py       # Validaciones determinísticas
│   ├── semantic.py     # Similitud semántica
│   ├── ocr.py          # OCR con docTR (opcional)
│   └── pipeline.py     # Orquestación principal
├── data/
│   ├── raw/            # Archivos de entrada
│   └── outputs/        # Resultados JSON
├── cli.py              # CLI (en desarrollo)
├── ui.py               # Interfaz Streamlit
└── requirements.txt    # Dependencias
```

## 🔍 Validaciones

El sistema valida que la simplificación:
- ✅ Mantiene los mismos importes
- ✅ Mantiene las mismas fechas
- ✅ Mantiene los mismos artículos legales
- ✅ No invierte negaciones
- ✅ Tiene similitud semántica ≥ 0.80
- ✅ Pasa la evaluación del "juez" LLM

## 🛠️ Troubleshooting

### Error: "Import doctr could not be resolved"
- Es solo una advertencia del IDE. El código funciona correctamente.

### Error: "Ollama connection failed"
- Asegúrate de que `ollama serve` esté corriendo
- Verifica que el modelo esté descargado: `ollama list`

### Error: "OpenAI API key not found"
- Crea el archivo `.env` con tu `OPENAI_API_KEY`
- O cambia `MODEL_PROVIDER=ollama` en `.env`

### OCR no funciona
- Asegúrate de tener `python-doctr[torch]` instalado
- Los modelos de docTR se descargan automáticamente la primera vez

## 📝 Notas

- El primer modelo (simplificación) usa **OpenAI** por defecto
- El segundo modelo (juez) usa **Ollama** por defecto
- Puedes cambiar los proveedores en `app/pipeline.py` o vía variables de entorno

