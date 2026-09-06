# deskkit

[![Tests](https://github.com/aaaaaprvdgrwwelt/deskkit/actions/workflows/tests.yml/badge.svg)](https://github.com/aaaaaprvdgrwwelt/deskkit/actions/workflows/tests.yml)

Gemeinsames Grundgerüst für die `*desk`-Dateimanager — Python + Qt (PySide6):

- [MovieDesk](https://github.com/aaaaaprvdgrwwelt/moviedesk) — Filme und Serien
- [ComicDesk](https://github.com/aaaaaprvdgrwwelt/comicdesk) — Comics
- [BookDesk](https://github.com/aaaaaprvdgrwwelt/bookdesk) — Ebooks (EPUB/PDF)
- [AudioDesk](https://github.com/aaaaaprvdgrwwelt/audiodesk) — Musik und Hörbücher

Kein eigenständiges Programm, sondern eine Bibliothek: Mechanismen, die in
mehreren dieser Apps identisch gebraucht werden, an einer Stelle gepflegt
statt in jeder App neu erfunden oder — schlimmer — leicht unterschiedlich
neu erfunden. Jede App bringt weiterhin ihre eigenen Daten mit (Icon-SVGs,
Übersetzungstabelle, Statusfarben, Provider-Liste); deskkit kennt nur den
Mechanismus dahinter.

## Enthalten

| Modul | Wofür |
|---|---|
| `deskkit.actions` | `ActionRegistry` — eine `QAction` je Befehl, von Menü, Werkzeugleiste und Kontextmenüs gemeinsam benutzt. Ohne das driftet Text/Icon/Tastenkürzel derselben Aktion leicht auseinander oder wird mehrfach neu angelegt. |
| `deskkit.i18n` | Sprachumschaltung: aktive Sprache verfolgen, Systemsprache erkennen, in einer App-eigenen Tabelle nachschlagen. Fehlt ein Eintrag, erscheint der (ASCII-deutsche) Schlüssel selbst — die App bleibt immer benutzbar. |
| `deskkit.theme` | Einheitliches Stylesheet, aus der Systempalette abgeleitet (Abstände, Rundungen, Akzentfarbe) — Farben/Schrift bleiben Systemvorgabe, damit sich die App in helle wie dunkle Themes einfügt. |
| `deskkit.icons` | Selbst gezeichnete SVG-Icons, die die Textfarbe der Palette übernehmen — Icon-Themes gibt es unter Windows/macOS nicht und unter Linux nicht zuverlässig. |
| `deskkit.appicon` | Programmsymbol aus SVG in alle gebrauchten Pixelgrößen rendern und als PNGs im hicolor-Icon-Theme ablegen (`~/.local/share/icons/hicolor/...`). |
| `deskkit.tiles` | `CoverDelegate` + `configure_grid()` — Kachel-Raster für ein `QListWidget` im IconMode (Cover/Poster, Titel, Statusfarb-Balken). |
| `deskkit.widgets` | `RootList` — Ordnerliste mit Hinzufügen/Entfernen für Einstellungsdialoge. |
| `deskkit.helpdialog` | Rahmen für den Hilfe-Dialog (Textbrowser + Schließen-Knopf); nur der HTML-Inhalt ist app-eigen. |
| `deskkit.thumbs` | Nebenläufiges Laden/Erzeugen von Thumbnails mit Speicher-Cache — was geladen wird und wie der Plattencache aussieht, entscheidet die App per Callback. |
| `deskkit.cache` | `ResponseCache` — SQLite-Cache für Netzwerkantworten externer Metadaten-Quellen, mit Ablaufzeit. |
| `deskkit.matching` | `normalize_title()`/`title_similarity()` — Titel vergleichbar machen (Artikel/Satzzeichen raus) und ihre Ähnlichkeit bewerten, für den Abgleich Dateiname ↔ Online-Quelle. |
| `deskkit.secrets` | `get_secret()`/`set_secret()` — API-Schlüssel/Tokens im System-Schlüsselbund (Windows Credential Locker, macOS Schlüsselbund, Linux Secret Service/KWallet) statt im Klartext in QSettings, mit automatischer Migration vorhandener Klartext-Werte und Rückfall auf QSettings ohne verfügbaren Schlüsselbund. |
| `deskkit.paths` | `subfolder_of()` — der direkte Unterordner eines Wurzelverzeichnisses, der einen Pfad enthält; Grundlage für den gezielten Rescan eines einzelnen Films/Albums/Buchs statt des ganzen Wurzelordners. |
| `deskkit.settings` | Kleine QSettings-Helfer (`as_bool()` — liefert je nach Backend mal einen echten `bool`, mal den String `"true"`/`"false"`). |

## Einbinden

Noch kein eigenes PyPI-Paket — `deskkit` liegt als Geschwister-Verzeichnis
neben den Apps und wird per `-e ../deskkit` in deren `requirements.txt`
eingebunden:

```
project/
├── deskkit/     ← dieses Repo
├── moviedesk/
├── comicdesk/
├── bookdesk/
└── audiodesk/
```

```bash
git clone https://github.com/aaaaaprvdgrwwelt/deskkit.git
git clone https://github.com/aaaaaprvdgrwwelt/moviedesk.git
cd moviedesk
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # zieht deskkit editable mit
```

Eine Änderung an deskkit wirkt sich damit sofort auf alle Apps aus, die im
selben venv laufen — kein erneutes Installieren nötig.

## Entwickeln

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```

Die Tests laufen unter `QT_QPA_PLATFORM=offscreen` (kein Display nötig,
so auch in der CI). `deskkit.secrets` wird ohne echten Systemschlüsselbund
getestet, indem `deskkit.secrets.available()`/`deskkit.secrets.keyring`
gemockt werden — kein Zugriff auf den echten Schlüsselbund des
Testrechners.

## Neue Funktion ergänzen

Bevor etwas hierher wandert: Es muss **identisch** von mindestens zwei Apps
gebraucht werden, nicht nur ähnlich. `metapanel.py` (Metadaten-Seitenpanel)
und `matcher.py`/`matchdialog.py` (Bewertungslogik) unterscheiden sich
zwischen den Apps zum Beispiel gerade so viel, dass eine gemeinsame
Abstraktion mehr Bedingungslogik als Ersparnis bedeuten würde — die bleiben
deshalb bewusst app-eigen.

## Lizenz

[MIT](LICENSE). Verwendet [PySide6](https://doc.qt.io/qtforpython/) (LGPL)
und [keyring](https://github.com/jaraco/keyring) (MIT).
