import time
from typing import Iterator

from flask import Flask, Response, render_template, stream_with_context

from .. import get_available_port, is_port_in_use
from ..model import load_dataset, train_model
from ..test import test_all
from ..warden import Warden

PORT = 6969

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/load-dataset")
def _load_dataset() -> Response:
    try:
        load_dataset()
    except FileExistsError:
        return Response(response="The dataset has already been installed.", status=500)

    return Response(response="Successfully installed dataset.", status=200)


@app.route("/api/train-model")
def _train_model() -> Response:
    try:
        train_model()
    except AssertionError as ex:
        return Response(response=str(ex), status=500)

    return Response(
        response="Successfully trained a new iteration of this model.", status=200
    )


@app.route("/api/test-model")
def _test_model() -> Response:
    try:
        test_all()
    except AssertionError as ex:
        return Response(response=str(ex), status=500)

    return Response(response="All tests passed.", status=200)


@app.route("/api/stream")
def stream() -> Response:
    def generate() -> Iterator[bytes]:
        while True:
            if warden.current_frame:
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                    + warden.current_frame
                    + b"\r\n"
                )

            time.sleep(warden.external_sleep_time)

    return Response(
        stream_with_context(generate()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def start_server() -> None:
    global warden
    warden = Warden()
    warden.start_inference(warden)

    if not is_port_in_use(PORT):
        app.run(host="0.0.0.0", port=PORT)
    else:
        app.run(host="0.0.0.0", port=get_available_port())


__all__ = ["start_server"]
