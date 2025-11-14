# app/ocr.py
from __future__ import annotations
from typing import Literal, Optional
from doctr.io import DocumentFile  # type: ignore
from doctr.models import ocr_predictor  # type: ignore

# Load once (CPU). If you later want a lighter model: det_arch="db_mobilenet_v3_large", reco_arch="crnn_mobilenet_v3_small"
_OCR = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="crnn_vgg16_bn",
    pretrained=True
)

def run_doctr_bytes(file_bytes: bytes, filetype: Optional[Literal["pdf","image"]] = None, dpi: int = 200) -> str:
    """
    OCR for scanned PDFs or images (PNG/JPG). Returns plain text (pages concatenated).
    - filetype="pdf" forces PDF rasterization; otherwise tries images.
    - dpi: rasterization for PDFs (200 is a good speed/quality trade-off).
    """
    if filetype == "pdf":
        doc = DocumentFile.from_pdf(file_bytes, dpi=dpi)
    elif filetype == "image":
        doc = DocumentFile.from_images(file_bytes)
    else:
        # Heuristic: if it starts with "%PDF" treat as PDF
        if file_bytes[:4] == b"%PDF":
            doc = DocumentFile.from_pdf(file_bytes, dpi=dpi)
        else:
            doc = DocumentFile.from_images(file_bytes)

    result = _OCR(doc).export()  # dict with pages/blocks/lines/words
    lines = []
    for page in result.get("pages", []):
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                lines.append("".join(w["value"] for w in line.get("words", [])))
    return "\n".join(lines).strip()

def run_doctr_path(path: str, dpi: int = 200) -> str:
    """
    Convenience helper if you have a file path instead of bytes.
    """
    if path.lower().endswith(".pdf"):
        doc = DocumentFile.from_pdf(path, dpi=dpi)
    else:
        doc = DocumentFile.from_images(path)
    result = _OCR(doc).export()
    out = []
    for page in result.get("pages", []):
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                out.append("".join(w["value"] for w in line.get("words", [])))
    return "\n".join(out).strip()
