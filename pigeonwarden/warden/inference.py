from picamera2 import Picamera2
from ultralytics import YOLO
import cv2

from ..utils import get_latest_trained_model


MIN_CONFIDENCE = 0.8
LABELS = ["common-mynas", "pigeons"]


def infer():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (1920, 1080)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()

    model = YOLO(model=get_latest_trained_model())

    frame = cv2.cvtColor(picam2.capture_array(), cv2.COLOR_RGB2BGR)
    results = model.predict(frame)
    _, jpg = cv2.imencode(".jpg", results[0].plot())
    framebytes = jpg.tobytes()

    if any(found["name"] in LABELS and found["confidence"] > MIN_CONFIDENCE for found in results[0].summary()):
        return dict(found=True, framebytes=framebytes)
    
    return dict(found=False, framebytes=framebytes)
        
