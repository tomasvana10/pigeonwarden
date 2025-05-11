import argparse

from .model import load_dataset, train_model
from .server import init_server, HOST, PORT
from .utils import export_ncnn


def main():
    parser = argparse.ArgumentParser(description="pigeonwarden options")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("dataset")
    subparsers.add_parser("train")
    subparsers.add_parser("ncnn")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--dev", action="store_true", help="Start in dev mode")
    init_parser.add_argument("--host", help="Server hostname")
    init_parser.add_argument("--port", type=int, help="Server port")

    args = parser.parse_args()

    if args.command == "dataset":
        load_dataset()
    elif args.command == "train":
        train_model()
    elif args.command == "ncnn":
        export_ncnn()
    elif args.command == "init":
        init_server(dev=args.dev, host=args.host or HOST, port=args.port or PORT)


main()
