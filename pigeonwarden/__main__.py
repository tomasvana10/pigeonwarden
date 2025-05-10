import sys

from .model import load_dataset, train_model
from .server import init_server
from .utils import export_ncnn

arg = sys.argv[1]

if arg == "dataset":
    load_dataset()
elif arg == "train":
    train_model()
elif arg == "ncnn":
    export_ncnn()
elif arg == "init":
    init_server()
