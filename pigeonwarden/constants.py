from pathlib import Path

DATASET_URL = "https://app.roboflow.com/ds/nZXCefQ1AU?key=YgRwnTbunC"

BASE_PATH = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_PATH / "datasets" / "pigeons"
RUNS_PATH = BASE_PATH / "runs"
DETECT_PATH = RUNS_PATH / "detect"
ASSETS_PATH = BASE_PATH / "assets"
