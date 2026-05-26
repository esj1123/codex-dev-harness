import hashlib
from pathlib import Path

from scripts import generate_checksums


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def assert_path_rejected(repo_root: Path, path_arg: str, flag_name: str, expected: str) -> None:
    try:
        generate_checksums.resolve_repo_path(repo_root, path_arg, flag_name)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"{flag_name} path should be rejected: {path_arg}")


def write_release_bundle(tmp_path: Path) -> dict[str, Path]:
    manifest = tmp_path / "artifacts" / "release-manifest.json"
    spdx = tmp_path / "artifacts" / "sbom.spdx.json"
    cyclonedx = tmp_path / "artifacts" / "sbom.cdx.json"
    provenance = tmp_path / "artifacts" / "provenance.intoto.jsonl"
    write(manifest, '{"schema_version":"1"}\n')
    write(spdx, '{"SPDXID":"SPDXRef-DOCUMENT"}\n')
    write(cyclonedx, '{"bomFormat":"CycloneDX"}\n')
    write(provenance, '{"predicateType":"local"}\n')
    return {
        "manifest": manifest,
        "spdx": spdx,
        "cyclonedx": cyclonedx,
        "provenance": provenance,
    }


def expected_line(path: Path, repo_root: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    relative_path = path.relative_to(repo_root).as_posix()
    return f"{digest}  {relative_path}"


def test_checksums_include_full_release_bundle_in_stable_order(tmp_path: Path) -> None:
    bundle = write_release_bundle(tmp_path)
    output = tmp_path / "artifacts" / "checksums.sha256"

    lines = generate_checksums.build_checksum_lines(tmp_path, bundle["manifest"], output)

    assert lines == [
        expected_line(bundle["provenance"], tmp_path),
        expected_line(bundle["manifest"], tmp_path),
        expected_line(bundle["cyclonedx"], tmp_path),
        expected_line(bundle["spdx"], tmp_path),
    ]


def test_checksums_include_optional_eval_report_when_present(tmp_path: Path) -> None:
    bundle = write_release_bundle(tmp_path)
    eval_report = tmp_path / "artifacts" / "eval-report.json"
    output = tmp_path / "artifacts" / "checksums.sha256"
    write(eval_report, '{"result":"PASS"}\n')

    lines = generate_checksums.build_checksum_lines(tmp_path, bundle["manifest"], output)

    assert expected_line(eval_report, tmp_path) in lines


def test_checksums_writer_uses_final_newline(tmp_path: Path) -> None:
    output = tmp_path / "artifacts" / "checksums.sha256"

    generate_checksums.write_checksums(["abc  artifacts/release-manifest.json"], output)

    assert output.read_text(encoding="utf-8") == "abc  artifacts/release-manifest.json\n"


def test_checksums_do_not_self_reference(tmp_path: Path) -> None:
    bundle = write_release_bundle(tmp_path)
    output = tmp_path / "artifacts" / "checksums.sha256"
    write(output, "old\n")

    lines = generate_checksums.build_checksum_lines(tmp_path, bundle["manifest"], output)

    assert all("checksums.sha256" not in line for line in lines)
    assert any("release-manifest.json" in line for line in lines)


def test_checksums_reject_release_artifact_output_overlap(tmp_path: Path) -> None:
    bundle = write_release_bundle(tmp_path)

    for output in [
        bundle["manifest"],
        bundle["spdx"],
        bundle["cyclonedx"],
        bundle["provenance"],
        tmp_path / "artifacts" / "eval-report.json",
    ]:
        try:
            generate_checksums.build_checksum_lines(tmp_path, bundle["manifest"], output)
        except ValueError as exc:
            assert "must not overwrite" in str(exc)
        else:
            raise AssertionError(f"checksum output should not overwrite {output}")


def test_checksums_fail_when_required_artifact_is_missing(tmp_path: Path) -> None:
    manifest = tmp_path / "artifacts" / "release-manifest.json"
    output = tmp_path / "artifacts" / "checksums.sha256"
    write(manifest, "{}\n")

    try:
        generate_checksums.build_checksum_lines(tmp_path, manifest, output)
    except FileNotFoundError as exc:
        assert "required release evidence artifact" in str(exc)
        assert "artifacts/sbom.spdx.json" in str(exc)
    else:
        raise AssertionError("missing release evidence artifacts should fail by default")


def test_checksums_allow_missing_artifacts_when_explicit(tmp_path: Path) -> None:
    manifest = tmp_path / "artifacts" / "release-manifest.json"
    output = tmp_path / "artifacts" / "checksums.sha256"
    write(manifest, "{}\n")

    lines = generate_checksums.build_checksum_lines(
        tmp_path,
        manifest,
        output,
        allow_missing=True,
    )

    assert lines == [expected_line(manifest, tmp_path)]


def test_checksums_reject_parent_traversal(tmp_path: Path) -> None:
    assert_path_rejected(tmp_path, "../checksums.sha256", "--output", "parent traversal")


def test_checksums_reject_paths_outside_artifacts(tmp_path: Path) -> None:
    for flag_name in ["--manifest", "--output"]:
        for path_arg in [
            "STATUS.md",
            "docs/release-manifest.md",
            "scripts/generate_checksums.py",
        ]:
            assert_path_rejected(tmp_path, path_arg, flag_name, "artifacts/")


def test_checksums_reject_absolute_paths(tmp_path: Path) -> None:
    for flag_name, filename in [
        ("--manifest", "release-manifest.json"),
        ("--output", "checksums.sha256"),
    ]:
        path_arg = str(tmp_path / "artifacts" / filename)
        assert_path_rejected(tmp_path, path_arg, flag_name, "relative path")
