import time
from typing import Iterator

from flask import Flask, Response, render_template, stream_with_context

from .. import get_available_port, is_port_in_use
from ..warden import Warden

PORT = 6969

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index() -> str:
    return render_template("index.html")


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


@app.route("/api/toggle-inference")
def toggle_inference() -> Response:
    if warden.is_inferring():
        warden.stop_inference()
        return Response("0", status=200)
    else:
        warden.start_inference()
        return Response("1", status=200)


@app.route("/api/status")
def status() -> Response:
    return Response("1" if warden.is_inferring() else "0", status=200)


def init_server() -> None:
    global warden
    warden = Warden()
    warden.start_inference()

    if not is_port_in_use(PORT):
        app.run(host="0.0.0.0", port=PORT)
    else:
        app.run(host="0.0.0.0", port=get_available_port())


__all__ = ["init_server"]
