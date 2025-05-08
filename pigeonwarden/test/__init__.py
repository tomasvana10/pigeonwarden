import os

from ultralytics import YOLO

from ..constants import TEST_IMGS_PATH
from ..utils import get_latest_trained_model


def test_all() -> None:
    try:
        model = YOLO(model=get_latest_trained_model())
    except FileNotFoundError:
        raise Exception("You must run pigeonwarden with the `ncnn` parameter first.")

    errors: list[str] = []
    for img in os.listdir(TEST_IMGS_PATH):
        expected = int(img.split("-")[0])
        results = model.predict(TEST_IMGS_PATH / img)
        actual = len(results[0].boxes)
        results[0].save(img)
        if expected != actual:
            errors.append(f"Image {img} has {actual} boxes, expected {expected}")

    if errors:
        raise AssertionError("Test failures:\n" + "\n".join(errors))

    print("All tests passed.")


__all__ = ["test_all"]
