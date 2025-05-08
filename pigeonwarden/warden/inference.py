from picamera2 import Picamera2
from ultralytics import YOLO

from ..utils import get_latest_trained_model

picam2 = Picamera2()
picam2.preview_configuration.main.size = (1920, 1080)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

model = YOLO(model=get_latest_trained_model())

frame = picam2.capture_array()
results = model.predict(frame)

print(results)
#cv2.imwrite("test.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
