"""Programmsymbol - Mechanismus geteilt von allen *desk-Apps.

Jede App bringt ihre eigene(n) SVG-Datei(en) mit und eine Zuordnung
Pixelgroesse -> SVG-Datei dafuer (meist dieselbe Datei fuer alle Groessen;
eine App mit zwei Zeichnungen - z. B. einer vereinfachten fuer kleine
Groessen, weil Details unter ~32px zu Brei zerfallen - traegt fuer die
kleinen Groessen einfach eine andere Datei ein). Qt waehlt anhand der
eingebetteten Groessen selbst die passende Pixmap aus.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon


def build_icon(size_to_svg: dict[int, Path]) -> QIcon:
    """Ein QIcon mit einer Pixmap je (Groesse, zugehoerige SVG-Datei)."""
    result = QIcon()
    cache: dict[Path, QIcon] = {}
    for size, svg in size_to_svg.items():
        source = cache.setdefault(svg, QIcon(str(svg)))
        result.addPixmap(source.pixmap(size, size))
    return result


def index_theme(sizes: tuple[int, ...]) -> str:
    """Ohne index.theme ist der Ordner kein gueltiges Icon-Thema - dann findet
    der Compositor das Symbol nicht, egal wie viele PNGs darin liegen."""
    folders = [f"{size}x{size}/apps" for size in sizes] + ["scalable/apps"]
    lines = ["[Icon Theme]", "Name=Hicolor", "Comment=Fallback icon theme",
             "Hidden=true", "Directories=" + ",".join(folders), ""]
    for size in sizes:
        lines += [f"[{size}x{size}/apps]", f"Size={size}",
                  "Context=Applications", "Type=Fixed", ""]
    lines += ["[scalable/apps]", "Size=48", "MinSize=8", "MaxSize=512",
              "Context=Applications", "Type=Scalable", ""]
    return "\n".join(lines)


def install(size_to_svg: dict[int, Path], name: str, scalable_svg: Path,
           target: Path | None = None) -> list[Path]:
    """PNGs (+ das Scalable-SVG) ins Icon-Thema legen, damit Menue und
    Fensterleiste sie finden. `name` ist der Dateiname ohne Endung (z. B.
    "moviedesk" -> moviedesk.png/.svg)."""
    base = target or (Path.home() / ".local" / "share" / "icons" / "hicolor")
    written: list[Path] = []
    cache: dict[Path, QIcon] = {}
    for size, svg in size_to_svg.items():
        source = cache.setdefault(svg, QIcon(str(svg)))
        folder = base / f"{size}x{size}" / "apps"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}.png"
        source.pixmap(size, size).save(str(path), "PNG")
        written.append(path)

    scalable = base / "scalable" / "apps"
    scalable.mkdir(parents=True, exist_ok=True)
    target_svg = scalable / f"{name}.svg"
    target_svg.write_bytes(scalable_svg.read_bytes())
    written.append(target_svg)

    index = base / "index.theme"
    index.write_text(index_theme(tuple(size_to_svg.keys())), "utf-8")
    written.append(index)
    return written
