import chromadb
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

if os.getenv("VERCEL"):
    CHROMA_DB_PATH = Path("/tmp/chroma_db")
else:
    CHROMA_DB_PATH = BASE_DIR / "data" / "chroma_db"

CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)