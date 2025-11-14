# app/semantic.py
from sentence_transformers import SentenceTransformer  # type: ignore
import numpy as np

# Load model once at module level (cached)
_model = None

def _get_model():
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

def similarity(text1: str, text2: str) -> float:
    """
    Compute semantic similarity between two texts.
    Returns float in range [-1, 1], but typically [0, 1] for similar texts.
    Expect ≥0.80 to pass validation.
    """
    if not text1 or not text2:
        return 0.0
    
    model = _get_model()
    embeddings = model.encode([text1, text2])
    
    # Cosine similarity
    cos_sim = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    
    return float(cos_sim)

