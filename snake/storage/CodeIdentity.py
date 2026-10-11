"""Identify the code that produced a saved artifact or report."""

import hashlib
from pathlib import Path
import subprocess


def code_identity():
    """Identify both the Git revision and the current Python source files."""
    project_root = Path(__file__).resolve().parents[2]
    try:
        revision = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
        git_commit = revision.stdout.strip() if revision.returncode == 0 else None
    except OSError:
        git_commit = None
    source_hash = hashlib.sha256()
    for source_path in sorted((project_root / "snake").rglob("*.py")):
        source_hash.update(str(source_path.relative_to(project_root)).encode())
        source_hash.update(b"\0")
        source_hash.update(source_path.read_bytes())

    return {
        "git_commit": git_commit,
        "source_sha256": source_hash.hexdigest(),
    }
