from flask import Flask, render_template, Response

from ..model import load_dataset, train_model
from ..test import test_all
from .. import is_port_in_use, get_available_port
from ..warden import infer

PORT = 6969

srv = Flask(__name__)
srv.config["TEMPLATES_AUTO_RELOAD"] = True


@srv.route("/")
def index() -> str:
    return render_template("index.html")


@srv.route("/api/load-dataset")
def _load_dataset() -> Response:
    try:
        load_dataset()
    except FileExistsError:
        return Response(response="The dataset has already been installed.", status=500)

    return Response(response="Successfully installed dataset.", status=200)


@srv.route("/api/train-model")
def _train_model() -> Response:
    try:
        train_model()
    except AssertionError as ex:
        return Response(response=str(ex), status=500)

    return Response(response="Successfully trained a new iteration of this model.", status=200)


@srv.route("/api/test-model")
def _test_model() -> Response:
    try:
        test_all()
    except AssertionError as ex:
        return Response(response=str(ex), status=500)

    return Response(response="All tests passed.", status=200)    


@srv.route("/api/frame")
def get_frame():
    result = infer()
    return Response(result["framebytes"], mimetype="image/jpeg")


def start_server() -> None:
    if not is_port_in_use(PORT):
        srv.run(host="0.0.0.0", port=PORT)
    else:
        srv.run(host="0.0.0.0", port=get_available_port())


__all__ = ["start_server"]
