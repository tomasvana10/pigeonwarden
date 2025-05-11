import multiprocessing

import gunicorn
from flask import Flask

from .. import get_available_port, is_port_in_use
from ..warden import Warden
from .routes import init_routes

PORT = 6969
HOST = "0.0.0.0"
CONFIG = "config.json"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


class ProductionApp(gunicorn.app.base.BaseApplication):
    def __init__(self, app: Flask, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self) -> None:
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> None:
        return self.application


def init_server(dev=False, *, host=HOST, port=PORT) -> None:
    warden = Warden(fps=4)
    init_routes(app, warden, CONFIG)
    warden.start_inference()

    free_port = get_available_port() if is_port_in_use(port) else port
    if dev:
        app.run(host=host, port=free_port)
    else:
        options = {
            "bind": "%s:%s" % (host, free_port),
            "workers": multiprocessing.cpu_count() * 2 + 1,
        }
        ProductionApp().run(app, options)


__all__ = ["init_server"]
