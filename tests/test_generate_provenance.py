import json
from pathlib import Path

from scripts import generate_checksums, generate_provenance


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
            {"path": "scripts/generate_manifest.py", "size_bytes": 20, "sha256": "b" * 64},
        ],
    }


def write_release_artifacts(repo_root: Path) -> Path:
    manifest_path = repo_root / "artifacts" / "release-manifest.json"
    write(manifest_path, json.dumps(sample_manifest()) + "\n")
    write(repo_root / "artifacts" / "sbom.spdx.json", "{}\n")
    write(repo_root / "artifacts" / "sbom.cdx.json", "{}\n")
    return manifest_path


def assert_path_rejected(repo_root: Path, path_arg: str, flag_name: str, expected: str) -> None:
    try:
        generate_provenance.resolve_artifact_path(repo_root, path_arg, flag_name)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"{flag_name} path should be rejected: {path_arg}")


def assert_provenance_path_rejected(repo_root: Path, manifest_path: Path, output_path: Path, expected: str) -> None:
    try:
        generate_provenance.validate_provenance_paths(repo_root, manifest_path, output_path)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError("Provenance output path should be rejected")


def test_provenance_records_repo_commands_python_and_digests(tmp_path: Path) -> None:
    manifest_path = write_release_artifacts(tmp_path)
    output_path = tmp_path / "artifacts" / "provenance.intoto.jsonl"

    statement = generate_provenance.build_statement(sample_manifest(), manifest_path, output_path, tmp_path, "2026-01-01T00:00:00Z")

    assert statement["_type"] == "https://in-toto.io/Statement/v1"
    assert statement["predicate"]["repo"]["git_ref"] == "main"
    assert statement["predicate"]["repo"]["git_commit"] == "abc123"
    assert statement["predicate"]["python_version"]
    assert statement["predicate"]["input_manifest"]["digest"]["sha256"]
    assert any("generate_sbom.py" in command for command in statement["predicate"]["commands"])
    assert any(subject["name"] == "artifacts/sbom.spdx.json" for subject in statement["subject"])
    assert all(subject["name"] != "artifacts/checksums.sha256" for subject in statement["subject"])
    assert all(subject["name"] != "artifacts/provenance.intoto.jsonl" for subject in statement["subject"])
    assert statement["predicate"]["checksum_entries"] == [
        {
            "path": product["name"],
            "sha256": product["digest"]["sha256"],
        }
        for product in statement["predicate"]["products"]
    ]


def test_release_evidence_pipeline_final_checksum_and_product_digests_match(
    tmp_path: Path,
) -> None:
    manifest_path = write_release_artifacts(tmp_path)
    manifest_path.write_bytes(
        (json.dumps(sample_manifest()) + "\r\n").encode("utf-8")
    )
    (tmp_path / "artifacts" / "sbom.spdx.json").write_bytes(b"{}\r\n")
    output_path = tmp_path / "artifacts" / "provenance.intoto.jsonl"
    checksums_path = tmp_path / "artifacts" / "checksums.sha256"
    statement = generate_provenance.build_statement(
        sample_manifest(),
        manifest_path,
        output_path,
        tmp_path,
        "2026-01-01T00:00:00Z",
    )
    generate_provenance.write_jsonl(statement, output_path)

    lines = generate_checksums.build_checksum_lines(
        tmp_path,
        manifest_path,
        checksums_path,
    )
    generate_checksums.write_checksums(lines, checksums_path)
    passed, _ = generate_checksums.verify_checksums(
        tmp_path,
        manifest_path,
        checksums_path,
    )

    assert passed is True
    checksum_entries = generate_checksums.parse_checksum_lines(
        lines,
        "generated checksums",
    )
    for product in statement["predicate"]["products"]:
        product_path = tmp_path / Path(product["name"])
        assert product["digest"]["sha256"] == checksum_entries[product["name"]]
        assert product["digest"]["sha256"] == generate_checksums.sha256_file(
            product_path
        )


def test_provenance_jsonl_writer_uses_single_final_newline(tmp_path: Path) -> None:
    output_path = tmp_path / "artifacts" / "provenance.intoto.jsonl"

    generate_provenance.write_jsonl({"name": "test"}, output_path)

    text = output_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert len(text.splitlines()) == 1


def test_provenance_rejects_paths_outside_artifacts(tmp_path: Path) -> None:
    for flag_name in ["--manifest", "--output"]:
        for path_arg in ["STATUS.md", "docs/provenance.jsonl", "scripts/generate_provenance.py"]:
            assert_path_rejected(tmp_path, path_arg, flag_name, "artifacts/")


def test_provenance_rejects_absolute_paths(tmp_path: Path) -> None:
    absolute_path = str(tmp_path / "artifacts" / "provenance.intoto.jsonl")

    assert_path_rejected(tmp_path, absolute_path, "--output", "relative path")


def test_provenance_rejects_parent_traversal(tmp_path: Path) -> None:
    assert_path_rejected(tmp_path, "../provenance.intoto.jsonl", "--output", "parent traversal")


def test_provenance_rejects_overwriting_release_artifacts(tmp_path: Path) -> None:
    manifest_path = tmp_path / "artifacts" / "release-manifest.json"
    output_path = tmp_path / "artifacts" / "provenance.intoto.jsonl"

    generate_provenance.validate_provenance_paths(tmp_path, manifest_path, output_path)
    for protected_path, expected in [
        (manifest_path, "--manifest"),
        (tmp_path / "artifacts" / "checksums.sha256", "checksums.sha256"),
        (tmp_path / "artifacts" / "checksums.txt", "checksums.txt"),
        (tmp_path / "artifacts" / "sbom.spdx.json", "sbom.spdx.json"),
        (tmp_path / "artifacts" / "sbom.cdx.json", "sbom.cdx.json"),
    ]:
        assert_provenance_path_rejected(tmp_path, manifest_path, protected_path, expected)
