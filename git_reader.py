"""
git_reader.py  —  read source files and commit history from a local git repo
"""

from pathlib import Path
import git


CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".c",
    ".cs", ".rb", ".php", ".swift", ".kt",
    ".html", ".css", ".sql", ".sh",
}

# Folders that add noise and should never be indexed
IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__",
    "venv", ".venv", "dist", "build", ".idea", ".vscode",
}


def is_indexable(path: Path) -> bool:
    """True if the file has a known code extension and isn't inside an ignored folder."""
    if any(part in IGNORED_DIRS for part in path.parts):
        return False
    return path.suffix in CODE_EXTENSIONS


def read_source_files(repo_path: str) -> list[dict]:
    """
    Walk the repo and return all readable source files.

    Each item: { file_path, language, content }
    """
    root   = Path(repo_path).resolve()
    result = []

    for file in root.rglob("*"):
        if not file.is_file() or not is_indexable(file.relative_to(root)):
            continue
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue
            result.append({
                "file_path": str(file.relative_to(root)),
                "language":  file.suffix.lstrip("."),
                "content":   content,
            })
        except Exception as e:
            print(f"[git_reader] skipping {file.name}: {e}")

    return result


def read_commits(repo_path: str, limit: int = 20) -> list[dict]:
    """
    Return the most recent commits from the repo.

    Each item: { hash, author, date, message }
    Returns an empty list if the path isn't a git repository.
    """
    try:
        repo = git.Repo(repo_path)
        return [
            {
                "hash":    commit.hexsha[:8],
                "author":  str(commit.author),
                "date":    commit.committed_datetime.strftime("%Y-%m-%d"),
                "message": commit.message.strip(),
            }
            for commit in repo.iter_commits(max_count=limit)
        ]
    except git.InvalidGitRepositoryError:
        print(f"[git_reader] not a git repo — skipping commits")
        return []