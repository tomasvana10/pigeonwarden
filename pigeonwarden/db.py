import sqlite3
from threading import Lock
from typing import TypedDict

from . import Singleton


class DBTable(TypedDict):
    cron_days: str
    cron_start_time: str
    cron_end_time: str


class DB(metaclass=Singleton):
    DEFAULTS: DBTable = {
        "cron_days": "0123456",
        "cron_start_time": "07:00",
        "cron_end_time": "20:00",
    }

    def __init__(self, db_path="config.db"):
        self.db_path = db_path
        self.lock = Lock()
        self._init_db()
        self._ensure_defaults()

    def _init_db(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)"
            )

    def _ensure_defaults(self):
        existing = self.read_all()
        for key, default_val in self.DEFAULTS.items():
            if key not in existing:
                self.write(key, default_val)

    def read(self, key: str, default=None) -> str | None:
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def write(self, key: str, value: str) -> None:
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def read_all(self) -> DBTable:
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT key, value FROM config")
            data = {row[0]: row[1] for row in cur.fetchall()}

        return {**self.DEFAULTS, **data}