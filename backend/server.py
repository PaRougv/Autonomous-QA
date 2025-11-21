import threading
import uvicorn

from .main import app as fastapi_app


def run_fastapi():
    # Run FastAPI on port 8000
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")


def start_backend_server():
    # Start FastAPI in a background thread
    thread = threading.Thread(target=run_fastapi, daemon=True)
    thread.start()
