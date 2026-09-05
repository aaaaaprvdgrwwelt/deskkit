"""Pfad-Hilfen fuer den gezielten Rescan eines einzelnen Eintrags statt des
ganzen Wurzelordners - geteilt von allen *desk-Apps mit dieser Funktion
(moviedesk: ein Film/eine Serie, audiodesk: ein Album/Hoerbuch, ...).
"""
from __future__ import annotations

from pathlib import Path


def subfolder_of(path: Path, root: Path) -> Path:
    """Der direkte Unterordner von `root`, der `path` enthaelt - z. B. der
    Ordner einer einzelnen Serie/eines einzelnen Albums fuer den gezielten
    Scan. Liegt `path` direkt in `root` (kein eigener Unterordner), wird
    `root` selbst zurueckgegeben."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return root
    return root / rel.parts[0] if len(rel.parts) > 1 else root
