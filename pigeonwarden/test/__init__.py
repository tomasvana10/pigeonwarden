import os

from ultralytics import YOLO

from ..constants import ASSETS_PATH
from ..utils import get_latest_trained_model


def test_all() -> None:
    try:
        model = YOLO(model=get_latest_trained_model())
    except FileNotFoundError:
        raise Exception("You must run pigeonwarden with the `ncnn` parameter first.")

    errors: list[str] = []
    dir_ = ASSETS_PATH / "test-images"
    for img in os.listdir(dir_):
        expected = int(img.split("-")[0])
        results = model.predict(dir_ / img)
        actual = len(results[0].boxes)
        results[0].save(img)
        if expected != actual:
            errors.append(f"Image {img} has {actual} boxes, expected {expected}")

    if errors:
        raise AssertionError("Test failures:\n" + "\n".join(errors))

    print("All tests passed.")


__all__ = ["test_all"]
