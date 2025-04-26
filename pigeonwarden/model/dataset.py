import os
import shutil
from zipfile import ZipFile

import requests

from .. import DATASET_PATH, DATASET_URL


def load_dataset() -> None:
    os.makedirs(DATASET_PATH.parent)
    zip_path = DATASET_PATH.with_suffix(".zip")
    temp_extract = os.path.join(DATASET_PATH.parent, "temp_extract")
    final_dest = os.path.join(DATASET_PATH)

    req = requests.get(DATASET_URL, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in req.iter_content(chunk_size=8192):
            f.write(chunk)

    os.makedirs(temp_extract, exist_ok=True)
    with ZipFile(zip_path) as zip_ref:
        zip_ref.extractall(temp_extract)

    os.remove(zip_path)
    os.makedirs(final_dest, exist_ok=True)

    for item in os.listdir(temp_extract):
        shutil.move(os.path.join(temp_extract, item), final_dest)

    os.rmdir(temp_extract)
