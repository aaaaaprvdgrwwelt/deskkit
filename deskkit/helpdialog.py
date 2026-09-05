"""Hilfe-Dialog-Rahmen - geteilt von allen *desk-Apps.

Der Rahmen (Textbrowser + Schliessen-Knopf, feste Groesse) ist immer
gleich; nur der HTML-Inhalt ist app-eigen, siehe z. B.
moviedesk/helpdialog.py oder comicdesk/helpdialog.py.
"""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout


class HelpDialog(QDialog):
    def __init__(self, html: str, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 640)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(html)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(browser)
        layout.addWidget(buttons)
