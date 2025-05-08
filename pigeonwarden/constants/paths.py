from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_PATH / "datasets" / "pigeons"
RUNS_PATH = BASE_PATH / "runs"
DETECT_PATH = RUNS_PATH / "detect"
DATA_PATH = DATASET_PATH / "data.yaml"
TEST_IMGS_PATH = BASE_PATH / "pigeonwarden" / "test-images"
ASSETS_PATH = BASE_PATH / "assets"
