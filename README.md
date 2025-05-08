# pigeonwarden
Detect and scare pigeons

---

Model used - https://universe.roboflow.com/general-detection/pigeon-model

Camera reference - https://docs.ultralytics.com/guides/raspberry-pi/#use-raspberry-pi-camera

Extra reference for bounding box rendering - https://www.ejtech.io/code/yolo_detect.py

Pytorch install reference (for me) - `pytorch install - pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

---

## Usage
1. `pip install -r requirements.txt`
2. `python -m pigeonwarden dataset` - Install pigeon dataset
3. `python -m pigeonwarden train` - Train model
4. `python -m pigeonwarden infer` - Begin pigeon inference (not yet implemented)

## Testing
Run `python -m pigeonwarden test`. You can modify the images you wish to test by adding them in `pigeonwarden/test-images` in the form `<expected-pigeon-count>-<counter-from-0>.<suffix>` (e.g. `1-0.png`, `1-1.png`, `2-0.png`).

## Hardware
- Raspberry Pi 4/4b/5 8GB+
- USB Speaker
- USB Camera


https://github.com/AsamK/signal-cli
https://medium.com/@dogukanakkaya/how-to-send-signal-messages-with-signal-cli-21f6fa1c7d58