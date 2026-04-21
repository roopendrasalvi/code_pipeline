"""
embedder.py  —  local embeddings via sentence-transformers

Model:      all-MiniLM-L6-v2  (downloads once ~90MB, then cached)
Dimensions: 384
No API key or internet connection needed after the first download.
"""

from sentence_transformers import SentenceTransformer

# Load once at module level — the model stays in memory for the whole server lifetime
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    """Return a 384-float embedding vector for a piece of text."""
    return _model.encode(text).tolist()


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed every chunk and attach the vector under key "embedding".
    Chunks that fail are logged and skipped.
    """
    embedded = []
    for idx, chunk in enumerate(chunks):
        try:
            vector = embed_text(chunk["content"])
            embedded.append({**chunk, "embedding": vector})
        except Exception as e:
            print(f"[embedder] chunk {idx} of '{chunk['file_path']}' failed: {e}")
    return embedded