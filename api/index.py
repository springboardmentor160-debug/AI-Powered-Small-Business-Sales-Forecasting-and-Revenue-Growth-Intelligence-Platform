"""
MarketMind AI — Vercel Serverless Function Entrypoint (Milestone 4)
Exposes the ASGI FastAPI application for Vercel Serverless Python Runtime.
"""

import os
import sys
import shutil

# Ensure the root of the Milestone 4 project is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Pre-copy the seeded database to /tmp when running on Vercel's read-only environment
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("VERCEL_ENV"):
    import tempfile
    tmp_dir = "/tmp" if os.path.exists("/tmp") else tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_db = os.path.join(tmp_dir, "marketmind.db")
    candidate_sources = [
        os.path.join(BASE_DIR, "marketmind.db"),
        os.path.join(BASE_DIR, "marketmind_default.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "marketmind.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "marketmind_default.db"),
        "/var/task/marketmind.db",
        "/var/task/marketmind_default.db",
        "/var/task/Milestone_4/marketmind.db",
        "/var/task/Milestone_4/marketmind_default.db",
    ]
    if not os.path.exists(tmp_db) or os.path.getsize(tmp_db) < 1024:
        for src in candidate_sources:
            if os.path.exists(src) and os.path.isfile(src) and os.path.getsize(src) > 1024:
                try:
                    shutil.copyfile(src, tmp_db)
                    print(f"[Vercel Runtime] Pre-seeded marketmind.db copied to {tmp_db} from {src}")
                    break
                except Exception as e:
                    print(f"[Vercel Runtime Warning] Could not copy db to /tmp from {src}: {e}")

# Import FastAPI instance
from backend.main import app

# Vercel Serverless Python runtime expects `app`
__all__ = ["app"]
