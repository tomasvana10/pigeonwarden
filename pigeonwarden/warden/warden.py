import asyncio
import os
import time
from datetime import datetime
from threading import Thread

import cv2
from dotenv import load_dotenv
from picamera2 import Picamera2
from telegram import Bot
from ultralytics import YOLO

from .. import Singleton
from ..constants import BASE_PATH, ASSETS_PATH
from ..utils import configure_cam, get_latest_trained_model
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

    inference_thread = None

    def __init__(self, **kwargs: dict[str, int | list[str] | str]) -> None:
        self.model = YOLO(model=get_latest_trained_model())
        self.picam2 = Picamera2()
        configure_cam(self.picam2)
        self.picam2.start()

        load_dotenv(BASE_PATH / self.__class__.ENV)
        self.bot = Bot(token=os.getenv("BOT_TOKEN"))
        self.chat_id = int(os.getenv("CHAT_ID"))

        self.current_frame: bytes | None = None
        self.most_recent_detection = 0

        for k, v in kwargs.items():
            assert k in self.__class__.__allowed__

        for k in self.__class__.__allowed__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, getattr(self.__class__, k))
        
        assert self.sound in os.listdir(ASSETS_PATH / "sound")

        self.internal_sleep_time = 1 / self.fps
        self.external_sleep_time = (
            self.internal_sleep_time + self.__class__.AVERAGE_INFERENCE_TIME
        )

    def infer(self) -> dict[str, bool | bytes]:
        frame = cv2.cvtColor(self.picam2.capture_array(), cv2.COLOR_RGB2BGR)
        results = self.model.predict(frame, stream=True, verbose=False)
        result = next(results)
        _, encoded = cv2.imencode(self.__class__.FRAME_ENCODING, result.plot())
        framebytes = encoded.tobytes()

        if any(
            found["name"] in self.labels and found["confidence"] > self.min_confidence
            for found in result.summary()
        ):
            now = time.time()
            if now - self.most_recent_detection >= self.alert_cooldown_seconds:
                play_sound(self.sound, self.volume)
                if self.telegram_alerts:
                    self.send_frame(framebytes)
            self.most_recent_detection = int(time.time())
            return dict(found=True, framebytes=framebytes)

        return dict(found=False, framebytes=framebytes)

    def infer_loop(self) -> None:
        while True:
            result = self.infer()
            self.current_frame = result["framebytes"]
            time.sleep(self.internal_sleep_time)

    @classmethod
    def start_inference(cls, inst: "Warden") -> None:
        assert cls.inference_thread is None

        cls.inference_thread = Thread(target=inst.infer_loop, daemon=True)
        cls.inference_thread.start()

    @classmethod
    def stop_inference(cls) -> None:
        assert cls.inference_thread is not None

        cls.inference_thread.join()
        cls.inference_thread = None

    def _get_timestamp(self) -> None:
        return datetime.utcfromtimestamp(time.time()).strftime("%d/%m/%Y %H:%M:%S")

    def send_frame(self, frame: bytes) -> None:
        asyncio.create_task(self._send_frame(frame))

    async def _send_frame(self, frame: bytes) -> None:
        await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=frame,
            caption=f"Detection at {self._get_timestamp()}",
        )
