import argparse
import subprocess

from .model import load_dataset, train_model
from .server import HOST, PORT, run_dev
from .utils import export_ncnn


def main():
    parser = argparse.ArgumentParser(description="pigeonwarden options")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("dataset")
    subparsers.add_parser("train")
    subparsers.add_parser("ncnn")

    run_parser = subparsers.add_parser("run")
    run_subparsers = run_parser.add_subparsers(dest="env", required=True)

    for env in ["dev", "deploy"]:
        env_parser = run_subparsers.add_parser(env)
        env_parser.add_argument("--host", help="Server hostname")
        env_parser.add_argument("--port", type=int, help="Server port")

    args = parser.parse_args()

    if args.command == "dataset":
        load_dataset()
    elif args.command == "train":
        train_model()
    elif args.command == "ncnn":
        export_ncnn()
    elif args.command == "run":
        host = args.host or HOST
        port = args.port or PORT
        if args.env == "dev":
            run_dev(host=host, port=port)
        elif args.env == "deploy":
            subprocess.run(
                [
                    "waitress-serve",
                    "--host",
                    host,
                    "--port",
                    str(port),
                    "--threads",
                    "35",
                    "--call",
                    "pigeonwarden.server:_factory",
                ]
            )


main()
