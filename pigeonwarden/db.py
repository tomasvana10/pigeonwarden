from threading import Lock
from typing import TypedDict, Optional

import redis

from .utils import Singleton, resolve_redis_uri_components


class DBTable(TypedDict):
    cron_days: str
    cron_start_time: str
    cron_end_time: str


class DB(metaclass=Singleton):
    DEFAULTS = DBTable(
        cron_days="0123456", cron_start_time="07:00", cron_end_time="20:00"
    )

    def __init__(self):
        self._lock = Lock()
        components = resolve_redis_uri_components()
        self._redis = redis.Redis(
            host=components["host"],
            port=components["port"],
            decode_responses=True,
        )
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        for key, default_val in self.DEFAULTS.items():
            if self.read(key) is None:
                self.write(key, default_val)  # type: ignore

    def read(self, key: str, default=None) -> Optional[str]:
        with self._lock:
            return self._redis.get(key)

    def write(self, key: str, value: str) -> None:
        with self._lock:
            self._redis.set(key, value)

    def read_all(self) -> DBTable:
        with self._lock:
            return {key: self._redis.get(key) for key in self.DEFAULTS}  # type: ignore
