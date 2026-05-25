import json
from pathlib import Path

from scripts import generate_manifest


def write(path: Path, content: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def assert_output_rejected(repo_root: Path, output_arg: str, expected: str) -> None:
    try:
        generate_manifest.resolve_output_path(repo_root, output_arg)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"output path should be rejected: {output_arg}")


def test_manifest_excludes_generated_and_temporary_directories(tmp_path: Path) -> None:
    write(tmp_path / "README.md")
    write(tmp_path / "docs" / "policy.md")
    write(tmp_path / "artifacts" / "release-manifest.json")
    write(tmp_path / ".git" / "config")
    write(tmp_path / ".pytest_cache" / "cache")
    write(tmp_path / "__pycache__" / "module.pyc")
    write(tmp_path / "local" / "scratch.md")

    manifest = generate_manifest.build_manifest(tmp_path)
    paths = [entry["path"] for entry in manifest["files"]]

    assert "README.md" in paths
    assert "docs/policy.md" in paths
    assert not any(path.startswith("artifacts/") for path in paths)
    assert not any(path.startswith(".git/") for path in paths)
    assert not any(path.startswith(".pytest_cache/") for path in paths)
    assert not any(path.startswith("__pycache__/") for path in paths)
    assert not any(path.startswith("local/") for path in paths)


def test_manifest_file_list_is_sorted(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "z.md")
    write(tmp_path / "docs" / "a.md")
    write(tmp_path / "README.md")

    manifest = generate_manifest.build_manifest(tmp_path)
    paths = [entry["path"] for entry in manifest["files"]]

    assert paths == sorted(paths)


def test_manifest_has_required_top_level_fields(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "hello\n")

    manifest = generate_manifest.build_manifest(tmp_path)

    for field in [
        "schema_version",
        "generated_at_utc",
        "repository",
        "git_ref",
        "git_commit",
        "git_tag",
        "python_version",
        "included_roots",
        "excluded_patterns",
        "verification_commands",
        "quality_gates",
        "eval_summary",
        "example_render_dry_runs",
        "files",
    ]:
        assert field in manifest
    assert manifest["repository"] == "UNKNOWN"
    assert manifest["git_ref"] == "UNKNOWN"
    assert manifest["git_commit"] == "UNKNOWN"
    assert manifest["git_tag"] is None
    assert manifest["verification_commands"][0]["result"] == "NOT_RUN"


def test_manifest_file_records_include_size_and_sha256(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "hello\n")

    manifest = generate_manifest.build_manifest(tmp_path)
    readme = next(entry for entry in manifest["files"] if entry["path"] == "README.md")

    assert readme["size_bytes"] == (tmp_path / "README.md").stat().st_size
    assert len(readme["sha256"]) == 64


def test_manifest_output_json_is_stable_shape(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "hello\n")
    output = tmp_path / "artifacts" / "release-manifest.json"

    manifest = generate_manifest.build_manifest(tmp_path)
    generate_manifest.write_manifest(manifest, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))

    assert loaded["files"][0]["path"] == "README.md"
    assert output.read_text(encoding="utf-8").endswith("\n")


def test_manifest_rejects_output_parent_traversal(tmp_path: Path) -> None:
    assert_output_rejected(tmp_path, "../release-manifest.json", "parent traversal")


def test_manifest_rejects_output_outside_artifacts(tmp_path: Path) -> None:
    for output_arg in [
        "STATUS.md",
        "docs/release-manifest.md",
        "scripts/generate_manifest.py",
    ]:
        assert_output_rejected(tmp_path, output_arg, "artifacts/")


def test_manifest_rejects_absolute_output_path(tmp_path: Path) -> None:
    output_arg = str(tmp_path / "artifacts" / "release-manifest.json")

    assert_output_rejected(tmp_path, output_arg, "relative path")
