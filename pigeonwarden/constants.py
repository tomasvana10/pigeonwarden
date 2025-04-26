from pathlib import Path

DATASET_URL = "https://universe.roboflow.com/ds/f1A39J33b5?key=u6rvtkrVQv"

BASE_PATH = Path(__file__).resolve().parents[1]
DATASET_PATH = BASE_PATH / "datasets" / "pigeons"
RUNS_PATH = BASE_PATH / "runs"
DETECT_PATH = RUNS_PATH / "detect"
DATA_PATH = DATASET_PATH / "data.yaml"
TEST_IMGS_PATH = BASE_PATH / "pigeonwarden" / "test-images"
