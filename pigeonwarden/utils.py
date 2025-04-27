import os
from pathlib import Path
import socket as s

from .constants import DETECT_PATH


def get_latest_trained_model() -> Path:
    assert Path(DETECT_PATH).exists(), "Please train the model before testing."
    
    trained = os.listdir(DETECT_PATH)

    def sort_fn(t: str) -> int:
        part = t.split("train")[1]
        try:
            return int(part)
        except ValueError:
            return 0

    trained.sort(key=sort_fn, reverse=True)

    return DETECT_PATH / trained[0] / "weights" / "best.pt"


def is_port_in_use(port: int) -> bool:
    with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def get_available_port() -> int:
    sock = s.socket()
    sock.bind(("", 0))
    port: int = sock.getsockname()[1]
    return port
