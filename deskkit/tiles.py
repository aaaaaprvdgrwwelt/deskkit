"""Kachel-Raster fuer ein `QListWidget` im IconMode: Cover/Poster oben,
Titel (+ optionale Unterzeile) darunter, ein Statusfarb-Balken am unteren
Cover-Rand. Geteilter Mechanismus zwischen allen *desk-Apps - Groessen und
welche Statuswerte welche Farbe bekommen, bringt jede App selbst mit
(siehe z. B. moviedesk/mainwindow.py oder bookdesk/mainwindow.py).

Qt's eingebautes IconMode-Raster kommt mit unterschiedlichen
Cover-Seitenverhaeltnissen nicht zurecht (falsch skaliert/zerhackt) -
deshalb wird hier selbst gezeichnet.
"""
from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QListWidget, QStyle, QStyledItemDelegate

#: Zweite Kachel-Zeile (Jahr, Interpret, Episodenzahl o. ae.).
SUBTITLE_ROLE = Qt.UserRole + 1
#: Steuert die Statusfarbe der Kachel (Schluessel in `status_colors`).
STATUS_ROLE = Qt.UserRole + 2


def _wrap_lines(text: str, fm, width: int, max_lines: int) -> list[str]:
    """Woerter zeilenweise auffuellen; ueberschuessiger Rest wird eliert."""
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = ""
    index = 0
    while index < len(words) and len(lines) < max_lines:
        candidate = f"{current} {words[index]}".strip()
        if fm.horizontalAdvance(candidate) <= width or not current:
            current = candidate
            index += 1
        else:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    if index < len(words) and lines:
        rest = " ".join(words[index:])
        lines[-1] = fm.elidedText(f"{lines[-1]} {rest}", Qt.ElideRight, width)
    return lines[:max_lines]


def _subtle_color(option) -> QColor:
    text = option.palette.text().color()
    window = option.palette.window().color()
    return QColor(
        round((text.red() + window.red()) / 2),
        round((text.green() + window.green()) / 2),
        round((text.blue() + window.blue()) / 2))


class CoverDelegate(QStyledItemDelegate):
    """Zeichnet eine Kachel. `status_colors` bildet einen `STATUS_ROLE`-Wert
    (z. B. "matched") auf eine `QColor` ab - Werte ohne Eintrag bleiben ohne
    Farbbalken."""

    def __init__(self, status_colors: dict[str, QColor], tile_w: int = 140,
                cover_h: int = 190, pad: int = 8, text_lines: int = 2,
                parent=None):
        super().__init__(parent)
        self.status_colors = status_colors
        self.tile_w = tile_w
        self.cover_h = cover_h
        self.pad = pad
        self.text_lines = text_lines

    def sizeHint(self, option, index):  # noqa: N802
        fm = option.fontMetrics
        lines = self.text_lines + (1 if index.data(SUBTITLE_ROLE) else 0)
        return QSize(self.tile_w, self.cover_h + lines * fm.height() + 3 * self.pad)

    def paint(self, painter: QPainter, option, index) -> None:  # noqa: N802
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = option.rect.adjusted(3, 3, -3, -3)
        selected = bool(option.state & QStyle.State_Selected)
        hovered = bool(option.state & QStyle.State_MouseOver)

        if selected or hovered:
            color = option.palette.highlight().color()
            if not selected:
                color.setAlpha(60)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 6, 6)

        pad = self.pad
        cover_rect = QRect(rect.left() + pad, rect.top() + pad,
                           rect.width() - 2 * pad, self.cover_h)
        icon = index.data(Qt.DecorationRole)
        pm = QPixmap()
        if isinstance(icon, QIcon):
            avail = icon.availableSizes()
            pm = icon.pixmap(avail[0] if avail else QSize(160, 220))
        if not pm.isNull():
            target = pm.size().scaled(cover_rect.size(), Qt.KeepAspectRatio)
            x = cover_rect.left() + (cover_rect.width() - target.width()) // 2
            y = cover_rect.top() + (cover_rect.height() - target.height())
            dest = QRect(x, y, target.width(), target.height())
            painter.setPen(QPen(QColor(0, 0, 0, 60)))
            painter.setBrush(Qt.NoBrush)
            painter.drawPixmap(dest, pm)
            painter.drawRect(dest.adjusted(0, 0, -1, -1))
        else:
            painter.setPen(QPen(option.palette.mid().color()))
            painter.setBrush(option.palette.base())
            painter.drawRoundedRect(cover_rect, 4, 4)

        status = index.data(STATUS_ROLE)
        color = self.status_colors.get(status)
        if color:
            bar = QRect(cover_rect.left(), cover_rect.bottom() - 5,
                       cover_rect.width(), 5)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(bar)

        fm = option.fontMetrics
        font = QFont(option.font)
        painter.setFont(font)
        painter.setPen(option.palette.highlightedText().color() if selected
                       else option.palette.text().color())
        text_top = cover_rect.bottom() + pad
        text_rect = QRect(rect.left() + 4, text_top, rect.width() - 8,
                          self.text_lines * fm.height())
        title = index.data(Qt.DisplayRole) or ""
        for i, line in enumerate(_wrap_lines(title, fm, text_rect.width(), self.text_lines)):
            painter.drawText(text_rect.left(), text_rect.top() + (i + 1) * fm.height()
                             - fm.descent(), line)
        subtitle = index.data(SUBTITLE_ROLE)
        if subtitle:
            painter.setPen(_subtle_color(option))
            y = text_rect.bottom() + fm.height() - fm.descent()
            painter.drawText(text_rect.left(), y, subtitle)
        painter.restore()


def configure_grid(widget: QListWidget, delegate: CoverDelegate) -> None:
    """Ein `QListWidget` fuers Kachel-Raster einrichten und `delegate`
    einhaengen."""
    widget.setViewMode(QListWidget.IconMode)
    widget.setResizeMode(QListWidget.Adjust)
    widget.setMovement(QListWidget.Static)
    widget.setSpacing(10)
    widget.setUniformItemSizes(False)
    widget.setSelectionMode(QListWidget.ExtendedSelection)
    widget.setItemDelegate(delegate)
