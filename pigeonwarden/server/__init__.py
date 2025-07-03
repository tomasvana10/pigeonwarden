import os

from dotenv import load_dotenv
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from passlib.hash import bcrypt

from ..warden import Warden
from .routes import init_routes

PORT = 6969
HOST = "0.0.0.0"
CONFIG = "config.json"

_app = Flask(__name__)
_app.config["TEMPLATES_AUTO_RELOAD"] = True


def _factory(dev: bool = False) -> Flask:
    load_dotenv()
    warden = Warden(fps=4)
    auth = None

    if not dev:
        auth = HTTPBasicAuth()
        limiter = Limiter(
            get_remote_address,
            app=_app,
            storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}",
            default_limits=["5 per minute"],
        )
        limiter.init_app(_app)

        USERNAME = os.getenv("USERNAME")
        USERPASS = os.getenv("USERPASS")

        users = {USERNAME: USERPASS}

        @auth.verify_password
        def _verify_password(username: str, password: str):
            if username in users and bcrypt.verify(password, users[username]):
                return username

    init_routes(_app, warden, auth, dev, CONFIG)
    warden.start_inference()

    return _app


def run_dev(*, host: str = HOST, port: int = PORT) -> None:
    app = _factory(True)
    app.run(host=host, port=port, threaded=True)


__all__ = ["run_dev", "HOST", "PORT"]
