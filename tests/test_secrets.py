from unittest.mock import MagicMock, patch

from PySide6.QtCore import QSettings

from deskkit import secrets


def make_settings(tmp_path) -> QSettings:
    return QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)


def test_available_false_without_keyring_module():
    with patch.object(secrets, "_KEYRING_IMPORTED", False):
        assert secrets.available() is False


def test_available_false_for_fail_backend():
    fail_backend = MagicMock()
    type(fail_backend).__module__ = "keyring.backends.fail"
    with patch.object(secrets, "_KEYRING_IMPORTED", True), \
         patch.object(secrets, "keyring") as mock_keyring:
        mock_keyring.get_keyring.return_value = fail_backend
        assert secrets.available() is False


def test_available_true_for_real_backend():
    real_backend = MagicMock()
    type(real_backend).__module__ = "keyring.backends.SecretService"
    with patch.object(secrets, "_KEYRING_IMPORTED", True), \
         patch.object(secrets, "keyring") as mock_keyring:
        mock_keyring.get_keyring.return_value = real_backend
        assert secrets.available() is True


def test_get_secret_without_keyring_reads_plaintext_from_qsettings(tmp_path):
    settings = make_settings(tmp_path)
    settings.beginGroup("app")
    settings.setValue("api_key", "plain-value")
    settings.endGroup()
    with patch.object(secrets, "available", return_value=False):
        settings.beginGroup("app")
        value = secrets.get_secret(settings, "app", "api_key")
        settings.endGroup()
    assert value == "plain-value"


def test_set_secret_without_keyring_writes_plaintext_to_qsettings(tmp_path):
    settings = make_settings(tmp_path)
    with patch.object(secrets, "available", return_value=False):
        settings.beginGroup("app")
        secrets.set_secret(settings, "app", "api_key", "my-secret")
        settings.endGroup()
    settings.beginGroup("app")
    stored = settings.value("api_key")
    settings.endGroup()
    assert stored == "my-secret"


def test_get_secret_prefers_keyring_value(tmp_path):
    settings = make_settings(tmp_path)
    with patch.object(secrets, "available", return_value=True), \
         patch.object(secrets, "keyring") as mock_keyring:
        mock_keyring.get_password.return_value = "from-keyring"
        settings.beginGroup("app")
        value = secrets.get_secret(settings, "app", "api_key")
        settings.endGroup()
    assert value == "from-keyring"
    mock_keyring.get_password.assert_called_once_with("app", "api_key")


def test_get_secret_migrates_legacy_plaintext_into_keyring(tmp_path):
    settings = make_settings(tmp_path)
    settings.beginGroup("app")
    settings.setValue("api_key", "legacy-plaintext")
    settings.endGroup()
    with patch.object(secrets, "available", return_value=True), \
         patch.object(secrets, "keyring") as mock_keyring:
        mock_keyring.get_password.return_value = None
        settings.beginGroup("app")
        value = secrets.get_secret(settings, "app", "api_key")
        settings.endGroup()
        # Migration ruft set_secret auf, das seinerseits keyring.set_password nutzt.
        mock_keyring.set_password.assert_called_once_with(
            "app", "api_key", "legacy-plaintext")
    assert value == "legacy-plaintext"
    settings.beginGroup("app")
    remaining = settings.value("api_key")
    settings.endGroup()
    assert remaining is None  # aus QSettings entfernt, liegt jetzt im Schluesselbund


def test_set_secret_with_keyring_removes_qsettings_plaintext(tmp_path):
    settings = make_settings(tmp_path)
    settings.beginGroup("app")
    settings.setValue("api_key", "old-plaintext")
    settings.endGroup()
    with patch.object(secrets, "available", return_value=True), \
         patch.object(secrets, "keyring") as mock_keyring:
        settings.beginGroup("app")
        secrets.set_secret(settings, "app", "api_key", "new-secret")
        settings.endGroup()
    mock_keyring.set_password.assert_called_once_with("app", "api_key", "new-secret")
    settings.beginGroup("app")
    remaining = settings.value("api_key")
    settings.endGroup()
    assert remaining is None


def test_set_secret_empty_value_deletes_keyring_entry(tmp_path):
    settings = make_settings(tmp_path)
    with patch.object(secrets, "available", return_value=True), \
         patch.object(secrets, "keyring") as mock_keyring:
        settings.beginGroup("app")
        secrets.set_secret(settings, "app", "api_key", "")
        settings.endGroup()
    mock_keyring.delete_password.assert_called_once_with("app", "api_key")
    mock_keyring.set_password.assert_not_called()


def test_set_secret_falls_back_to_qsettings_if_keyring_raises(tmp_path):
    settings = make_settings(tmp_path)
    with patch.object(secrets, "available", return_value=True), \
         patch.object(secrets, "keyring") as mock_keyring:
        mock_keyring.set_password.side_effect = RuntimeError("locked")
        settings.beginGroup("app")
        secrets.set_secret(settings, "app", "api_key", "value")
        settings.endGroup()
    settings.beginGroup("app")
    stored = settings.value("api_key")
    settings.endGroup()
    assert stored == "value"
