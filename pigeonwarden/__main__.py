import sys

from .model import load_dataset, train_model
from .server import start_server
from .test import test_all
from .utils import export_ncnn
from .warden import infer

arg = sys.argv[1]

if arg == "dataset":
    load_dataset()
elif arg == "train":
    train_model()
elif arg == "test":
    test_all()
elif arg == "infer":
    infer()
elif arg == "ncnn":
    export_ncnn()
elif arg == "start-server":
    start_server()
