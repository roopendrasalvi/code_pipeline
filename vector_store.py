"""
vector_store.py  —  store chunk embeddings in Qdrant (in-memory)

Qdrant keeps vectors alongside a payload (arbitrary JSON).
We store the raw chunk text and metadata in the payload so search
results are self-contained — no need to re-read files later.

In-memory mode: data lives in RAM for the server lifetime.
To persist across restarts, swap QdrantClient(":memory:") for
QdrantClient(path="./qdrant_data") — no Docker needed either way.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import settings


EMBEDDING_DIM = 384   # matches all-MiniLM-L6-v2 output size
BATCH_SIZE    = 100   # points per upsert call


# Single shared in-memory client — created once when the module loads
_client = QdrantClient(":memory:")


def get_client() -> QdrantClient:
    """Return the shared in-memory Qdrant client."""
    return _client


def ensure_collection(client: QdrantClient, collection: str) -> None:
    """Create the collection if it doesn't already exist."""
    existing = {c.name for c in client.get_collections().collections}
    if collection not in existing:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        print(f"[vector_store] created collection '{collection}'")


def upsert_chunks(client: QdrantClient, collection: str, embedded_chunks: list[dict]) -> int:
    """
    Write all embedded chunks to Qdrant in batches.
    Returns the number of points stored.

    Point IDs are positional integers — fine for a POC.
    For production use a stable ID (hash of file_path + chunk_index) so
    re-indexing the same repo updates existing points instead of duplicating.
    """
    if not embedded_chunks:
        return 0

    points = [
        PointStruct(
            id      = idx,
            vector  = chunk["embedding"],
            payload = {
                "file_path":   chunk["file_path"],
                "language":    chunk["language"],
                "chunk_index": chunk["chunk_index"],
                "chunk_total": chunk["chunk_total"],
                "content":     chunk["content"],
            },
        )
        for idx, chunk in enumerate(embedded_chunks)
    ]

    for start in range(0, len(points), BATCH_SIZE):
        client.upsert(collection_name=collection, points=points[start : start + BATCH_SIZE])

    return len(points)