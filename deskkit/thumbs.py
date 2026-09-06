"""Nebenlaeufiges Laden/Erzeugen von Thumbnails, mit Speicher-Cache und
Fertig-Signal - Mechanismus geteilt von allen *desk-Apps (Threadpool,
Warteschlange, Cache). Was genau geladen wird - von einer URL, aus einer
Datei - und wie ein Cache auf der Platte funktioniert, entscheidet die App
per `load`-Callback, siehe z. B. moviedesk/thumbs.py oder comicdesk/thumbs.py.
"""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QImage, QPixmap


class _Signals(QObject):
    done = Signal(str, QImage)


class _Job(QRunnable):
    def __init__(self, key: str, load: Callable[[str], QImage], signals: _Signals):
        super().__init__()
        self.key = key
        self.load = load
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            img = self.load(self.key)
        except Exception:  # noqa: BLE001
            img = QImage()
        self.signals.done.emit(self.key, img)


class ThumbLoader(QObject):
    """`load(key) -> QImage` macht die eigentliche Arbeit: von der Platte
    lesen, aus dem eigenen Cache, sonst laden/erzeugen und dort ablegen.
    Schluessel sind hier immer Strings - eine App, die mit `Path`-Objekten
    arbeitet, wandelt beim Aufruf um (siehe `ThumbLoader.get`/`forget` in
    comicdesk/thumbs.py)."""

    ready = Signal(str, QPixmap)

    def __init__(self, load: Callable[[str], QImage], parent=None):
        super().__init__(parent)
        self._load = load
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(
            max(2, QThreadPool.globalInstance().maxThreadCount() - 1))
        self._signals = _Signals(self)
        self._signals.done.connect(self._on_done)
        self._pending: set[str] = set()
        self._cache: dict[str, QPixmap] = {}

    def get(self, key: str) -> QPixmap | None:
        if key in self._cache:
            return self._cache[key]
        if key not in self._pending:
            self._pending.add(key)
            self._pool.start(_Job(key, self._load, self._signals))
        return None

    def forget(self, key: str) -> None:
        """Zwischenspeicher fuer `key` verwerfen - er hat sich geaendert."""
        self._cache.pop(key, None)
        self._pending.discard(key)

    def clear_queue(self) -> None:
        self._pool.clear()
        self._pending.clear()

    def _on_done(self, key: str, img: QImage) -> None:
        self._pending.discard(key)
        pm = QPixmap.fromImage(img) if not img.isNull() else QPixmap()
        self._cache[key] = pm
        self.ready.emit(key, pm)
