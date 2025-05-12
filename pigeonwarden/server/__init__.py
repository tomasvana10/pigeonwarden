from flask import Flask

from .. import get_available_port, is_port_in_use
from ..warden import Warden
from .routes import init_routes


PORT = 6969
HOST = "0.0.0.0"
CONFIG = "config.json"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


def init_server(*, host: str = HOST, port: int = PORT) -> None:
    # If you want to make pigeonwarden work with anything other than the Flask development
    # server PLEASE be my guest and submit a pull request because I have given up
    warden = Warden(fps=4)
    init_routes(app, warden, CONFIG)
    warden.start_inference()

    free_port = get_available_port() if is_port_in_use(port) else port
    app.run(host=host, port=free_port)


__all__ = ["init_server", "HOST", "PORT"]
