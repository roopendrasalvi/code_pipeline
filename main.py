"""
main.py  —  FastAPI server

Single endpoint:
    POST /index   { "repo_path": "/path/to/repo" }

Pipeline:
    read files → read commits → chunk → embed → store in Qdrant
"""

from pathlib import Path
from typing import TypedDict

from fastapi import FastAPI, HTTPException

from git_reader   import read_source_files, read_commits
from chunker      import chunk_files
from embedder     import embed_chunks
from vector_store import get_client, ensure_collection, upsert_chunks
from config       import settings


app = FastAPI(title="Doc-Gen API", version="0.1.0")


# ── Typed shapes for request / response ───────────────────────────────────────

class IndexRequest(TypedDict):
    repo_path: str

class IndexResponse(TypedDict):
    status:        str
    repo_path:     str
    files_found:   int
    chunks_stored: int
    commits_read:  int


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(repo_path: str) -> IndexResponse:
    """
    Full read → chunk → embed → store pipeline.
    Prints progress at each step so you can follow along in the terminal.
    """
    print(f"\n[pipeline] repo: {repo_path}")

    files = read_source_files(repo_path)
    print(f"[pipeline] {len(files)} files found")

    if not files:
        return {"files_found": 0, "chunks_stored": 0, "commits_read": 0}

    commits = read_commits(repo_path)
    print(f"[pipeline] {len(commits)} commits read")

    chunks = chunk_files(files)
    print(f"[pipeline] {len(chunks)} chunks produced")

    embedded = embed_chunks(chunks)
    print(f"[pipeline] {len(embedded)} chunks embedded")

    client     = get_client()
    collection = settings["collection"]
    ensure_collection(client, collection)
    stored = upsert_chunks(client, collection, embedded)
    print(f"[pipeline] {stored} vectors stored → collection '{collection}'")

    return {
        "files_found":   len(files),
        "chunks_stored": stored,
        "commits_read":  len(commits),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/index")
def index_repository(request: dict) -> IndexResponse:
    """
    Index a local git repository into Qdrant.

    Body:  { "repo_path": "/absolute/path/to/repo" }
    """
    repo_path = Path(request.get("repo_path", "")).resolve()

    if not repo_path.exists():
        raise HTTPException(status_code=400, detail=f"Path not found: {repo_path}")
    if not repo_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {repo_path}")

    result = run_pipeline(str(repo_path))

    return IndexResponse(
        status        = "indexed",
        repo_path     = str(repo_path),
        files_found   = result["files_found"],
        chunks_stored = result["chunks_stored"],
        commits_read  = result["commits_read"],
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}