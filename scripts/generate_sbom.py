"""Generate minimal local SBOM artifacts from a release manifest."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from typing import Any

try:
    from scripts import generate_checksums as release_artifacts
    from scripts import verify_dev_environment
except ImportError:  # Direct script execution from scripts/.
    import generate_checksums as release_artifacts
    import verify_dev_environment


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = "artifacts"
SCHEMA_VERSION = "1"
TOOL_NAME = "codex-dev-harness generate_sbom.py"
DEFAULT_MANIFEST_PATH = "artifacts/release-manifest.json"
DEFAULT_SPDX_PATH = "artifacts/sbom.spdx.json"
DEFAULT_CYCLONEDX_PATH = "artifacts/sbom.cdx.json"
MIT_LICENSE_ID = "MIT"
MIT_COPYRIGHT_TEXT = "Copyright (c) 2026 esj1123"
MIT_LICENSE_MARKERS = (
    "MIT License",
    MIT_COPYRIGHT_TEXT,
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    "The above copyright notice and this permission notice shall be included",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND',
)
def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sanitize_spdx_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9.-]+", "-", value).strip("-")
    return safe or "unknown"


def resolve_artifact_path(repo_root: Path, path_arg: str, flag_name: str) -> Path:
    return release_artifacts.resolve_repo_path(repo_root, path_arg, flag_name)


def validate_sbom_paths(repo_root: Path, manifest_path: Path, spdx_path: Path, cyclonedx_path: Path) -> None:
    if spdx_path.resolve() == manifest_path.resolve():
        raise ValueError("--spdx must not overwrite --manifest")
    if cyclonedx_path.resolve() == manifest_path.resolve():
        raise ValueError("--cyclonedx must not overwrite --manifest")
    release_artifacts.validate_release_output_path(
        repo_root,
        spdx_path,
        allowed_reserved_paths=(DEFAULT_SPDX_PATH,),
        flag_name="--spdx",
    )
    release_artifacts.validate_release_output_path(
        repo_root,
        cyclonedx_path,
        allowed_reserved_paths=(DEFAULT_CYCLONEDX_PATH,),
        flag_name="--cyclonedx",
    )
    if spdx_path.resolve() == cyclonedx_path.resolve():
        raise ValueError("--spdx must not overlap --cyclonedx")


def sha256_file(path: Path) -> str:
    return sha256_bytes(
        release_artifacts.read_regular_file(
            release_artifacts.infer_repo_root(path), path
        )
    )


def load_manifest(manifest_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or release_artifacts.infer_repo_root(manifest_path)
    data = release_artifacts.read_regular_file(root, manifest_path, "--manifest")
    return json.loads(data.decode("utf-8"))


def manifest_source_bytes(
    manifest: dict[str, Any], repo_root: Path, relative_path: str
) -> bytes:
    matches = [
        entry for entry in manifest.get("files", []) if entry.get("path") == relative_path
    ]
    if len(matches) != 1:
        raise ValueError(f"manifest must contain exactly one {relative_path} source record")
    source_path = repo_root / relative_path
    data = release_artifacts.read_regular_file(repo_root, source_path, relative_path)
    expected = matches[0]
    if expected.get("size_bytes") != len(data) or expected.get("sha256") != sha256_bytes(data):
        raise ValueError(f"{relative_path} bytes do not match the manifest source basis")
    return data


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def read_dev_dependencies(
    repo_root: Path, manifest: dict[str, Any]
) -> list[dict[str, str]]:
    try:
        lock_text = manifest_source_bytes(
            manifest, repo_root, "requirements-dev.lock"
        ).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("requirements-dev.lock is not UTF-8") from exc
    locked = verify_dev_environment.parse_lock_text(lock_text)
    return [
        {
            "name": item.name,
            "version": item.version,
            "requirement": item.requirement,
            "license": "UNKNOWN",
        }
        for _, item in sorted(locked.items())
    ]


def manifest_files(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    files = manifest.get("files", [])
    return sorted(files, key=lambda item: item.get("path", ""))


def repository_name(manifest: dict[str, Any]) -> str:
    repository = manifest.get("repository") or "UNKNOWN"
    return str(repository)


def detect_repository_license(
    repo_root: Path, manifest: dict[str, Any] | None = None
) -> tuple[str, str]:
    if manifest is not None:
        license_text = (
            manifest_source_bytes(manifest, repo_root, "LICENSE")
            .decode("utf-8")
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )
        if all(marker in license_text for marker in MIT_LICENSE_MARKERS):
            return MIT_LICENSE_ID, MIT_COPYRIGHT_TEXT
        return "UNKNOWN", "UNKNOWN"
    try:
        license_bytes = release_artifacts.read_regular_file(
            repo_root, repo_root / "LICENSE", "LICENSE"
        )
        license_text = license_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    except (OSError, ValueError, UnicodeDecodeError, FileNotFoundError):
        return "UNKNOWN", "UNKNOWN"
    if all(marker in license_text for marker in MIT_LICENSE_MARKERS):
        return MIT_LICENSE_ID, MIT_COPYRIGHT_TEXT
    return "UNKNOWN", "UNKNOWN"


def build_spdx(
    manifest: dict[str, Any],
    manifest_path: Path,
    repo_root: Path,
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or utc_now()
    repo_name = repository_name(manifest)
    repo_spdx_id = "SPDXRef-Package-codex-dev-harness"
    repo_license, repo_copyright = detect_repository_license(repo_root, manifest)
    dependencies = read_dev_dependencies(repo_root, manifest)
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
                "summary": f"Declared in requirements-dev.lock as {dependency['requirement']}",
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
                "comment": f"manifest={relpath(manifest_path, repo_root)} sha256={manifest_digest}",
            }
        ],
    }


def build_cyclonedx(
    manifest: dict[str, Any],
    manifest_path: Path,
    repo_root: Path,
    created_at: str | None = None,
) -> dict[str, Any]:
    created = created_at or utc_now()
    repo_name = repository_name(manifest)
    repo_license, _ = detect_repository_license(repo_root, manifest)
    dependencies = read_dev_dependencies(repo_root, manifest)
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
    release_artifacts.write_artifact_bytes(
        output_path, (json.dumps(data, indent=2) + "\n").encode("utf-8")
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate minimal local SPDX and CycloneDX SBOM artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--manifest", required=True, help="Repo-internal release manifest path under artifacts/")
    parser.add_argument("--spdx", default=DEFAULT_SPDX_PATH, help="Repo-internal SPDX output path under artifacts/")
    parser.add_argument("--cyclonedx", default=DEFAULT_CYCLONEDX_PATH, help="Repo-internal CycloneDX output path under artifacts/")
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

    manifest = load_manifest(manifest_path, repo_root)
    created = utc_now()
    write_json(build_spdx(manifest, manifest_path, repo_root, created), spdx_path)
    write_json(build_cyclonedx(manifest, manifest_path, repo_root, created), cyclonedx_path)
    print(f"Wrote SPDX SBOM: {relpath(spdx_path, repo_root)}")
    print(f"Wrote CycloneDX SBOM: {relpath(cyclonedx_path, repo_root)}")
    print(f"Manifest files represented: {len(manifest_files(manifest))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
