"""Eine Quelle der Wahrheit fuer Qt-Actions - geteilt von allen *desk-Apps.

Menue, Werkzeugleiste und Kontextmenues sollen fuer dieselbe Aktion (z. B.
"Loeschen") denselben Text, dasselbe Icon und dasselbe Tastenkuerzel zeigen.
Ohne gemeinsame Stelle driftet das leicht auseinander oder wird mehrfach neu
angelegt - `ActionRegistry` haelt eine `QAction` je Schluessel, die ueberall
wiederverwendet wird.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QWidget


class ActionRegistry:
    def __init__(self, window: QWidget, translate: Callable[[str], str]):
        self.window = window
        self.translate = translate
        self._actions: dict[str, QAction] = {}

    def add(self, key: str, text: str, shortcut: str | None = None,
           slot: Callable[[], None] | None = None, icon: QIcon | None = None,
           target: QWidget | None = None,
           shortcut_context: Qt.ShortcutContext = Qt.WindowShortcut) -> QAction:
        """Legt eine `QAction` an, registriert sie unter `key` und haengt sie
        an `target` (Standard: das Fenster selbst). `target` + engerer
        `shortcut_context` binden ein Tastenkuerzel an ein bestimmtes Widget -
        z. B. `Entf` nur im Dateibereich, damit es in einem Textfeld normal
        loescht statt eine Auswahl zu entfernen."""
        action = QAction(self.translate(text), self.window)
        if icon is not None:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
            action.setShortcutContext(shortcut_context)
        if slot is not None:
            action.triggered.connect(slot)
        (target or self.window).addAction(action)
        self._actions[key] = action
        return action

    def __getitem__(self, key: str) -> QAction:
        return self._actions[key]

    def __contains__(self, key: str) -> bool:
        return key in self._actions

    def get(self, key: str, default=None):
        return self._actions.get(key, default)

    def values(self):
        return self._actions.values()
