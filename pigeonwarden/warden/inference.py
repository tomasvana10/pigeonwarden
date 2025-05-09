import time

from picamera2 import Picamera2
from ultralytics import YOLO
import cv2

from .speaker import play_sound
from ..utils import get_latest_trained_model, configure_cam
from .. import Singleton


class Warden(metaclass=Singleton):
    ENCODING = ".jpg"
    
    min_confidence = 0.8
    labels = ["common-mynas", "pigeons"]
    sound = "airhorn.mp3"
    volume = 150
    alert_cooldown = 1000
    
    __allowed__ = ["min_confidence", "labels", "sound", "volume", "alert_cooldown"]


    def __init__(self, **kwargs: dict[str, int | list[str] | str]) -> None:
        self.model = YOLO(model=get_latest_trained_model())
        self.picam2 = Picamera2()
        configure_cam(self.picam2)
        self.picam2.start()
        
        self.most_recent_detection = 0
        
        for k, v in kwargs.items():
            assert (k in self.__class__.__allowed__)
        
        for k in self.__class__.__allowed__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, getattr(self.__class__, k))
    
    
    def infer(self) -> dict[str, bool | bytes]:
        frame = cv2.cvtColor(self.picam2.capture_array(), cv2.COLOR_RGB2BGR)
        results = self.model.predict(frame)
        _, encoded = cv2.imencode(self.__class__.ENCODING, results[0].plot())
        framebytes = encoded.tobytes()

        if any(found["name"] in self.labels and found["confidence"] > self.min_confidence for found in results[0].summary()):
            now = time.time()
            if now - self.most_recent_detection >= self.alert_cooldown:
                play_sound(self.sound, self.volume)
            self.most_recent_detection = time.time()
            return dict(found=True, framebytes=framebytes)
        
        return dict(found=False, framebytes=framebytes)

