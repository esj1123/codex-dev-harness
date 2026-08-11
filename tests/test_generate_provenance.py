import json
import hashlib
from pathlib import Path

from scripts import (
    generate_checksums,
    generate_manifest,
    generate_provenance,
    generate_sbom,
)


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
            {"path": "scripts/generate_manifest.py", "size_bytes": 20, "sha256": "b" * 64},
            source_record("LICENSE", MIT_LICENSE_TEXT),
            source_record("requirements-dev.lock", LOCK_TEXT),
        ],
    }


def write_release_artifacts(repo_root: Path) -> Path:
    (repo_root / "LICENSE").write_bytes(MIT_LICENSE_TEXT.encode("utf-8"))
    (repo_root / "requirements-dev.lock").write_bytes(LOCK_TEXT.encode("utf-8"))
    manifest_path = repo_root / "artifacts" / "release-manifest.json"
    write(manifest_path, json.dumps(sample_manifest()) + "\n")
    write(repo_root / "artifacts" / "sbom.spdx.json", "{}\n")
    write(repo_root / "artifacts" / "sbom.cdx.json", "{}\n")
    return manifest_path


def sample_snapshot(
    manifest_path: Path,
) -> generate_manifest.ValidatedManifestSnapshot:
    digest = hashlib.sha256(
        generate_checksums.canonical_text_bytes(manifest_path.read_bytes())
    ).hexdigest()
    return generate_manifest.ValidatedManifestSnapshot(
        manifest_path, sample_manifest(), digest
    )


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

    statement = generate_provenance.build_statement(
        sample_snapshot(manifest_path),
        output_path,
        tmp_path,
        "2026-01-01T00:00:00Z",
    )

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
    snapshot = sample_snapshot(manifest_path)
    created = "2026-01-01T00:00:00Z"
    generate_sbom.write_json(
        generate_sbom.build_spdx(snapshot, tmp_path, created),
        tmp_path / "artifacts" / "sbom.spdx.json",
    )
    generate_sbom.write_json(
        generate_sbom.build_cyclonedx(snapshot, tmp_path, created),
        tmp_path / "artifacts" / "sbom.cdx.json",
    )
    output_path = tmp_path / "artifacts" / "provenance.intoto.jsonl"
    checksums_path = tmp_path / "artifacts" / "checksums.sha256"
    statement = generate_provenance.build_statement(
        snapshot,
        output_path,
        tmp_path,
        created,
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


def test_provenance_uses_captured_manifest_without_rereading_path(
    tmp_path: Path, monkeypatch
) -> None:
    manifest_path = write_release_artifacts(tmp_path)
    snapshot = sample_snapshot(manifest_path)
    manifest_path.write_bytes(b"tampered after snapshot\n")
    original_read = generate_checksums.read_regular_file

    def reject_manifest_reread(repo_root: Path, path: Path, flag_name: str = "input") -> bytes:
        if path == manifest_path:
            raise AssertionError("manifest path was reopened")
        return original_read(repo_root, path, flag_name)

    monkeypatch.setattr(generate_checksums, "read_regular_file", reject_manifest_reread)

    statement = generate_provenance.build_statement(
        snapshot,
        tmp_path / "artifacts" / "provenance.intoto.jsonl",
        tmp_path,
        "2026-01-01T00:00:00Z",
    )

    assert statement["predicate"]["input_manifest"]["digest"]["sha256"] == snapshot.canonical_sha256
    manifest_product = next(
        item
        for item in statement["subject"]
        if item["name"] == "artifacts/release-manifest.json"
    )
    assert manifest_product["digest"]["sha256"] == snapshot.canonical_sha256


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
    generate_provenance.validate_provenance_paths(
        tmp_path,
        manifest_path,
        tmp_path / "artifacts" / "custom-provenance.jsonl",
    )
    for protected_path, expected in [
        (manifest_path, "--manifest"),
        (tmp_path / "artifacts" / "checksums.sha256", "reserved release artifact"),
        (tmp_path / "artifacts" / "checksums.txt", "reserved release artifact"),
        (tmp_path / "artifacts" / "sbom.spdx.json", "reserved release artifact"),
        (tmp_path / "artifacts" / "sbom.cdx.json", "reserved release artifact"),
        (tmp_path / "artifacts" / "eval-report.json", "reserved release artifact"),
    ]:
        assert_provenance_path_rejected(tmp_path, manifest_path, protected_path, expected)
