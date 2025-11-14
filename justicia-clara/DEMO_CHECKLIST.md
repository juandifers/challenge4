# ✅ Checklist para Demo

## Requisitos Previos

### 1. Dependencias Instaladas
- [x] `pip install -r requirements.txt` ejecutado
- [x] Todos los módulos importan correctamente

### 2. Configuración de LLM

**Opción A: Usar Ollama (Recomendado para demo local)**
```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# Si no está corriendo:
ollama serve

# Descargar modelo si no lo tienes:
ollama pull llama3
```

**Opción B: Usar OpenAI**
- [ ] Crear archivo `.env` con:
  ```
  OPENAI_API_KEY=sk-...
  OPENAI_MODEL=gpt-4o-mini
  ```

### 3. Archivo .env

Crea `justicia-clara/.env` con:
```env
# Para usar Ollama (juez)
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Para usar OpenAI (simplificación)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**Nota:** El pipeline usa OpenAI para simplificar y Ollama para el juez por defecto.

## 🚀 Ejecutar Demo

### Paso 1: Iniciar Streamlit
```bash
cd justicia-clara
streamlit run ui.py
```

### Paso 2: Probar con Archivo de Ejemplo
1. Abre `http://localhost:8501`
2. Ve a la pestaña **"Texto"**
3. Copia el contenido de `data/raw/sample.txt`
4. Pega en el área de texto
5. Haz clic en **"Procesar Texto"**

### Paso 3: Verificar Resultados
- ✅ Debe mostrar "Aprobado" o "Rechazado"
- ✅ Similitud debe ser ≥ 0.80
- ✅ Texto simplificado debe aparecer
- ✅ Detalles de validación deben mostrarse

## 🧪 Archivos de Prueba

- `data/raw/sample.txt` - Sentencia legal de ejemplo con:
  - Importes: 5.234,56 euros
  - Fechas: 15 de marzo de 2025, 11 de febrero de 2024
  - Artículos: artículo 389, artículo 1.254, etc.

## ⚠️ Problemas Comunes

### "Ollama connection failed"
- Verifica: `ollama serve` está corriendo
- Verifica: `ollama list` muestra el modelo

### "OpenAI API key not found"
- Crea `.env` con tu API key
- O modifica `pipeline.py` para usar solo Ollama

### "Model download" (primera vez)
- La primera vez que uses `semantic.py`, descargará el modelo de sentence-transformers (~400MB)
- La primera vez que uses `ocr.py`, descargará modelos de docTR (~160MB)

### Similitud baja (< 0.80)
- Normal si el texto es muy diferente
- Revisa los detalles en el expander "Detalles de Validación"

## 📊 Qué Esperar en el Demo

1. **Tiempo de procesamiento:** 5-15 segundos (depende de LLM)
2. **Resultados:**
   - Texto simplificado más corto y claro
   - Métricas de validación
   - JSON con detalles técnicos
3. **Validaciones:**
   - Importes preservados
   - Fechas preservadas
   - Artículos preservados
   - Sin inversión de negaciones

## 🎯 Próximos Pasos

- [ ] Implementar `cli.py` para procesamiento por lotes
- [ ] Agregar más ejemplos en `data/raw/`
- [ ] Mejorar prompts según feedback
- [ ] Ajustar umbrales de validación si es necesario

