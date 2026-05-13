from collections.abc import Callable, Iterator
import os
from pathlib import Path
from typing import Optional
from gitignore_parser import parse_gitignore

from repo_chat.indexer.consts import (
    BINARY_SUFFIXES,
    SKIPPED_DIRECTORIES
)

def iter_repository_files(repo_path: Path) -> Iterator[Path]:
    gitignore_matcher = _load_gitignore_matcher(repo_path)

    for current_root, dir_names, file_names in os.walk(repo_path):
        current_path = Path(current_root)
        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not _should_skip_path(repo_path, current_path / dir_name, gitignore_matcher)
        ]

        for file_name in file_names:
            file_path = current_path / file_name

            if _should_skip_path(repo_path, file_path, gitignore_matcher):
                continue

            if _looks_binary(file_path):
                continue

            yield file_path


def _load_gitignore_matcher(repo_path: Path) -> Optional[Callable[[str], bool]]:
    gitignore_path = repo_path / ".gitignore"
    if not gitignore_path.exists():
        return None

    return parse_gitignore(gitignore_path, base_dir=repo_path)


def _has_skipped_directory(repo_path: Path, file_path: Path) -> bool:
    relative_parts = file_path.relative_to(repo_path).parts
    return any(part in SKIPPED_DIRECTORIES for part in relative_parts)


def _should_skip_path(
    repo_path: Path,
    path: Path,
    gitignore_matcher: Optional[Callable[[str], bool]],
) -> bool:
    if _has_skipped_directory(repo_path, path):
        return True

    return gitignore_matcher is not None and gitignore_matcher(str(path))


def _looks_binary(file_path: Path) -> bool:
    if file_path.suffix.lower() in BINARY_SUFFIXES:
        return True

    try:
        sample = file_path.read_bytes()[:2048]
    except OSError:
        return True

    return b"\0" in sample
