import os
import re
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from ultralytics import YOLO

from .common import DETECT_PATH

TEMPERATURE_REGEX = re.compile(r"(\d+\.\d+)'([CF])")


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self, db_path="config.db"):
        self.db_path = db_path
        self.lock = Lock()
        self._init_db()

    def _init_db(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)"
            )

    def read(self, key: str, default=None) -> str | None:
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def write(self, key: str, value: str) -> None:
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def read_all(self) -> dict:
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT key, value FROM config")
            return {row[0]: row[1] for row in cur.fetchall()}


def get_latest_trained_model(source_ncnn=True) -> Path:
    assert Path(DETECT_PATH).exists(), (
        "You must run pigeonwarden with the `train` parameter first."
    )

    trained = os.listdir(DETECT_PATH)

    def sort_fn(t: str) -> int:
        part = t.split("train")[1]
        try:
            return int(part)
        except ValueError:
            return 0

    trained.sort(key=sort_fn, reverse=True)

    model = "best_ncnn_model" if source_ncnn else "best.pt"

    return DETECT_PATH / trained[0] / "weights" / model


def export_ncnn():
    if get_latest_trained_model().exists():
        raise Exception("NCNN Model already exported")

    model = YOLO(get_latest_trained_model(source_ncnn=False))
    model.export(format="ncnn")


def get_timestamp() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def get_cpu_temp() -> dict[str, float | str]:
    output = subprocess.Popen(
        ["vcgencmd", "measure_temp"], stdout=subprocess.PIPE
    ).communicate()[0]
    results = re.findall(TEMPERATURE_REGEX, output.decode())[0]

    return dict(temp=float(results[0]), unit=results[1])
