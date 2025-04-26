from ultralytics import YOLO

from .. import DATA_PATH

EPOCHS = 10
PATIENCE = 5


def train_model() -> None:
    model = YOLO("yolo11n.pt")

    assert DATA_PATH.exists(), (
        "Please run `python -m pigeonwarden dataset` to install the required dataset."
    )

    model.train(data=DATA_PATH, epochs=EPOCHS, patience=PATIENCE)
