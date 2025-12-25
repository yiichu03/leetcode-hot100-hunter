import subprocess
from typing import Iterable, List


def _run_git(args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def git_add(paths: Iterable[str]) -> subprocess.CompletedProcess:
    return _run_git(["add", *paths])


def git_commit(message: str) -> subprocess.CompletedProcess:
    return _run_git(["commit", "-m", message])


def git_add_commit(paths: Iterable[str], message: str) -> subprocess.CompletedProcess:
    add_result = git_add(paths)
    if add_result.returncode != 0:
        return add_result
    return git_commit(message)


def git_push() -> subprocess.CompletedProcess:
    return _run_git(["push"])
