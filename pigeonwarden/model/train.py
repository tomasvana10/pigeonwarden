from ultralytics import YOLO

from ..constants import DATA_PATH


EPOCHS = 350
PATIENCE = 50


def train_model() -> None:
    model = YOLO("yolo11n.pt")

    assert DATA_PATH.exists(), (
        "Please install the dataset before training."
    )
    
    model.train(data=DATA_PATH, epochs=EPOCHS, patience=PATIENCE)
