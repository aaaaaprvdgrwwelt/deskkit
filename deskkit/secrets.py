"""API-Schluessel/Tokens/Passwoerter im System-Schluesselbund statt im
Klartext in QSettings - geteilt von allen *desk-Apps, die eine externe
Quelle mit Zugangsdaten ansprechen (TMDb-Key bei moviedesk, ComicVine-Key
bei comicdesk, Discogs-Token bei audiodesk, ...).

Nutzt das `keyring`-Paket (Windows Credential Locker, macOS Schluesselbund,
Linux Secret Service/KWallet). Ohne verfuegbaren Schluesselbund - z. B. per
SSH auf einem Linux-Server ohne grafische Sitzung - faellt es auf den
bisherigen Klartext in QSettings zurueck; das ist kein Rueckschritt
gegenueber vorher, nur eben auch keine Verbesserung in dem Fall.
"""
from __future__ import annotations

from PySide6.QtCore import QSettings

try:
    import keyring
    import keyring.errors
    _KEYRING_IMPORTED = True
except Exception:  # noqa: BLE001
    _KEYRING_IMPORTED = False


def available() -> bool:
    """Ob ein echter Schluesselbund-Backend bereitsteht (nicht nur die
    eingebaute "fail"-Ersatzimplementierung, die jeden Zugriff ablehnt)."""
    if not _KEYRING_IMPORTED:
        return False
    try:
        backend = keyring.get_keyring()
    except Exception:  # noqa: BLE001
        return False
    return type(backend).__module__ != "keyring.backends.fail"


def get_secret(settings: QSettings, service: str, field: str) -> str:
    """Liest ein Geheimnis - bevorzugt aus dem Schluesselbund. Liegt dort
    noch nichts, aber ein alter Klartext-Wert in QSettings (Migration von
    vor dieser Umstellung), wird der uebernommen und gleich in den
    Schluesselbund verschoben."""
    if not available():
        return settings.value(field, "") or ""
    try:
        value = keyring.get_password(service, field)
    except Exception:  # noqa: BLE001
        value = None
    if value:
        return value
    legacy = settings.value(field, "") or ""
    if legacy:
        set_secret(settings, service, field, legacy)
    return legacy


def set_secret(settings: QSettings, service: str, field: str, value: str) -> None:
    """Schreibt ein Geheimnis. Bei verfuegbarem Schluesselbund landet es
    dort und ein evtl. vorhandener Klartext-Wert in QSettings wird entfernt -
    nie beides gleichzeitig halten. Ohne Schluesselbund wie bisher in
    QSettings (Klartext, unveraendertes Verhalten)."""
    value = (value or "").strip()
    if not available():
        settings.setValue(field, value)
        return
    try:
        if value:
            keyring.set_password(service, field, value)
        else:
            try:
                keyring.delete_password(service, field)
            except keyring.errors.PasswordDeleteError:
                pass
    except Exception:  # noqa: BLE001
        # Schluesselbund meldete sich als verfuegbar, scheiterte dann aber
        # doch (z. B. gesperrt) - lieber den Wert behalten als verlieren.
        settings.setValue(field, value)
        return
    settings.remove(field)
