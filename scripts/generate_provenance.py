"""Generate minimal local in-toto-style provenance for release evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
from typing import Any

try:
    from scripts import generate_checksums as release_artifacts
    from scripts import generate_manifest
except ImportError:  # Direct script execution from scripts/.
    import generate_checksums as release_artifacts
    import generate_manifest


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = "artifacts"
SCHEMA_VERSION = "1"
TOOL_NAME = "codex-dev-harness generate_provenance.py"
DEFAULT_PRODUCTS = [
    release_artifacts.DEFAULT_MANIFEST_PATH,
    "artifacts/sbom.spdx.json",
    "artifacts/sbom.cdx.json",
]
DEFAULT_PROVENANCE_PATH = "artifacts/provenance.intoto.jsonl"
DEFAULT_COMMANDS = [
    "python scripts/generate_manifest.py --output artifacts/release-manifest.json",
    "python scripts/generate_sbom.py --manifest artifacts/release-manifest.json --spdx artifacts/sbom.spdx.json --cyclonedx artifacts/sbom.cdx.json",
    "python scripts/generate_provenance.py --manifest artifacts/release-manifest.json --output artifacts/provenance.intoto.jsonl",
    "python scripts/generate_checksums.py --manifest artifacts/release-manifest.json --output artifacts/checksums.sha256",
    "python scripts/generate_checksums.py --verify",
]


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_artifact_path(repo_root: Path, path_arg: str, flag_name: str) -> Path:
    return release_artifacts.resolve_repo_path(repo_root, path_arg, flag_name)


def validate_provenance_paths(repo_root: Path, manifest_path: Path, output_path: Path) -> None:
    if output_path.resolve() == manifest_path.resolve():
        raise ValueError("--output must not overwrite --manifest")
    release_artifacts.validate_release_output_path(
        repo_root,
        output_path,
        allowed_reserved_paths=(DEFAULT_PROVENANCE_PATH,),
        flag_name="--output",
    )


def digest_record(path: Path, repo_root: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    release_artifacts.validate_physical_path(
        repo_root, path, "provenance product", require_file=True
    )
    return {
        "name": relpath(path, repo_root),
        "digest": {"sha256": release_artifacts.sha256_file(path)},
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


def existing_products(
    snapshot: generate_manifest.ValidatedManifestSnapshot,
    repo_root: Path,
    output_path: Path,
) -> list[dict[str, Any]]:
    products = [
        {
            "name": relpath(snapshot.manifest_path, repo_root),
            "digest": {"sha256": snapshot.canonical_sha256},
        }
    ]
    for relative in DEFAULT_PRODUCTS[1:]:
        path = release_artifacts.release_artifact_path(repo_root, relative)
        if path == output_path.resolve():
            continue
        record = digest_record(path, repo_root)
        if record:
            products.append(record)
    return sorted(products, key=lambda item: item["name"])


def build_statement(
    snapshot: generate_manifest.ValidatedManifestSnapshot,
    output_path: Path,
    repo_root: Path,
    created_at: str | None = None,
) -> dict[str, Any]:
    manifest = snapshot.manifest
    manifest_path = snapshot.manifest_path
    created = created_at or utc_now()
    manifest_digest = snapshot.canonical_sha256
    products = existing_products(snapshot, repo_root, output_path)
    checksum_entries = [
        {
            "path": str(product["name"]),
            "sha256": str(product["digest"]["sha256"]),
        }
        for product in products
    ]

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
    release_artifacts.write_artifact_bytes(
        output_path, (json.dumps(statement, sort_keys=True) + "\n").encode("utf-8")
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate minimal local in-toto-style provenance.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--manifest", required=True, help="Repo-internal release manifest path under artifacts/")
    parser.add_argument("--output", default=DEFAULT_PROVENANCE_PATH, help="Repo-internal provenance output path under artifacts/")
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

    try:
        snapshot = generate_manifest.load_validated_manifest_snapshot(
            repo_root, manifest_path
        )
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))
    statement = build_statement(snapshot, output_path, repo_root)
    write_jsonl(statement, output_path)
    print(f"Wrote provenance: {relpath(output_path, repo_root)}")
    print(f"Provenance subjects: {len(statement['subject'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
