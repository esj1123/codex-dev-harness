"""Build safe Python semantic summaries and compare contract surfaces."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Iterable


SCHEMA_VERSION = "1"
MAX_SOURCE_BYTES = 1024 * 1024
REASON_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,79}$")


class SemanticInputError(ValueError):
    """Raised when a semantic input cannot be inspected safely."""


def _safe_python_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or not value.endswith(".py"):
        return False
    if not value.isascii() or "\\" in value or "://" in value:
        return False
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return False
    candidate = PurePosixPath(value)
    return (
        not candidate.is_absolute()
        and candidate.as_posix() == value
        and all(part not in ("", ".", "..") for part in candidate.parts)
        and not value.endswith("/")
    )


def _read_python_source(repo_root: Path, relative_path: str) -> str:
    if not _safe_python_path(relative_path):
        raise SemanticInputError("PYTHON_PATH_INVALID")

    try:
        root = repo_root.resolve(strict=True)
    except OSError as exc:
        raise SemanticInputError("REPOSITORY_ROOT_INVALID") from exc
    if not root.is_dir():
        raise SemanticInputError("REPOSITORY_ROOT_INVALID")

    candidate = root
    for part in PurePosixPath(relative_path).parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise SemanticInputError("PYTHON_SYMLINK_NOT_ALLOWED")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
        info = resolved.stat()
    except FileNotFoundError as exc:
        raise SemanticInputError("PYTHON_FILE_MISSING") from exc
    except (OSError, ValueError) as exc:
        raise SemanticInputError("PYTHON_PATH_OUTSIDE_REPOSITORY") from exc
    if not stat.S_ISREG(info.st_mode):
        raise SemanticInputError("PYTHON_FILE_NOT_REGULAR")
    if info.st_size > MAX_SOURCE_BYTES:
        raise SemanticInputError("PYTHON_FILE_TOO_LARGE")
    try:
        return resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SemanticInputError("PYTHON_FILE_NOT_UTF8") from exc
    except OSError as exc:
        raise SemanticInputError("PYTHON_FILE_READ_FAILED") from exc


def _assigned_names(target: ast.expr) -> Iterable[str]:
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for child in target.elts:
            yield from _assigned_names(child)


def _top_level_symbols(tree: ast.Module) -> tuple[list[dict[str, str]], list[str]]:
    entries: list[tuple[str, str]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entries.append((node.name, "function"))
        elif isinstance(node, ast.ClassDef):
            entries.append((node.name, "class"))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                entries.extend((name, "variable") for name in _assigned_names(target))
        elif isinstance(node, ast.AnnAssign):
            entries.extend((name, "variable") for name in _assigned_names(node.target))

    public_entries = [(name, kind) for name, kind in entries if not name.startswith("_")]
    counts: dict[str, int] = {}
    for name, _kind in public_entries:
        counts[name] = counts.get(name, 0) + 1
    symbols = [
        {"kind": kind, "name": name}
        for name, kind in sorted(set(public_entries), key=lambda item: (item[0], item[1]))
    ]
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    return symbols, duplicates


def _imports(tree: ast.Module) -> list[str]:
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            values.add(module)
    return sorted(values)


def _reason_codes(tree: ast.Module) -> list[str]:
    return sorted(
        {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and REASON_CODE_PATTERN.fullmatch(node.value)
        }
    )


def summarize_python_files(repo_root: Path, relative_paths: Iterable[str]) -> dict[str, Any]:
    """Return a deterministic source-free summary of selected Python files."""

    paths = list(relative_paths)
    if not paths or len(paths) != len(set(paths)):
        raise SemanticInputError("PYTHON_FILE_SET_INVALID")

    files: list[dict[str, Any]] = []
    for relative_path in sorted(paths):
        source = _read_python_source(repo_root, relative_path)
        try:
            tree = ast.parse(source, filename=relative_path)
        except SyntaxError as exc:
            raise SemanticInputError("PYTHON_SYNTAX_INVALID") from exc
        symbols, duplicates = _top_level_symbols(tree)
        files.append(
            {
                "duplicate_top_level_definitions": duplicates,
                "imports": _imports(tree),
                "line_count": len(source.splitlines()),
                "path": relative_path,
                "public_top_level_symbols": symbols,
                "reason_code_values": _reason_codes(tree),
            }
        )

    content = {"files": files, "schema_version": SCHEMA_VERSION}
    canonical = json.dumps(
        content, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return {
        **content,
        "semantic_summary_id": hashlib.sha256(canonical).hexdigest(),
        "performed_actions": [],
    }


def _file_index(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = summary.get("files")
    if summary.get("schema_version") != SCHEMA_VERSION or not isinstance(files, list):
        raise SemanticInputError("SEMANTIC_SUMMARY_INVALID")
    index: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict) or not _safe_python_path(item.get("path")):
            raise SemanticInputError("SEMANTIC_SUMMARY_INVALID")
        path = str(item["path"])
        if path in index:
            raise SemanticInputError("SEMANTIC_SUMMARY_INVALID")
        expected = {
            "duplicate_top_level_definitions",
            "imports",
            "line_count",
            "path",
            "public_top_level_symbols",
            "reason_code_values",
        }
        if set(item) != expected:
            raise SemanticInputError("SEMANTIC_SUMMARY_INVALID")
        index[path] = item
    return index


def compare_semantic_summaries(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    """Compare safe summaries without exposing source text."""

    baseline_files = _file_index(baseline)
    candidate_files = _file_index(candidate)
    blockers: list[dict[str, Any]] = []

    all_paths = sorted(set(baseline_files) | set(candidate_files))
    for path in all_paths:
        categories: list[str] = []
        before = baseline_files.get(path)
        after = candidate_files.get(path)
        if before is None or after is None:
            categories.append("FILE_SET_CHANGED")
        else:
            if before["public_top_level_symbols"] != after["public_top_level_symbols"]:
                categories.append("PUBLIC_API_CHANGED")
            if before["reason_code_values"] != after["reason_code_values"]:
                categories.append("REASON_CODE_VOCABULARY_CHANGED")
            if before["imports"] != after["imports"]:
                categories.append("DEPENDENCY_SET_CHANGED")
            if after["duplicate_top_level_definitions"]:
                categories.append("DUPLICATE_TOP_LEVEL_DEFINITION")
        if categories:
            blockers.append({"categories": sorted(categories), "path": path})

    reason_codes = sorted(
        {category for blocker in blockers for category in blocker["categories"]}
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not blockers else "BLOCKED",
        "reason_codes": reason_codes,
        "blockers": blockers,
        "comparison_summary": {
            "baseline_file_count": len(baseline_files),
            "blocker_count": len(blockers),
            "candidate_file_count": len(candidate_files),
        },
        "performed_actions": [],
    }
