"""Titel/Namen vergleichbar machen und ihre Aehnlichkeit bewerten -
Mechanismus geteilt von allen *desk-Apps, die einen Datei-/Ordnernamen gegen
eine Online-Quelle abgleichen (Filmtitel bei moviedesk, Comic-Reihenname bei
comicdesk, ...).
"""
from __future__ import annotations

import difflib
import re

_ARTICLES = {"the", "a", "an", "der", "die", "das", "les", "la", "le", "el"}
_punct_re = re.compile(r"[^\w\s]", re.UNICODE)
_space_re = re.compile(r"\s+")


def normalize_title(name: str) -> str:
    """Titel auf eine vergleichbare Form bringen: kleingeschrieben,
    Satzzeichen entfernt, fuehrende/eingestreute Artikel raus."""
    name = _punct_re.sub(" ", (name or "").casefold())
    words = [w for w in _space_re.split(name) if w and w not in _ARTICLES]
    return " ".join(words)


def title_similarity(a: str, b: str) -> float:
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    return difflib.SequenceMatcher(None, na, nb).ratio()
