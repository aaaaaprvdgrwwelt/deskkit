"""Kleine Helfer rund um QSettings - geteilt von allen *desk-Apps."""
from __future__ import annotations


def as_bool(value, default: bool) -> bool:
    """QSettings liefert je nach Backend mal einen echten bool, mal den
    String "true"/"false" - hier auf einen Nenner gebracht."""
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes")
