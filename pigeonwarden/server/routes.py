import time
from typing import Iterator, Optional

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)
from flask_httpauth import HTTPBasicAuth

from .. import Config, get_cpu_temp
from ..warden import Warden


def init_routes(
    app: Flask, warden: Warden, auth: Optional[HTTPBasicAuth], dev: bool
) -> None:
    conf = Config()

    if not dev:

        @app.before_request
        def main_auth() -> Optional[Response]:
            return auth.login_required(lambda: None)()

    @app.route("/")
    def index() -> str:
        entries = conf.read_all()

        return render_template(
            "index.html",
            cron_days=entries["cron_days"],
            cron_start_time=entries["cron_start_time"],
            cron_end_time=entries["cron_end_time"],
            is_inferring=warden.is_inferring(),
        )

    @app.route("/submit_schedule", methods=["GET"])
    def submit_schedule() -> Response:
        conf.write("cron_days", "".join(request.args.getlist("cron_days")))
        conf.write("cron_start_time", request.args.get("cron_start_time"))
        conf.write("cron_end_time", request.args.get("cron_end_time"))

        return redirect(url_for("index"))

    @app.route("/api/camera_stream")
    def camera_stream() -> Response:
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

    @app.route("/api/current_timestamp_stream")
    def stream_text() -> Response:
        def generate() -> Iterator[str]:
            while True:
                yield f"data: {warden.current_frame_timestamp}\n\n"
                time.sleep(warden.external_sleep_time)

        return Response(stream_with_context(generate()), mimetype="text/event-stream")

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
