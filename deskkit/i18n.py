"""Generisches Sprachumschaltungs-Grundgeruest - von allen *desk-Apps geteilt.

Jede App bringt ihre eigene Uebersetzungstabelle mit (ASCII-Deutsch als
Schluessel, siehe Docstring von `Translator`); dieses Modul kennt nur den
Mechanismus dahinter: aktive Sprache verfolgen, Systemsprache erkennen, in
der App-eigenen Tabelle nachschlagen.
"""
from __future__ import annotations

#: Code -> Anzeigename im Menue - gleich fuer alle Apps.
LANGUAGES = {"auto": "Automatisch", "de": "Deutsch", "en": "English"}

_SUPPORTED = ("de", "en")


def system_language() -> str:
    from PySide6.QtCore import QLocale

    code = QLocale.system().name().split("_")[0].lower()
    return code if code in _SUPPORTED else "en"


class Translator:
    """Haelt die aktive Sprache und die Uebersetzungstabelle einer App.

    Die Tabelle hat die Form `{"de": {...}, "en": {...}}`. Die
    Quelltext-Strings der App sind zugleich die Schluessel - ASCII-Deutsch,
    damit sie robust als Schluessel taugen. Fehlt ein Eintrag (in beiden
    Sprachen, oder weil die Tabelle fuer diese Sprache leer ist), liefert
    `__call__` den Schluessel selbst zurueck - die App bleibt so immer
    benutzbar, auch wenn eine Uebersetzung vergessen wurde.

    Eine Instanz ist selbst aufrufbar und ersetzt damit direkt das
    gewohnte `_("...")` - siehe die `i18n.py` der einzelnen Apps."""

    def __init__(self, table: dict[str, dict[str, str]]):
        self.table = table
        self.current = "de"

    def set_language(self, code: str) -> None:
        self.current = system_language() if code == "auto" else (
            code if code in _SUPPORTED else "de")

    def language(self) -> str:
        return self.current

    def __call__(self, text: str) -> str:
        """Uebersetzt `text` in die aktive Sprache."""
        return self.table.get(self.current, {}).get(text, text)
