"""Kleine, wiederverwendbare Widgets fuer Einstellungsdialoge - geteilt von
allen *desk-Apps.
"""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QListWidget, QPushButton, QVBoxLayout, QWidget,
)


class RootList(QWidget):
    """Ordnerliste mit Hinzufuegen/Entfernen - fuer eine Bibliotheks-Wurzel
    (Filme-/Serien-/Ebook-/Musik-Ordner o. ae.).

    `add_label`/`remove_label`/`choose_title` kommen von der App, damit die
    Beschriftung uebersetzt ist (siehe `deskkit.i18n.Translator`), ohne dass
    dieses Modul selbst eine Sprache kennen muss.
    """

    def __init__(self, roots: list[str], translate: Callable[[str], str],
                parent=None):
        super().__init__(parent)
        self._translate = translate
        self.list = QListWidget()
        self.list.addItems(roots)

        add_button = QPushButton(translate("Ordner hinzufuegen …"))
        add_button.clicked.connect(self._add)
        remove_button = QPushButton(translate("Entfernen"))
        remove_button.clicked.connect(self._remove)

        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(remove_button)
        buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list)
        layout.addLayout(buttons)

    def _add(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, self._translate("Ordner waehlen"))
        if folder:
            self.list.addItem(folder)

    def _remove(self) -> None:
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def roots(self) -> list[str]:
        return [self.list.item(i).text() for i in range(self.list.count())]
