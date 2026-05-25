"""Generate minimal local in-toto-style provenance for release evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
from typing import Any


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = "artifacts"
SCHEMA_VERSION = "1"
TOOL_NAME = "codex-dev-harness generate_provenance.py"
DEFAULT_PRODUCTS = [
    "artifacts/release-manifest.json",
    "artifacts/checksums.sha256",
    "artifacts/sbom.spdx.json",
    "artifacts/sbom.cdx.json",
]
PROTECTED_OUTPUT_PATHS = DEFAULT_PRODUCTS + ["artifacts/checksums.txt"]
DEFAULT_COMMANDS = [
    "python scripts/generate_manifest.py --output artifacts/release-manifest.json",
    "python scripts/generate_checksums.py --manifest artifacts/release-manifest.json --output artifacts/checksums.sha256",
    "python scripts/generate_sbom.py --manifest artifacts/release-manifest.json --spdx artifacts/sbom.spdx.json --cyclonedx artifacts/sbom.cdx.json",
    "python scripts/generate_provenance.py --manifest artifacts/release-manifest.json --output artifacts/provenance.intoto.jsonl",
]


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_artifact_path(repo_root: Path, path_arg: str, flag_name: str) -> Path:
    raw_path = Path(path_arg)
    if raw_path.is_absolute() or raw_path.drive or raw_path.anchor:
        raise ValueError(f"{flag_name} must be a repo-internal relative path")
    if not raw_path.parts:
        raise ValueError(f"{flag_name} must name a file")
    if any(part == ".." for part in raw_path.parts):
        raise ValueError(f"{flag_name} must not contain parent traversal")
    if raw_path.parts[0] != ARTIFACTS_ROOT or len(raw_path.parts) < 2:
        raise ValueError(f"{flag_name} must be under artifacts/")
    resolved_root = repo_root.resolve()
    resolved_path = (resolved_root / raw_path).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{flag_name} must resolve inside the repository") from exc
    if resolved_path == resolved_root:
        raise ValueError(f"{flag_name} must name a file")
    return resolved_path


def validate_provenance_paths(repo_root: Path, manifest_path: Path, output_path: Path) -> None:
    protected_paths = [("--manifest", manifest_path.resolve())]
    protected_paths.extend((relative_path, (repo_root / relative_path).resolve()) for relative_path in PROTECTED_OUTPUT_PATHS)
    for protected_name, protected_path in protected_paths:
        if output_path.resolve() == protected_path:
            raise ValueError(f"--output must not overwrite {protected_name}")


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def read_checksums(checksums_path: Path) -> list[dict[str, str]]:
    if not checksums_path.is_file():
        return []
    entries = []
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, path = line.partition("  ")
        if digest and path:
            entries.append({"path": path, "sha256": digest})
    return sorted(entries, key=lambda entry: entry["path"])


def digest_record(path: Path, repo_root: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return {
        "name": relpath(path, repo_root),
        "digest": {"sha256": sha256_file(path)},
    }


def manifest_materials(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    materials = []
    for entry in sorted(manifest.get("files", []), key=lambda item: item.get("path", "")):
        materials.append(
            {
                "name": str(entry["path"]),
                "digest": {"sha256": str(entry["sha256"])},
            }
        )
    return materials


def existing_products(repo_root: Path, output_path: Path) -> list[dict[str, Any]]:
    products = []
    for relative in DEFAULT_PRODUCTS:
        path = (repo_root / relative).resolve()
        if path == output_path.resolve():
            continue
        record = digest_record(path, repo_root)
        if record:
            products.append(record)
    return sorted(products, key=lambda item: item["name"])


def build_statement(
    manifest: dict[str, Any],
    manifest_path: Path,
    output_path: Path,
    repo_root: Path,
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or utc_now()
    checksums_path = repo_root / "artifacts" / "checksums.sha256"
    manifest_digest = sha256_file(manifest_path)
    products = existing_products(repo_root, output_path)
    checksum_entries = read_checksums(checksums_path)

    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": products,
        "predicateType": "https://codex-dev-harness.local/provenance/v1",
        "predicate": {
            "schema_version": SCHEMA_VERSION,
            "local_only": True,
            "builder": {
                "id": "codex-dev-harness-local",
                "tool": TOOL_NAME,
            },
            "repo": {
                "repository": str(manifest.get("repository") or "UNKNOWN"),
                "git_ref": str(manifest.get("git_ref") or "UNKNOWN"),
                "git_commit": str(manifest.get("git_commit") or "UNKNOWN"),
                "git_tag": manifest.get("git_tag"),
            },
            "python_version": platform.python_version(),
            "build_started_on": created,
            "build_finished_on": created,
            "commands": DEFAULT_COMMANDS,
            "input_manifest": {
                "path": relpath(manifest_path, repo_root),
                "digest": {"sha256": manifest_digest},
            },
            "checksum_entries": checksum_entries,
            "materials": manifest_materials(manifest),
            "products": products,
            "notes": [
                "Local-only provenance generated without host identifiers or external service calls.",
                "The provenance file does not include its own digest to avoid self-reference.",
            ],
        },
    }


def write_jsonl(statement: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(statement, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate minimal local in-toto-style provenance.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--manifest", required=True, help="Repo-internal release manifest path under artifacts/")
    parser.add_argument("--output", default="artifacts/provenance.intoto.jsonl", help="Repo-internal provenance output path under artifacts/")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        manifest_path = resolve_artifact_path(repo_root, args.manifest, "--manifest")
        output_path = resolve_artifact_path(repo_root, args.output, "--output")
        validate_provenance_paths(repo_root, manifest_path, output_path)
    except ValueError as exc:
        parser.error(str(exc))

    manifest = load_manifest(manifest_path)
    statement = build_statement(manifest, manifest_path, output_path, repo_root)
    write_jsonl(statement, output_path)
    print(f"Wrote provenance: {relpath(output_path, repo_root)}")
    print(f"Provenance subjects: {len(statement['subject'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
