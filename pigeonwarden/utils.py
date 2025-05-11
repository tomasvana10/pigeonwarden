import os
import socket as s
import re
import json
import subprocess
from threading import Lock
from datetime import datetime
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from .common import DETECT_PATH


TEMPERATURE_REGEX = re.compile(r"(\d+\.\d+)'([CF])")


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Dict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class JSON:
    DEFAULTS = {
        "config.json": {
            "cron_days": "0123456",
            "cron_start_time": "07:00",
            "cron_end_time": "20:00"
        }
    }
    
    lock = Lock()
    
    @staticmethod
    def _read(val: Any | Dict) -> Dict | list[Dict]:
        if isinstance(val, dict):
            return Dict({k: JSON._read(v) for k, v in val.items()})
        if isinstance(val, list):
            return [JSON._read(v) for v in val]
        return val

    @staticmethod
    def read(file: str) -> Dict:
        with JSON.lock:
            try:
                with open(file, "r") as f:
                    return JSON._read(json.load(f))
            except FileNotFoundError:
                JSON.write(JSON.DEFAULTS[file], file)
                return JSON.read(file)

    @staticmethod
    def write(obj: Any, file: str) -> None:
        with JSON.lock:
            with open(file, "w") as f:
                json.dump(obj, f)
    

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


def get_cpu_temp() -> dict[str, float | str]:
    output = subprocess.Popen(["vcgencmd", "measure_temp"], stdout=subprocess.PIPE).communicate()[0]
    results = re.findall(TEMPERATURE_REGEX, output.decode())[0]

    return dict(temp=float(results[0]), unit=results[1])
