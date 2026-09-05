import time

from deskkit.cache import ResponseCache


def test_put_and_get_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache = ResponseCache("desktest", "cache.sqlite", ttl_days=1)
    cache.put("key1", {"title": "Matrix", "year": 1999})
    assert cache.get("key1") == {"title": "Matrix", "year": 1999}


def test_get_missing_key_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache = ResponseCache("desktest", "cache.sqlite", ttl_days=1)
    assert cache.get("missing") is None


def test_expired_entry_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache = ResponseCache("desktest", "cache.sqlite", ttl_days=1)
    cache.put("key1", {"a": 1})
    # Zeit direkt in der Tabelle zurueckdrehen statt Sekunden zu warten.
    with cache._lock:
        cache._con.execute(
            "UPDATE cache SET ts=? WHERE key=?", (time.time() - 999999, "key1"))
        cache._con.commit()
    assert cache.get("key1") is None


def test_put_overwrites_existing_key(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache = ResponseCache("desktest", "cache.sqlite", ttl_days=1)
    cache.put("key1", {"v": 1})
    cache.put("key1", {"v": 2})
    assert cache.get("key1") == {"v": 2}
