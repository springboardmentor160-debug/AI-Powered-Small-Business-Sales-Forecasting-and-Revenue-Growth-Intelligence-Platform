import os
import sys
import subprocess
import time

def run():
    """
    Unified Single-Service Runner for Free-Tier Cloud Deployments (Render / Railway / Heroku).
    Spins up the FastAPI backend internally on 127.0.0.1:8000 and exposes the Streamlit UI
    on the platform-assigned public $PORT, staying well within 512MB RAM limits.
    """
    public_port = os.environ.get("PORT", "8501")
    internal_backend_port = "8000"

    print(f"⚡ [MarketMind AI] Starting internal FastAPI backend on port {internal_backend_port}...")
    backend_proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1",
        "--port", internal_backend_port,
        "--workers", "1"
    ])

    # Direct Streamlit to talk to the local backend
    os.environ["API_URL"] = f"http://127.0.0.1:{internal_backend_port}"
    
    # Wait for backend initialization
    time.sleep(2)

    print(f"🚀 [MarketMind AI] Starting Streamlit UI on public port {public_port}...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(public_port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], check=True)
    finally:
        print("🛑 Shutting down backend process...")
        backend_proc.terminate()

if __name__ == "__main__":
    run()
