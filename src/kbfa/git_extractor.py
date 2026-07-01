import git
from pathlib import Path


def get_blame_records(repo_path: str) -> list[dict]:
    """
    Open a git repo at repo_path and run git blame on every tracked text file.

    Returns a list of records, one per (file, author) combination:
    [
        {"file": "auth.py", "author": "Alice", "email": "alice@example.com", "line_count": 19},
        {"file": "auth.py", "author": "Bob",   "email": "bob@example.com",   "line_count": 1},
        ...
    ]

    Why blame and not git log --numstat?
    - git log --numstat tells you: "who historically added/removed lines"
    - git blame tells you: "who currently owns the lines sitting in the file TODAY"
    - Your risk metric is about current state ("if Alice leaves, 95% of auth.py
      has no owner"), so blame is the correct tool.
    """
    repo = git.Repo(repo_path)

    # Collect all file paths currently tracked by git (i.e., in the latest commit).
    # repo.tree() gives the file tree at HEAD (latest commit).
    # We only want files, not folders, so we use item.type == "blob".
    tracked_files = [
        item.path
        for item in repo.tree().traverse()
        if item.type == "blob"
    ]

    results = []

    for file_path in tracked_files:
        # Skip binary files (images, compiled artifacts, etc.).
        # git blame on a binary file produces garbage output.
        if _is_binary(repo_path, file_path):
            continue

        try:
            blame_output = repo.blame("HEAD", file_path)
        except git.GitCommandError:
            # Some files (empty files, submodules) can't be blamed — skip them.
            continue

        # blame_output is a list of [commit, lines] pairs.
        # Each pair means: "this commit authored these lines."
        # We count how many lines each author owns across the whole file.
        author_line_counts = {}

        for commit, lines in blame_output:
            author = commit.author.name
            email = commit.author.email
            key = (author, email)
            author_line_counts[key] = author_line_counts.get(key, 0) + len(lines)

        # Turn the counted dict into individual records, one per author.
        for (author, email), line_count in author_line_counts.items():
            results.append({
                "file": file_path,
                "author": author,
                "email": email,
                "line_count": line_count,
            })

    return results


def _is_binary(repo_path: str, file_path: str) -> bool:
    """
    Return True if the file looks binary (not safe to blame).
    Simple heuristic: try reading the first 8000 bytes and check
    for null bytes — that's the same trick git itself uses internally.
    """
    full_path = Path(repo_path) / file_path
    try:
        with open(full_path, "rb") as f:
            chunk = f.read(8000)
        return b"\x00" in chunk
    except (OSError, PermissionError):
        return True