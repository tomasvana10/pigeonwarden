import socket as s
import sys

port = 6969


def start_server() -> None:
    with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
        sock.bind(("", port))
        sock.listen(1)

        print(
            f"Running server on port {port} (http://127.0.0.1:{port}). Use CTRL+C to stop."
        )

        while True:
            conn, addr = sock.accept()

        sock.close()
        sys.exit()


__all__ = ["start_server"]
