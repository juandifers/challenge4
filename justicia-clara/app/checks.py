# app/checks.py
import re
from typing import Tuple

def _extract_amounts(text: str) -> list[str]:
    """Extract monetary amounts in Spanish format (1.234,56 €, 1234,56€, etc.)"""
    # Patterns: 1.234,56 €, 1234,56€, 1.234,56EUR, etc.
    patterns = [
        r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*€',
        r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*EUR',
        r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*euros?',
        r'\d+,\d{2}\s*€',  # Simple: 123,45 €
    ]
    amounts = []
    for pattern in patterns:
        amounts.extend(re.findall(pattern, text, re.IGNORECASE))
    return [a.strip() for a in amounts]

def _extract_dates(text: str) -> list[str]:
    """Extract dates in Spanish format (DD/MM/YYYY, DD-MM-YYYY, etc.)"""
    patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 11/02/2025, 11-02-2025
        r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',  # 11 de febrero de 2025
    ]
    dates = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    return dates

def _extract_articles(text: str) -> list[str]:
    """Extract legal article references (artículo, art., etc.)"""
    patterns = [
        r'(?:artículo|art\.?)\s+\d+',
        r'art\.\s+\d+',
    ]
    articles = []
    for pattern in patterns:
        articles.extend(re.findall(pattern, text, re.IGNORECASE))
    return articles

def _check_negation_flip(original: str, simplified: str) -> bool:
    """Check if negation was flipped (no -> sí, etc.)"""
    # Simple heuristic: count negation words
    neg_words_orig = len(re.findall(r'\b(?:no|nunca|ningún|ninguna|ninguno|tampoco)\b', original, re.IGNORECASE))
    neg_words_simp = len(re.findall(r'\b(?:no|nunca|ningún|ninguna|ninguno|tampoco)\b', simplified, re.IGNORECASE))
    
    # If count differs significantly, might be a flip
    if neg_words_orig == 0 and neg_words_simp > 0:
        return True
    if neg_words_simp == 0 and neg_words_orig > 0:
        return True
    
    # Check for explicit flips (simple pattern)
    if re.search(r'\bno\b', original, re.IGNORECASE) and re.search(r'\bsí\b', simplified, re.IGNORECASE):
        return True
    
    return False

def _cmp_lists(list1: list[str], list2: list[str]) -> bool:
    """Compare two lists of strings (normalized)"""
    def normalize(s: str) -> str:
        return re.sub(r'[^\w]', '', s.lower())
    
    norm1 = {normalize(x) for x in list1}
    norm2 = {normalize(x) for x in list2}
    return norm1 == norm2

def rule_checks(original: str, simplified: str) -> Tuple[dict, dict]:
    """
    Deterministic validation checks.
    Returns: (checks: dict, details: dict)
    """
    checks = {}
    details = {}
    
    # Extract amounts
    amounts_orig = _extract_amounts(original)
    amounts_simp = _extract_amounts(simplified)
    checks["amounts_ok"] = _cmp_lists(amounts_orig, amounts_simp)
    if not checks["amounts_ok"]:
        details["amounts"] = {
            "original": amounts_orig,
            "simplified": amounts_simp
        }
    
    # Extract dates
    dates_orig = _extract_dates(original)
    dates_simp = _extract_dates(simplified)
    checks["dates_ok"] = _cmp_lists(dates_orig, dates_simp)
    if not checks["dates_ok"]:
        details["dates"] = {
            "original": dates_orig,
            "simplified": dates_simp
        }
    
    # Extract articles
    articles_orig = _extract_articles(original)
    articles_simp = _extract_articles(simplified)
    checks["articles_ok"] = _cmp_lists(articles_orig, articles_simp)
    if not checks["articles_ok"]:
        details["articles"] = {
            "original": articles_orig,
            "simplified": articles_simp
        }
    
    # Check negation flip
    checks["negation_flip"] = _check_negation_flip(original, simplified)
    if checks["negation_flip"]:
        details["negation_flip"] = "Negation may have been flipped"
    
    return checks, details

