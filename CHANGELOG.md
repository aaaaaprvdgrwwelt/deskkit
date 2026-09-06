# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).
Noch kein Release getaggt — alles bislang unter „Unreleased“.

## [Unreleased]

### Added

- `deskkit.i18n` — Sprachumschaltung (aktive Sprache verfolgen,
  Systemsprache erkennen, in einer App-eigenen Tabelle nachschlagen).
- `deskkit.theme` — einheitliches Stylesheet aus der Systempalette.
- `deskkit.icons` — Mechanismus für selbst gezeichnete SVG-Icons.
- `deskkit.appicon` — Programmsymbol aus SVG in alle Pixelgrößen rendern.
- `deskkit.thumbs` — nebenläufiges Laden/Erzeugen von Thumbnails mit Cache.
- `deskkit.cache` — `ResponseCache` für Netzwerkantworten.
- `deskkit.matching` — Titel normalisieren und vergleichen.
- `deskkit.settings` — kleine QSettings-Helfer (`as_bool()`).
- `deskkit.actions` — `ActionRegistry`, eine `QAction` je Befehl für
  Menü/Werkzeugleiste/Kontextmenüs.
- `deskkit.helpdialog` — Rahmen für den Hilfe-Dialog.
- `deskkit.tiles` — `CoverDelegate`/`configure_grid()` für Kachel-Raster.
- `deskkit.widgets` — `RootList` für Ordnerlisten in Einstellungsdialogen.
- `deskkit.secrets` — API-Schlüssel im System-Schlüsselbund statt im
  Klartext in QSettings, mit automatischer Migration vorhandener
  Klartext-Werte.
- `deskkit.paths` — `subfolder_of()`, Grundlage für den gezielten Rescan
  eines einzelnen Films/Albums/Buchs.
- Testsuite (pytest) für `matching`, `cache`, `secrets`, `paths`.
- CI (GitHub Actions): Tests bei jedem Push/PR.

[Unreleased]: https://github.com/aaaaaprvdgrwwelt/deskkit/commits/main
