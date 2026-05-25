import json
from pathlib import Path

from scripts import generate_sbom


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
        ],
    }


def write_manifest(repo_root: Path) -> Path:
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


def test_spdx_uses_manifest_files_and_unknown_licenses(tmp_path: Path) -> None:
    manifest_path = write_manifest(tmp_path)
    write(tmp_path / "requirements-dev.txt", "pytest>=9\n")
    checksums = [{"path": "artifacts/release-manifest.json", "sha256": "c" * 64}]

    spdx = generate_sbom.build_spdx(sample_manifest(), manifest_path, tmp_path, checksums, "2026-01-01T00:00:00Z")

    assert spdx["spdxVersion"] == "SPDX-2.3"
    assert any(file_entry["fileName"] == "README.md" for file_entry in spdx["files"])
    assert any(package["name"] == "pytest" and package["licenseDeclared"] == "UNKNOWN" for package in spdx["packages"])
    assert "checksum_entries=1" in spdx["annotations"][0]["comment"]


def test_cyclonedx_uses_manifest_files_and_dev_dependencies(tmp_path: Path) -> None:
    manifest_path = write_manifest(tmp_path)
    write(tmp_path / "requirements-dev.txt", "pytest==9.0.3\n")

    cdx = generate_sbom.build_cyclonedx(sample_manifest(), manifest_path, tmp_path, [], "2026-01-01T00:00:00Z")

    assert cdx["bomFormat"] == "CycloneDX"
    assert cdx["metadata"]["component"]["name"] == "esj1123/codex-dev-harness"
    assert any(component["type"] == "file" and component["name"] == "README.md" for component in cdx["components"])
    assert any(component["type"] == "library" and component["name"] == "pytest" for component in cdx["components"])


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
