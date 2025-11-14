# app/llm.py
import os, json, requests
from dotenv import load_dotenv
load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE  = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ---- low-level callers ----

def _chat_openai(system: str, user: str, model: str | None = None, temperature: float = 0.0) -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=temperature,
    )
    return resp.choices[0].message.content

def _chat_ollama(system: str, user: str, model: str | None = None, temperature: float = 0.0, num_ctx: int = 2048) -> str:
    """
    Optimized Ollama chat with reduced context window for faster processing.
    num_ctx: Context window size (default 2048, was 4096)
    """
    payload = {
        "model": model or OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,  # Reduced from 4096 to 2048 for speed
            "num_predict": 512,  # Limit response length
        },
        "stream": False,
    }
    # Reduced timeout (3 minutes should be enough with optimizations)
    r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["message"]["content"]

# ---- public helpers ----

def chat(system: str, user: str, *, provider: str, model: str | None = None, temperature: float = 0.0, num_ctx: int = 2048) -> str:
    """
    provider: "openai" or "ollama"
    num_ctx: Context window for Ollama (ignored for OpenAI)
    """
    provider = provider.lower()
    if provider == "openai":
        return _chat_openai(system, user, model=model, temperature=temperature)
    if provider == "ollama":
        return _chat_ollama(system, user, model=model, temperature=temperature, num_ctx=num_ctx)
    raise ValueError(f"Unknown provider: {provider}")

def chat_json(system: str, user: str, *, provider: str, model: str | None = None, num_ctx: int = 2048) -> dict:
    """
    Ensures strict JSON by retrying once with stronger instruction.
    num_ctx: Context window for Ollama (ignored for OpenAI)
    """
    raw = chat(system, user, provider=provider, model=model, temperature=0.0, num_ctx=num_ctx)
    try:
        return json.loads(raw)
    except Exception:
        raw2 = chat(system + "\nDevuelve SOLO JSON válido. Sin comentarios.", user,
                    provider=provider, model=model, temperature=0.0, num_ctx=num_ctx)
        return json.loads(raw2)
