"""Generate minimal local SBOM artifacts from a release manifest."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from typing import Any


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = "artifacts"
SCHEMA_VERSION = "1"
TOOL_NAME = "codex-dev-harness generate_sbom.py"
DEFAULT_CHECKSUMS_PATH = "artifacts/checksums.sha256"
MIT_LICENSE_ID = "MIT"
MIT_COPYRIGHT_TEXT = "Copyright (c) 2026 esj1123"
MIT_LICENSE_MARKERS = (
    "MIT License",
    MIT_COPYRIGHT_TEXT,
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    "The above copyright notice and this permission notice shall be included",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND',
)
PROTECTED_RELEASE_ARTIFACT_PATHS = [
    DEFAULT_CHECKSUMS_PATH,
    "artifacts/checksums.txt",
    "artifacts/provenance.intoto.jsonl",
]


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sanitize_spdx_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9.-]+", "-", value).strip("-")
    return safe or "unknown"


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


def validate_sbom_paths(repo_root: Path, manifest_path: Path, spdx_path: Path, cyclonedx_path: Path) -> None:
    protected_paths = [
        ("--manifest", manifest_path.resolve()),
    ]
    protected_paths.extend((relative_path, (repo_root / relative_path).resolve()) for relative_path in PROTECTED_RELEASE_ARTIFACT_PATHS)
    output_paths = [
        ("--spdx", spdx_path.resolve()),
        ("--cyclonedx", cyclonedx_path.resolve()),
    ]
    for output_name, output_path in output_paths:
        for protected_name, protected_path in protected_paths:
            if output_path == protected_path:
                raise ValueError(f"{output_name} must not overwrite {protected_name}")
    if output_paths[0][1] == output_paths[1][1]:
        raise ValueError("--spdx must not overlap --cyclonedx")


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def read_checksums(checksums_path: Path, repo_root: Path) -> list[dict[str, str]]:
    if not checksums_path.is_file():
        return []
    entries: list[dict[str, str]] = []
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, path = line.partition("  ")
        if digest and path:
            entries.append({"path": path, "sha256": digest})
    return sorted(entries, key=lambda entry: entry["path"])


def parse_requirement_line(line: str) -> dict[str, str] | None:
    value = line.strip()
    if not value or value.startswith("#") or value.startswith("-"):
        return None
    for separator in ["==", ">=", "<=", "~=", "!=", ">", "<"]:
        if separator in value:
            name, version = value.split(separator, 1)
            return {
                "name": name.strip(),
                "version": version.strip() or "UNKNOWN",
                "requirement": value,
                "license": "UNKNOWN",
            }
    return {
        "name": value,
        "version": "UNKNOWN",
        "requirement": value,
        "license": "UNKNOWN",
    }


def read_dev_dependencies(repo_root: Path) -> list[dict[str, str]]:
    requirements = repo_root / "requirements-dev.txt"
    if not requirements.is_file():
        return []
    dependencies = []
    for line in requirements.read_text(encoding="utf-8").splitlines():
        parsed = parse_requirement_line(line)
        if parsed:
            dependencies.append(parsed)
    return sorted(dependencies, key=lambda item: item["name"].lower())


def manifest_files(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    files = manifest.get("files", [])
    return sorted(files, key=lambda item: item.get("path", ""))


def repository_name(manifest: dict[str, Any]) -> str:
    repository = manifest.get("repository") or "UNKNOWN"
    return str(repository)


def detect_repository_license(repo_root: Path) -> tuple[str, str]:
    license_path = repo_root / "LICENSE"
    if not license_path.is_file():
        return "UNKNOWN", "UNKNOWN"
    try:
        license_text = license_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    except (OSError, UnicodeDecodeError):
        return "UNKNOWN", "UNKNOWN"
    if all(marker in license_text for marker in MIT_LICENSE_MARKERS):
        return MIT_LICENSE_ID, MIT_COPYRIGHT_TEXT
    return "UNKNOWN", "UNKNOWN"


def build_spdx(
    manifest: dict[str, Any],
    manifest_path: Path,
    repo_root: Path,
    checksums: list[dict[str, str]],
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or utc_now()
    repo_name = repository_name(manifest)
    repo_spdx_id = "SPDXRef-Package-codex-dev-harness"
    repo_license, repo_copyright = detect_repository_license(repo_root)
    dependencies = read_dev_dependencies(repo_root)
    files = manifest_files(manifest)

    packages = [
        {
            "name": repo_name,
            "SPDXID": repo_spdx_id,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "licenseConcluded": repo_license,
            "licenseDeclared": repo_license,
            "copyrightText": repo_copyright,
            "versionInfo": str(manifest.get("git_commit") or "UNKNOWN"),
        }
    ]
    for dependency in dependencies:
        packages.append(
            {
                "name": dependency["name"],
                "SPDXID": f"SPDXRef-Package-{sanitize_spdx_id(dependency['name'])}",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "UNKNOWN",
                "licenseDeclared": "UNKNOWN",
                "copyrightText": "UNKNOWN",
                "versionInfo": dependency["version"],
                "summary": f"Declared in requirements-dev.txt as {dependency['requirement']}",
            }
        )

    spdx_files = []
    relationships = [{"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": repo_spdx_id}]
    for entry in files:
        path = str(entry["path"])
        file_id = f"SPDXRef-File-{sanitize_spdx_id(path)}"
        spdx_files.append(
            {
                "fileName": path,
                "SPDXID": file_id,
                "checksums": [{"algorithm": "SHA256", "checksumValue": entry["sha256"]}],
                "licenseConcluded": "UNKNOWN",
                "copyrightText": "UNKNOWN",
            }
        )
        relationships.append({"spdxElementId": repo_spdx_id, "relationshipType": "CONTAINS", "relatedSpdxElement": file_id})

    manifest_digest = sha256_file(manifest_path)
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{repo_name} local release SBOM",
        "documentNamespace": f"https://example.invalid/codex-dev-harness/spdx/{manifest_digest}",
        "creationInfo": {
            "created": created,
            "creators": [f"Tool: {TOOL_NAME}"],
        },
        "documentComment": "Local-only SBOM generated from release-manifest.json; unknown licenses are recorded as UNKNOWN.",
        "packages": packages,
        "files": spdx_files,
        "relationships": relationships,
        "externalDocumentRefs": [],
        "annotations": [
            {
                "annotationDate": created,
                "annotationType": "OTHER",
                "annotator": f"Tool: {TOOL_NAME}",
                "comment": f"manifest={relpath(manifest_path, repo_root)} sha256={manifest_digest}; checksum_entries={len(checksums)}",
            }
        ],
    }


def build_cyclonedx(
    manifest: dict[str, Any],
    manifest_path: Path,
    repo_root: Path,
    checksums: list[dict[str, str]],
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or utc_now()
    repo_name = repository_name(manifest)
    repo_license, _ = detect_repository_license(repo_root)
    dependencies = read_dev_dependencies(repo_root)
    components: list[dict[str, Any]] = []

    for entry in manifest_files(manifest):
        components.append(
            {
                "type": "file",
                "name": str(entry["path"]),
                "hashes": [{"alg": "SHA-256", "content": entry["sha256"]}],
                "properties": [{"name": "size_bytes", "value": str(entry.get("size_bytes", "UNKNOWN"))}],
            }
        )
    for dependency in dependencies:
        component: dict[str, Any] = {
            "type": "library",
            "name": dependency["name"],
            "licenses": [{"license": {"name": "UNKNOWN"}}],
            "properties": [{"name": "declared_requirement", "value": dependency["requirement"]}],
        }
        if dependency["version"] != "UNKNOWN":
            component["version"] = dependency["version"]
        components.append(component)

    manifest_digest = sha256_file(manifest_path)
    repository_component: dict[str, Any] = {
        "type": "application",
        "name": repo_name,
        "version": str(manifest.get("git_commit") or "UNKNOWN"),
        "properties": [
            {"name": "git_ref", "value": str(manifest.get("git_ref") or "UNKNOWN")},
            {"name": "manifest_path", "value": relpath(manifest_path, repo_root)},
            {"name": "manifest_sha256", "value": manifest_digest},
            {"name": "checksum_entries", "value": str(len(checksums))},
        ],
    }
    if repo_license != "UNKNOWN":
        repository_component["licenses"] = [{"license": {"id": repo_license}}]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": created,
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "generate_sbom.py",
                        "version": SCHEMA_VERSION,
                    }
                ]
            },
            "component": repository_component,
        },
        "components": sorted(components, key=lambda item: (item["type"], item["name"])),
        "dependencies": [],
    }


def write_json(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate minimal local SPDX and CycloneDX SBOM artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--manifest", required=True, help="Repo-internal release manifest path under artifacts/")
    parser.add_argument("--spdx", default="artifacts/sbom.spdx.json", help="Repo-internal SPDX output path under artifacts/")
    parser.add_argument("--cyclonedx", default="artifacts/sbom.cdx.json", help="Repo-internal CycloneDX output path under artifacts/")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        manifest_path = resolve_artifact_path(repo_root, args.manifest, "--manifest")
        spdx_path = resolve_artifact_path(repo_root, args.spdx, "--spdx")
        cyclonedx_path = resolve_artifact_path(repo_root, args.cyclonedx, "--cyclonedx")
        validate_sbom_paths(repo_root, manifest_path, spdx_path, cyclonedx_path)
    except ValueError as exc:
        parser.error(str(exc))

    manifest = load_manifest(manifest_path)
    checksums = read_checksums(repo_root / DEFAULT_CHECKSUMS_PATH, repo_root)
    created = utc_now()
    write_json(build_spdx(manifest, manifest_path, repo_root, checksums, created), spdx_path)
    write_json(build_cyclonedx(manifest, manifest_path, repo_root, checksums, created), cyclonedx_path)
    print(f"Wrote SPDX SBOM: {relpath(spdx_path, repo_root)}")
    print(f"Wrote CycloneDX SBOM: {relpath(cyclonedx_path, repo_root)}")
    print(f"Manifest files represented: {len(manifest_files(manifest))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
