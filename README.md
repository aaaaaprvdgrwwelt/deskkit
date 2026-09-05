# deskkit

Gemeinsames Grundgerüst für die `*desk`-Apps ([moviedesk](https://github.com/aaaaaprvdgrwwelt/moviedesk),
[comicdesk](https://github.com/aaaaaprvdgrwwelt/comicdesk), künftig weitere für
Bücher/Audio) — Python + Qt (PySide6).

Kein eigenständiges Programm, sondern eine Bibliothek: Bausteine, die in
mehreren dieser Dateimanager identisch gebraucht werden, an einer Stelle
gepflegt statt in jeder App neu erfunden.

## Enthalten

- **`deskkit.i18n`** — Sprachumschaltungs-Mechanismus (aktive Sprache
  verfolgen, Systemsprache erkennen, in einer App-eigenen Tabelle
  nachschlagen). Jede App bringt ihre eigene Übersetzungstabelle mit, siehe
  `moviedesk/i18n.py` bzw. `comicdesk/i18n.py` als Beispiel.

Weitere Kandidaten (noch nicht extrahiert): Theming, Icon-Rendering,
Poster/Cover-Laden, das Metadaten-Seitenpanel, das Provider-Muster für
Metadaten-Quellen.

## Einbinden

Noch kein eigenes PyPI-Paket — `deskkit` liegt als Sibling-Verzeichnis neben
den Apps und wird per `-e ../deskkit` in `requirements.txt` eingebunden.
