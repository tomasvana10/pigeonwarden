import time

from flask import Flask, render_template, Response, stream_with_context

from ..model import load_dataset, train_model
from ..test import test_all
from .. import is_port_in_use, get_available_port
from ..warden import Warden

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


@srv.route("/api/stream")
def stream():
    def generate():
        while True:
            with warden.lock:
                frame = warden.current_frame
            
            if frame:
                yield (b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    frame + b"\r\n")
            
            time.sleep(warden.sleep_time)

    return Response(stream_with_context(generate()), mimetype="multipart/x-mixed-replace; boundary=frame")


def start_server() -> None:
    global warden 
    warden = Warden()    
    warden.start_infer_loop_thread(warden)
    
    if not is_port_in_use(PORT):
        srv.run(host="0.0.0.0", port=PORT)
    else:
        srv.run(host="0.0.0.0", port=get_available_port())


__all__ = ["start_server"]
