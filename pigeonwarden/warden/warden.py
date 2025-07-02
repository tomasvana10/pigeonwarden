import asyncio
import os
import time
from threading import Lock, Thread
from typing import Optional

import cv2
from dotenv import load_dotenv
from picamera2 import Picamera2
from telegram import Bot
from ultralytics import YOLO

from .. import ASSETS_PATH, BASE_PATH, Singleton, get_timestamp
from ..utils import get_latest_trained_model
from .speaker import play_sound


class Warden(metaclass=Singleton):
    FRAME_ENCODING = ".jpg"
    ENV = ".env.local"
    AVERAGE_INFERENCE_TIME = 0.2

    min_confidence = 0.8
    labels = ["common-mynas", "pigeons"]
    sound = "airhorn.mp3"
    volume = 150
    alert_cooldown_seconds = 10
    fps = 1
    telegram_alerts = True

    __allowed__ = [
        "min_confidence",
        "labels",
        "sound",
        "volume",
        "alert_cooldown_seconds",
        "fps",
        "telegram_alerts",
    ]

    def __init__(self, **kwargs: dict[str, int | list[str] | str]) -> None:
        self.model = YOLO(model=get_latest_trained_model())
        self.picam2 = Picamera2()
        self._configure_cam()

        self.current_frame: Optional[bytes] = None
        self.current_frame_timestamp: str = "N/A"
        self.most_recent_detection = 0

        for k, v in kwargs.items():
            if k not in self.__class__.__allowed__:
                raise TypeError(
                    f"Invalid argument. Please provide an argument in {self.__class__.__allowed__}"
                )

        for k in self.__class__.__allowed__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, getattr(self.__class__, k))

        if self.sound not in os.listdir(ASSETS_PATH / "sound"):
            raise FileNotFoundError(
                f"{self.sound} does not exist in {ASSETS_PATH / 'sound'}"
            )

        self.internal_sleep_time = 1 / self.fps
        self.external_sleep_time = (
            self.internal_sleep_time + self.__class__.AVERAGE_INFERENCE_TIME
        )

        if self.telegram_alerts:
            load_dotenv(BASE_PATH / self.__class__.ENV)
            self.bot = Bot(token=os.getenv("BOT_TOKEN"))
            self.chat_id = int(os.getenv("CHAT_ID"))

        self._lock = Lock()
        self._stop_flag = False
        self._inference_thread = None

    def infer(self) -> dict[str, bool | bytes]:
        self.current_frame_timestamp = get_timestamp()
        frame = cv2.cvtColor(self.picam2.capture_array(), cv2.COLOR_RGB2BGR)
        results = self.model.predict(frame, stream=True, verbose=False)
        result = next(results)
        _, encoded = cv2.imencode(self.__class__.FRAME_ENCODING, result.plot())
        framebytes = encoded.tobytes()
        self.current_frame = framebytes

        if any(
            found["name"] in self.labels and found["confidence"] > self.min_confidence
            for found in result.summary()
        ):
            now = time.time()
            if now - self.most_recent_detection >= self.alert_cooldown_seconds:
                play_sound(self.sound, self.volume)
                if self.telegram_alerts:
                    self.send_frame_to_telegram(framebytes)
            self.most_recent_detection = int(time.time())
            return dict(found=True, framebytes=framebytes)

        return dict(found=False, framebytes=framebytes)

    def is_inferring(self) -> bool:
        with self._lock:
            return (
                self._inference_thread is not None and self._inference_thread.is_alive()
            )

    def infer_loop(self) -> None:
        while not self._stop_flag:
            self.infer()
            time.sleep(self.internal_sleep_time)

    def start_inference(self) -> None:
        with self._lock:
            self.picam2.start()
            self._stop_flag = False
            self._inference_thread = Thread(target=self.infer_loop, daemon=True)
            self._inference_thread.start()

    def stop_inference(self) -> None:
        with self._lock:
            self.picam2.stop()
            self._stop_flag = True

    def _configure_cam(self):
        self.picam2.preview_configuration.main.size = (1920, 1080)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.preview_configuration.align()
        self.picam2.configure("preview")

    def send_frame_to_telegram(self, frame: bytes) -> None:
        thread = Thread(target=asyncio.run, args=(self._send_frame_to_telegram(frame),))
        thread.start()

    async def _send_frame_to_telegram(self, frame: bytes) -> None:
        await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=frame,
            caption=f"Detection at {self.current_frame_timestamp}",
        )
