from picamera2 import Picamera2
from ultralytics import YOLO
import cv2

from ..utils import configure_cam


MIN_CONFIDENCE = 0.8
LABELS = ["common-mynas", "pigeons"]


def infer(model: YOLO, picam2: Picamera2):
    # `picam2` must be pre-configured and initialised
    
    frame = cv2.cvtColor(picam2.capture_array(), cv2.COLOR_RGB2BGR)
    results = model.predict(frame)
    _, jpg = cv2.imencode(".jpg", results[0].plot())
    framebytes = jpg.tobytes()

    if any(found["name"] in LABELS and found["confidence"] > MIN_CONFIDENCE for found in results[0].summary()):
        return dict(found=True, framebytes=framebytes)
    
    return dict(found=False, framebytes=framebytes)
        
