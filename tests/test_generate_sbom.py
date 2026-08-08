import json
import hashlib
from pathlib import Path

import pytest

from scripts import generate_sbom


REPO_ROOT = Path(__file__).resolve().parents[1]
MIT_LICENSE_TEXT = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
LOCK_TEXT = "pytest==9.0.3 \\\n    --hash=sha256:" + "a" * 64 + "\n"


def source_record(path: str, content: str) -> dict:
    data = content.encode("utf-8")
    return {"path": path, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_manifest() -> dict:
    return {
        "repository": "esj1123/codex-dev-harness",
        "git_ref": "main",
        "git_commit": "abc123",
        "git_tag": None,
        "files": [
            {"path": "README.md", "size_bytes": 10, "sha256": "a" * 64},
            {"path": "docs/RELEASE_BUNDLE_POLICY.md", "size_bytes": 20, "sha256": "b" * 64},
            source_record("LICENSE", MIT_LICENSE_TEXT),
            source_record("requirements-dev.lock", LOCK_TEXT),
        ],
    }


def write_manifest(repo_root: Path) -> Path:
    (repo_root / "LICENSE").write_bytes(MIT_LICENSE_TEXT.encode("utf-8"))
    (repo_root / "requirements-dev.lock").write_bytes(LOCK_TEXT.encode("utf-8"))
    manifest_path = repo_root / "artifacts" / "release-manifest.json"
    write(manifest_path, json.dumps(sample_manifest()) + "\n")
    return manifest_path


def assert_path_rejected(repo_root: Path, path_arg: str, flag_name: str, expected: str) -> None:
    try:
        generate_sbom.resolve_artifact_path(repo_root, path_arg, flag_name)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"{flag_name} path should be rejected: {path_arg}")


def assert_sbom_paths_rejected(
    repo_root: Path,
    manifest_path: Path,
    spdx_path: Path,
    cyclonedx_path: Path,
    expected: str,
) -> None:
    try:
        generate_sbom.validate_sbom_paths(repo_root, manifest_path, spdx_path, cyclonedx_path)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError("SBOM paths should be rejected")


def test_spdx_uses_manifest_files_and_repository_license(tmp_path: Path) -> None:
    manifest_path = write_manifest(tmp_path)
    spdx = generate_sbom.build_spdx(sample_manifest(), manifest_path, tmp_path, "2026-01-01T00:00:00Z")

    assert spdx["spdxVersion"] == "SPDX-2.3"
    assert any(file_entry["fileName"] == "README.md" for file_entry in spdx["files"])
    repository_package = next(package for package in spdx["packages"] if package["name"] == "esj1123/codex-dev-harness")
    assert repository_package["licenseDeclared"] == "MIT"
    assert repository_package["licenseConcluded"] == "MIT"
    assert repository_package["copyrightText"] == "Copyright (c) 2026 esj1123"
    assert any(package["name"] == "pytest" and package["licenseDeclared"] == "UNKNOWN" for package in spdx["packages"])
    assert "checksum_entries" not in spdx["annotations"][0]["comment"]


def test_cyclonedx_uses_manifest_files_and_dev_dependencies(tmp_path: Path) -> None:
    manifest_path = write_manifest(tmp_path)
    cdx = generate_sbom.build_cyclonedx(sample_manifest(), manifest_path, tmp_path, "2026-01-01T00:00:00Z")

    assert cdx["bomFormat"] == "CycloneDX"
    assert cdx["metadata"]["component"]["name"] == "esj1123/codex-dev-harness"
    assert cdx["metadata"]["component"]["licenses"] == [{"license": {"id": "MIT"}}]
    assert any(component["type"] == "file" and component["name"] == "README.md" for component in cdx["components"])
    assert any(component["type"] == "library" and component["name"] == "pytest" for component in cdx["components"])
    assert all(
        property_entry["name"] != "checksum_entries"
        for property_entry in cdx["metadata"]["component"]["properties"]
    )


def test_sbom_bytes_do_not_depend_on_checksum_file_state(tmp_path: Path) -> None:
    manifest_path = write_manifest(tmp_path)
    checksum_path = tmp_path / "artifacts" / "checksums.sha256"
    created = "2026-01-01T00:00:00Z"

    def rendered() -> tuple[bytes, bytes]:
        spdx = generate_sbom.build_spdx(sample_manifest(), manifest_path, tmp_path, created)
        cdx = generate_sbom.build_cyclonedx(sample_manifest(), manifest_path, tmp_path, created)
        return (
            (json.dumps(spdx, indent=2) + "\n").encode("utf-8"),
            (json.dumps(cdx, indent=2) + "\n").encode("utf-8"),
        )

    absent = rendered()
    write(checksum_path, "0" * 64 + "  artifacts/release-manifest.json\n")
    stale = rendered()
    write(checksum_path, "f" * 64 + "  artifacts/release-manifest.json\n")
    current = rendered()

    assert absent == stale == current


def test_current_repository_license_is_detected_as_mit() -> None:
    assert generate_sbom.detect_repository_license(REPO_ROOT) == ("MIT", "Copyright (c) 2026 esj1123")


@pytest.mark.parametrize("license_text", [None, "Custom license\n"])
def test_repository_license_detection_defaults_to_unknown(tmp_path: Path, license_text: str | None) -> None:
    if license_text is not None:
        write(tmp_path / "LICENSE", license_text)

    assert generate_sbom.detect_repository_license(tmp_path) == ("UNKNOWN", "UNKNOWN")


def test_sbom_writers_use_final_newline(tmp_path: Path) -> None:
    output = tmp_path / "artifacts" / "sbom.spdx.json"

    generate_sbom.write_json({"name": "test"}, output)

    assert output.read_text(encoding="utf-8").endswith("\n")


def test_sbom_rejects_paths_outside_artifacts(tmp_path: Path) -> None:
    for flag_name in ["--manifest", "--spdx", "--cyclonedx"]:
        for path_arg in ["STATUS.md", "docs/sbom.json", "scripts/generate_sbom.py"]:
            assert_path_rejected(tmp_path, path_arg, flag_name, "artifacts/")


def test_sbom_rejects_absolute_paths(tmp_path: Path) -> None:
    absolute_path = str(tmp_path / "artifacts" / "sbom.spdx.json")

    assert_path_rejected(tmp_path, absolute_path, "--spdx", "relative path")


def test_sbom_rejects_parent_traversal(tmp_path: Path) -> None:
    assert_path_rejected(tmp_path, "../sbom.spdx.json", "--spdx", "parent traversal")


def test_sbom_rejects_overlapping_artifact_paths(tmp_path: Path) -> None:
    manifest_path = tmp_path / "artifacts" / "release-manifest.json"
    checksums_path = tmp_path / "artifacts" / "checksums.sha256"
    checksums_txt_path = tmp_path / "artifacts" / "checksums.txt"
    provenance_path = tmp_path / "artifacts" / "provenance.intoto.jsonl"
    spdx_path = tmp_path / "artifacts" / "sbom.spdx.json"
    cyclonedx_path = tmp_path / "artifacts" / "sbom.cdx.json"

    generate_sbom.validate_sbom_paths(tmp_path, manifest_path, spdx_path, cyclonedx_path)
    generate_sbom.validate_sbom_paths(
        tmp_path,
        manifest_path,
        tmp_path / "artifacts" / "custom-spdx.json",
        tmp_path / "artifacts" / "custom-cyclonedx.json",
    )
    assert_sbom_paths_rejected(tmp_path, manifest_path, manifest_path, cyclonedx_path, "--manifest")
    assert_sbom_paths_rejected(tmp_path, manifest_path, checksums_path, cyclonedx_path, "reserved release artifact")
    assert_sbom_paths_rejected(tmp_path, manifest_path, checksums_txt_path, cyclonedx_path, "reserved release artifact")
    assert_sbom_paths_rejected(tmp_path, manifest_path, provenance_path, cyclonedx_path, "reserved release artifact")
    assert_sbom_paths_rejected(tmp_path, manifest_path, spdx_path, manifest_path, "--manifest")
    assert_sbom_paths_rejected(tmp_path, manifest_path, spdx_path, checksums_path, "reserved release artifact")
    assert_sbom_paths_rejected(tmp_path, manifest_path, spdx_path, spdx_path, "reserved release artifact")

    for reserved in [
        manifest_path,
        checksums_path,
        checksums_txt_path,
        provenance_path,
        tmp_path / "artifacts" / "eval-report.json",
        cyclonedx_path,
    ]:
        assert_sbom_paths_rejected(
            tmp_path,
            manifest_path,
            reserved,
            cyclonedx_path,
            "manifest" if reserved == manifest_path else "reserved release artifact",
        )


@pytest.mark.parametrize("relative_path", ["LICENSE", "requirements-dev.lock"])
def test_sbom_rejects_source_bytes_outside_manifest_basis(
    tmp_path: Path, relative_path: str
) -> None:
    manifest_path = write_manifest(tmp_path)
    (tmp_path / relative_path).write_bytes(b"tampered\n")

    with pytest.raises(ValueError, match="manifest source basis"):
        generate_sbom.build_spdx(
            sample_manifest(), manifest_path, tmp_path, "2026-01-01T00:00:00Z"
        )
