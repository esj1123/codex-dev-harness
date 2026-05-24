import hashlib
from pathlib import Path

from scripts import generate_checksums


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_checksums_format_is_stable(tmp_path: Path) -> None:
    manifest = tmp_path / "artifacts" / "release-manifest.json"
    output = tmp_path / "artifacts" / "checksums.sha256"
    write(manifest, '{"schema_version":"1"}\n')

    lines = generate_checksums.build_checksum_lines(tmp_path, manifest, output)

    expected = hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert lines == [f"{expected}  artifacts/release-manifest.json"]


def test_checksums_writer_uses_final_newline(tmp_path: Path) -> None:
    output = tmp_path / "artifacts" / "checksums.sha256"

    generate_checksums.write_checksums(["abc  artifacts/release-manifest.json"], output)

    assert output.read_text(encoding="utf-8") == "abc  artifacts/release-manifest.json\n"


def test_checksums_do_not_self_reference(tmp_path: Path) -> None:
    manifest = tmp_path / "artifacts" / "release-manifest.json"
    output = tmp_path / "artifacts" / "checksums.sha256"
    write(manifest, "{}\n")
    write(output, "old\n")

    lines = generate_checksums.build_checksum_lines(tmp_path, manifest, output)

    assert all("checksums.sha256" not in line for line in lines)
    assert any("release-manifest.json" in line for line in lines)


def test_checksums_reject_manifest_output_overlap(tmp_path: Path) -> None:
    manifest = tmp_path / "artifacts" / "release-manifest.json"
    write(manifest, "{}\n")

    try:
        generate_checksums.build_checksum_lines(tmp_path, manifest, manifest)
    except ValueError as exc:
        assert "must not overwrite" in str(exc)
    else:
        raise AssertionError("checksum output should not overwrite manifest")


def test_checksums_reject_parent_traversal(tmp_path: Path) -> None:
    try:
        generate_checksums.resolve_repo_path(tmp_path, "../checksums.sha256", "--output")
    except ValueError as exc:
        assert "parent traversal" in str(exc)
    else:
        raise AssertionError("parent traversal should be rejected")
