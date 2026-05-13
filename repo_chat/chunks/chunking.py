import ast
from pathlib import Path
from typing import List, Optional, Tuple

from repo_chat.chunks.consts import (
    BRACE_LANGUAGES,
    LANGUAGES_BY_SUFFIX,
    DEFAULT_MAX_CHUNK_LINES,
    BRACE_BLOCK_START,
    Language,
)
from repo_chat.chunks.structures import CodeChunk


def chunk_file(repo_path: Path, file_path: Path, max_chunk_lines: int = DEFAULT_MAX_CHUNK_LINES) -> List[CodeChunk]:
    language = language_for_file(file_path)
    relative_file = file_path.relative_to(repo_path).as_posix()
    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    if not lines:
        return []

    if language == Language.PYTHON:
        return _chunk_python(lines, relative_file, language, max_chunk_lines)

    if language in BRACE_LANGUAGES:
        return _chunk_brace_language(lines, relative_file, language, max_chunk_lines)

    return _chunk_line_ranges(lines, relative_file, language, max_chunk_lines)


def language_for_file(file_path: Path) -> Language:
    return LANGUAGES_BY_SUFFIX.get(file_path.suffix.lower(), Language.TEXT)


def _chunk_python(
    lines: List[str],
    relative_file: str,
    language: Language,
    max_chunk_lines: int,
) -> List[CodeChunk]:
    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError:
        return _chunk_line_ranges(lines, relative_file, language, max_chunk_lines)

    ranges: List[Tuple[int, int]] = []
    for node in tree.body:
        node_range = _python_node_range(node)
        if node_range is not None:
            ranges.append(node_range)

    return _chunks_from_structural_ranges(lines, relative_file, language, ranges, max_chunk_lines)


def _python_node_range(node: ast.AST) -> Optional[Tuple[int, int]]:
    if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
        return None

    start_line = node.lineno
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        decorator_lines = [decorator.lineno for decorator in node.decorator_list]
        if decorator_lines:
            start_line = min(decorator_lines)

    return start_line, node.end_lineno


def _chunk_brace_language(
    lines: List[str],
    relative_file: str,
    language: Language,
    max_chunk_lines: int,
) -> List[CodeChunk]:
    ranges: List[Tuple[int, int]] = []
    block_start: Optional[int] = None
    depth = 0
    saw_opening_brace = False

    for line_number, line in enumerate(lines, start=1):
        if block_start is None and _looks_like_brace_block_start(line):
            block_start = line_number
            depth = 0
            saw_opening_brace = False

        if block_start is None:
            continue

        opening_count = line.count("{")
        closing_count = line.count("}")
        saw_opening_brace = saw_opening_brace or opening_count > 0
        depth += opening_count - closing_count

        if saw_opening_brace and depth <= 0:
            ranges.append((block_start, line_number))
            block_start = None
            depth = 0
            saw_opening_brace = False

    return _chunks_from_structural_ranges(lines, relative_file, language, ranges, max_chunk_lines)


def _looks_like_brace_block_start(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith(("//", "/*", "*")):
        return False

    return BRACE_BLOCK_START.search(line) is not None


def _chunks_from_structural_ranges(
    lines: List[str],
    relative_file: str,
    language: Language,
    ranges: List[Tuple[int, int]],
    max_chunk_lines: int,
) -> List[CodeChunk]:
    chunks: List[CodeChunk] = []
    next_line = 1

    for start_line, end_line in _normalize_structural_ranges(ranges):
        if start_line > next_line:
            chunks.extend(
                _chunk_line_ranges(
                    lines,
                    relative_file,
                    language,
                    max_chunk_lines,
                    start_line=next_line,
                    end_line=start_line - 1,
                )
            )

        chunks.append(_make_chunk(lines, relative_file, language, start_line, end_line))
        next_line = end_line + 1

    if next_line <= len(lines):
        chunks.extend(
            _chunk_line_ranges(
                lines,
                relative_file,
                language,
                max_chunk_lines,
                start_line=next_line,
                end_line=len(lines),
            )
        )

    return [chunk for chunk in chunks if chunk.content.strip()]


def _normalize_structural_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    normalized_ranges: List[Tuple[int, int]] = []

    for start_line, end_line in sorted(ranges, key=lambda line_range: (line_range[0], -line_range[1])):
        if not normalized_ranges:
            normalized_ranges.append((start_line, end_line))
            continue

        previous_start_line, previous_end_line = normalized_ranges[-1]
        if start_line <= previous_end_line:
            normalized_ranges[-1] = (
                previous_start_line,
                max(previous_end_line, end_line),
            )
            continue

        normalized_ranges.append((start_line, end_line))

    return normalized_ranges


def _chunk_line_ranges(
    lines: List[str],
    relative_file: str,
    language: Language,
    max_chunk_lines: int,
    start_line: int = 1,
    end_line: Optional[int] = None,
) -> List[CodeChunk]:
    last_line = end_line or len(lines)
    chunks: List[CodeChunk] = []
    current_start = start_line

    while current_start <= last_line:
        current_end = min(current_start + max_chunk_lines - 1, last_line)
        split_line = _find_blank_line_split(lines, current_start, current_end)
        if split_line is not None and split_line > current_start:
            current_end = split_line - 1

        chunks.append(_make_chunk(lines, relative_file, language, current_start, current_end))
        current_start = current_end + 1

        while current_start <= last_line and not lines[current_start - 1].strip():
            current_start += 1

    return [chunk for chunk in chunks if chunk.content.strip()]


def _find_blank_line_split(lines: List[str], start_line: int, end_line: int) -> Optional[int]:
    if end_line >= len(lines):
        return None

    for line_number in range(end_line, start_line, -1):
        if not lines[line_number - 1].strip():
            return line_number

    return None


def _make_chunk(
    lines: List[str],
    relative_file: str,
    language: Language,
    start_line: int,
    end_line: int,
) -> CodeChunk:
    content = "\n".join(lines[start_line - 1 : end_line])
    return CodeChunk(
        content=content,
        file=relative_file,
        start_line=start_line,
        end_line=end_line,
        language=language,
    )
