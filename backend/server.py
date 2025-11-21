import threading
import uvicorn
import socket

from .main import app as fastapi_app

def is_port_in_use(port: int) -> bool:
    """Check if port is already running (so we don't start twice)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("0.0.0.0", port)) == 0

def run_fastapi():
    if not is_port_in_use(8000):
        uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

def start_backend_server():
    thread = threading.Thread(target=run_fastapi, daemon=True)
    thread.start()
