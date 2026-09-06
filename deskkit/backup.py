"""Bibliotheksindex sichern - geteilt von den *desk-Apps, bei denen die
SQLite-Datenbank (nicht eine Datei wie ComicInfo.xml) die Quelle der
Wahrheit fuer Zuordnungen ist (moviedesk, bookdesk, audiodesk).

Eine einfache Dateikopie waere riskant, waehrend die App laeuft: SQLite
haelt die Datei offen und schreibt gelegentlich mitten im Betrieb - eine
zum falschen Zeitpunkt kopierte Datei kann inkonsistent sein. Die
eingebaute Online-Backup-API von SQLite (`Connection.backup()`) kopiert
stattdessen transaktional, waehrend die Quelle weiterlaeuft.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


def backup_database(source: sqlite3.Connection, destination: Path) -> None:
    """Sichert `source` (die offene Verbindung der laufenden App) nach
    `destination` - sicher aufrufbar, waehrend `source` in Benutzung ist."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(destination)) as dest_con:
        source.backup(dest_con)
