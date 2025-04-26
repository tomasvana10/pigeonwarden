import os
from pathlib import Path

from . import DETECT_PATH


def get_latest_trained_model() -> Path:
    trained = os.listdir(DETECT_PATH)

    def sort_fn(t: str) -> int:
        part = t.split("train")[1]
        try:
            return int(part)
        except ValueError:
            return 0

    trained.sort(key=sort_fn, reverse=True)

    return DETECT_PATH / trained[0] / "weights" / "best.pt"
