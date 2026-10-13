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
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    tmp_db = "/tmp/marketmind.db"
    source_db = os.path.join(BASE_DIR, "marketmind.db")
    if not os.path.exists(tmp_db) and os.path.exists(source_db):
        try:
            shutil.copyfile(source_db, tmp_db)
            print("[Vercel Runtime] Pre-seeded marketmind.db copied to /tmp/marketmind.db")
        except Exception as e:
            print(f"[Vercel Runtime Warning] Could not copy db to /tmp: {e}")

# Import FastAPI instance
from backend.main import app

# Vercel Serverless Python runtime expects `app`
__all__ = ["app"]
