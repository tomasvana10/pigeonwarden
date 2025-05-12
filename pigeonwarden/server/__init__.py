from flask import Flask

from ..warden import Warden
from .routes import init_routes


PORT = 6969
HOST = "0.0.0.0"
CONFIG = "config.json"

_app = Flask(__name__)
_app.config["TEMPLATES_AUTO_RELOAD"] = True


def _factory() -> Flask:
    warden = Warden(fps=4)
    init_routes(_app, warden, CONFIG)
    warden.start_inference()

    return _app


def run_dev(*, host: str = HOST, port: int = PORT) -> None:
    app = _factory()
    app.run(host=host, port=port)


__all__ = ["run_dev", "HOST", "PORT"]
