"""
chunker.py  —  split file content into overlapping chunks for embedding

Embedding models have a token limit (~256 tokens for all-MiniLM-L6-v2).
Overlapping chunks prevent a function or logical block from being cut
at a boundary and losing context on both sides.
"""


CHUNK_SIZE    = 800    # ~200 tokens at 4 chars/token — within MiniLM's 256 token limit
CHUNK_OVERLAP = 100    # shared characters between consecutive chunks


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping fixed-size character chunks."""
    chunks = []
    start  = 0
    while start < len(text):
        chunks.append(text[start : start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def chunk_file(file: dict) -> list[dict]:
    """
    Split a single file dict into chunk dicts.

    Each chunk inherits file_path and language, and adds:
      chunk_index  — position of this chunk within the file
      chunk_total  — total chunks produced from this file
    """
    chunks = chunk_text(file["content"])
    return [
        {
            "file_path":   file["file_path"],
            "language":    file["language"],
            "chunk_index": idx,
            "chunk_total": len(chunks),
            "content":     chunk,
        }
        for idx, chunk in enumerate(chunks)
    ]


def chunk_files(files: list[dict]) -> list[dict]:
    """Chunk every file and return a single flat list of all chunks."""
    result = []
    for file in files:
        result.extend(chunk_file(file))
    return result