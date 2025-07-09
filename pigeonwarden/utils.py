import os
import time
import socket
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict, Callable
from functools import wraps

from dotenv import load_dotenv
from ultralytics import YOLO

from .common import DETECT_PATH, WARDEN_SETTINGS_PATH


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

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


def export_ncnn() -> None:
    if get_latest_trained_model().exists():
        raise Exception("NCNN Model already exported")

    model = YOLO(get_latest_trained_model(source_ncnn=False))
    model.export(format="ncnn")


def get_timestamp() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class WardenSettings(TypedDict):
    min_confidence: float
    labels: list[str]
    sound: str
    volume: int
    alert_cooldown_seconds: int
    fps: int
    telegram_alerts: bool


def get_warden_settings() -> WardenSettings:
    with open(WARDEN_SETTINGS_PATH, "rb") as f:
        data = tomllib.load(f)

    config = data.get("default", {}).copy()
    config.update(data.get("user-override", {}))

    return WardenSettings(**config)  # type: ignore


def resolve_redis_uri_components() -> dict[str, int | str]:
    load_dotenv()

    components: dict[str, int | str] = {}
    components["host"] = (
        get_device_ip() if int(os.getenv("USE_IP_FOR_REDIS_URI", 0)) else "localhost"
    )
    components["port"] = int(os.getenv("REDIS_PORT", 6379))

    return components


def get_device_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("1.1.1.1", 80))
        return s.getsockname()[0]


def cooldown(seconds: int, /, *, if_cooldown_return: Any = None) -> Callable:
    last_called: dict[tuple[Callable, tuple[Any, ...]], float] = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            key = (func, args)
            if key in last_called and now - last_called[key] < seconds:
                return if_cooldown_return
            last_called[key] = now
            return func(*args, **kwargs)

        return wrapper

    return decorator
