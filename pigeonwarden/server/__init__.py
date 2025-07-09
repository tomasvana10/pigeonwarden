import os

from dotenv import load_dotenv
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from .. import resolve_redis_uri_components
from ..warden import Warden
from .route_init import init_auth_routes, init_main_routes

PORT = 6969
HOST = "0.0.0.0"

load_dotenv()

_app = Flask(__name__)
secret_key = os.getenv("SECRET_KEY")
if secret_key is None:
    raise RuntimeError(
        "SECRET_KEY is not defined in the environment, please create one with `scripts/secret.py`."
    )
_app.secret_key = secret_key
_app.config["WTF_CSRF_TIME_LIMIT"] = None
_app.config["TEMPLATES_AUTO_RELOAD"] = True

csrf = CSRFProtect()
csrf.init_app(_app)


def _factory(dev: bool = False) -> Flask:
    warden = Warden()

    users = {}
    raw_users = os.getenv("USERS", "")
    for user_entry in raw_users.split(","):
        if ":" in user_entry:
            name, password = user_entry.strip().split(":", 1)
            users[name] = password

    if not dev:
        components = resolve_redis_uri_components()
        limiter = Limiter(
            get_remote_address,
            app=_app,
            storage_uri=f"redis://{components['host']}:{components['port']}",
            default_limits=["30 per minute"],
        )
        limiter.init_app(_app)

    init_auth_routes(_app, users, dev)
    init_main_routes(_app, warden)
    warden.start_inference()
    return _app


def run_dev(*, host: str = HOST, port: int = PORT) -> None:
    app = _factory(True)
    app.run(host=host, port=port, threaded=True)


__all__ = ["run_dev", "HOST", "PORT"]
