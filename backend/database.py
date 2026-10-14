from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "")
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DB_URL)
