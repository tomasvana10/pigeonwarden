import time
from typing import Iterator

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
from werkzeug.wrappers.response import Response as WZResponse

from ... import DB
from ...warden import Warden


def init_main_routes(app: Flask, warden: Warden) -> None:
    conf = DB()

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
    def submit_schedule() -> WZResponse:
        conf.write("cron_days", "".join(request.args.getlist("cron_days")))
        conf.write(
            "cron_start_time",
            request.args.get("cron_start_time", DB.DEFAULTS["cron_start_time"]),
        )
        conf.write(
            "cron_end_time",
            request.args.get("cron_end_time", DB.DEFAULTS["cron_end_time"]),
        )

        return redirect(url_for("index"))

    @app.route("/api/camera_stream")
    def camera_stream() -> Response:
        def generate() -> Iterator[bytes]:
            while warden.current_frame is None:
                time.sleep(0.1)
                
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
        with warden._lock:
            modified = False
            cooldown = False
            if not warden.is_inferring():
                cooldown = not warden.toggle_inference(1)
                modified = True
            return jsonify(modified=modified, state=1, cooldown=cooldown)

    @app.route("/api/inference_off")
    def inference_off() -> Response:
        with warden._lock:
            modified = False
            cooldown = False
            if warden.is_inferring():
                cooldown = not warden.toggle_inference(0)
                modified = True
            return jsonify(modified=modified, state=0, cooldown=cooldown)

    @app.route("/api/status")
    def status() -> Response:
        return jsonify(state=1 if warden.is_inferring() else 0)
