from ultralytics import YOLO

from .. import DATASET_PATH

EPOCHS = 10
PATIENCE = 5


def train_model() -> None:
    model = YOLO("yolo11n.pt")
    path = DATASET_PATH / "data.yaml"

    assert path.exists(), "Please install the dataset before training."

    model.train(data=path, epochs=EPOCHS, patience=PATIENCE)
