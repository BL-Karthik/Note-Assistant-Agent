
import chromadb
from pathlib import Path

# Get the backend directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Set the persistent ChromaDB location
CHROMA_DB_PATH = BASE_DIR / "data" / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)
