"""Antwort-Cache fuer Netz-Quellen: spart Kontingent und macht schnell -
Mechanismus geteilt von allen *desk-Apps. Jedes hat sein eigenes
Cache-Verzeichnis unter `~/.cache/<app_name>/...`, siehe z. B.
moviedesk/providers/cache.py oder comicdesk/providers/cache.py.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path


def cache_dir(app_name: str) -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    path = Path(base) / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path


class ResponseCache:
    def __init__(self, app_name: str, name: str, ttl_days: int = 14):
        self.ttl = ttl_days * 86400
        self._con = sqlite3.connect(
            str(cache_dir(app_name) / name), check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            self._con.execute(
                "CREATE TABLE IF NOT EXISTS cache "
                "(key TEXT PRIMARY KEY, ts REAL, body TEXT)")
            self._con.commit()

    def get(self, key: str):
        with self._lock:
            row = self._con.execute(
                "SELECT ts, body FROM cache WHERE key=?", (key,)).fetchone()
        if not row or time.time() - row[0] > self.ttl:
            return None
        try:
            return json.loads(row[1])
        except json.JSONDecodeError:
            return None

    def put(self, key: str, value) -> None:
        with self._lock:
            self._con.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?)",
                              (key, time.time(), json.dumps(value)))
            self._con.commit()
