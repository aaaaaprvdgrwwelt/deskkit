"""Eigene Icons als SVG - Mechanismus geteilt von allen *desk-Apps.

Icon-Themes gibt es unter Windows und macOS nicht und unter Linux nicht
zuverlaessig. Deshalb werden die paar gebrauchten Symbole selbst gezeichnet.
Sie uebernehmen die Textfarbe der Palette und funktionieren damit in hellen
wie dunklen Themes. Jede App bringt ihre eigene `PATHS`-Tabelle mit
(Strichzeichnungen auf einem 24x24-Raster) und legt sich darauf ein eigenes
`IconSet` an - siehe z. B. moviedesk/icons.py oder comicdesk/icons.py.
"""
from __future__ import annotations

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{color}" stroke-width="1.7" stroke-linecap="round" '
    'stroke-linejoin="round">{body}</svg>'
)


def text_color() -> QColor:
    app = QApplication.instance()
    if app is None:
        return QColor("#303030")
    return app.palette().color(QPalette.WindowText)


class IconSet:
    """Rendert Icons aus einer App-eigenen `paths`-Tabelle (Name -> SVG-Body),
    mit eigenem Cache je (Name, Farbe, Groesse)."""

    def __init__(self, paths: dict[str, str]):
        self.paths = paths
        self._cache: dict[tuple[str, str, int], QIcon] = {}

    def icon(self, name: str, size: int = 24, color: str | None = None) -> QIcon:
        """Icon `name` in Textfarbe. Unbekannte Namen ergeben ein leeres Icon.

        `color` erzwingt eine feste Farbe - fuer Flaechen, die nicht der
        Palette folgen, etwa das dunkle Vollbild-HUD eines Readers.
        """
        body = self.paths.get(name)
        if not body:
            return QIcon()
        color_obj = QColor(color) if color else text_color()
        key = (name, color_obj.name(), size)
        if key in self._cache:
            return self._cache[key]

        svg = TEMPLATE.format(color=color_obj.name(), body=body)
        renderer = QSvgRenderer(QByteArray(svg.encode()))
        result = QIcon()
        for scale in (1, 2):
            pixmap = QPixmap(size * scale, size * scale)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter, QRectF(pixmap.rect()))
            painter.end()
            pixmap.setDevicePixelRatio(scale)
            result.addPixmap(pixmap)
        self._cache[key] = result
        return result
