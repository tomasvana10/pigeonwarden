import time
from typing import Iterator

from flask import Flask, Response, render_template, stream_with_context, jsonify, request, redirect, url_for

from .. import get_available_port, is_port_in_use, get_cpu_temp, JSON
from ..warden import Warden


PORT = 6969
CONFIG = "config.json"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index() -> str:
    config = JSON.read(CONFIG)
    return render_template(
        "index.html",
        cron_days=config.cron_days,
        cron_start_time=config.cron_start_time,
        cron_end_time=config.cron_end_time,
        is_inferring=warden.is_inferring()
    )


@app.route("/submit_schedule", methods=["GET"])
def submit_schedule() -> Response:
    config = JSON.read(CONFIG)
    config.cron_days = "".join(request.args.getlist("cron_days"))
    config.cron_start_time = request.args.get("cron_start_time")
    config.cron_end_time = request.args.get("cron_end_time")
    JSON.write(config, CONFIG)
    
    return redirect(url_for("index"))


@app.route("/api/camera_stream")
def camera_stream() -> Response:
    def generate_frames() -> Iterator[bytes]:
        while True:
            if warden.current_frame:
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                    + warden.current_frame
                    + b"\r\n"
                )

            time.sleep(warden.external_sleep_time)

    return Response(
        stream_with_context(generate_frames()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/current_timestamp_stream")
def stream_text() -> Response:
    def generate() -> Iterator[str]:
        while True:
            yield f"data: {warden.current_frame_timestamp}\n\n"
            time.sleep(warden.external_sleep_time)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )


@app.route("/api/inference_on")
def inference_on() -> Response:
    modified = False
    if not warden.is_inferring():
        warden.start_inference()
        modified = True
    return jsonify(modified=modified, state=1)


@app.route("/api/inference_off")
def inference_off() -> Response:
    modified = False
    if warden.is_inferring():
        warden.stop_inference()
        modified = True
    return jsonify(modified=modified, state=0)


@app.route("/api/status")
def status() -> Response:
    return jsonify(state=1 if warden.is_inferring() else 0)


@app.route("/api/temp")
def temp() -> Response:
    return jsonify(**get_cpu_temp())


def init_server() -> None:
    global warden
    warden = Warden()
    warden.start_inference()

    if not is_port_in_use(PORT):
        app.run(host="0.0.0.0", port=PORT)
    else:
        app.run(host="0.0.0.0", port=get_available_port())


__all__ = ["init_server"]
