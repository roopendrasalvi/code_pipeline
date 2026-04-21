import os
from dotenv import load_dotenv

load_dotenv()

# Collection name is the only thing worth configuring for the POC.
# Qdrant runs in-memory (no host/port needed).
# Embeddings run locally via sentence-transformers (no API key needed).
settings = {
    "collection": os.getenv("QDRANT_COLLECTION", "code_docs"),
}