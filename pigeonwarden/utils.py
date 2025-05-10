import os
import socket as s
from datetime import datetime
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from .constants import DETECT_PATH


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


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


def is_port_in_use(port: int) -> bool:
    with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def get_available_port() -> int:
    sock = s.socket()
    sock.bind(("", 0))
    port: int = sock.getsockname()[1]
    return port

def get_timestamp() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")