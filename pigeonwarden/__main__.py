import sys

from .model import load_dataset, train_model
from .server import start_server
from .test import test_all

arg = sys.argv[1]

if arg == "dataset":
    load_dataset()
elif arg == "train":
    train_model()
elif arg == "test":
    test_all()
elif arg == "infer":
    print("Not yet implemented")
elif arg == "start-server":
    start_server()
