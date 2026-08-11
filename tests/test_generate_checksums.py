import hashlib
import os
from pathlib import Path
import subprocess

import pytest

from scripts import (
    generate_checksums,
    generate_manifest,
    generate_provenance,
    generate_sbom,
)


WRITER_OUTPUTS = {
    "manifest": "release-manifest.json",
    "checksums": "checksums.sha256",
    "sbom": "sbom.spdx.json",
    "provenance": "provenance.intoto.jsonl",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def invoke_release_writer(writer_name: str, output_path: Path) -> None:
    if writer_name == "manifest":
        generate_manifest.write_manifest({"schema_version": "1"}, output_path)
    elif writer_name == "checksums":
        generate_checksums.write_checksums(
            ["abc  artifacts/release-manifest.json"], output_path
        )
    elif writer_name == "sbom":
        generate_sbom.write_json({"name": "test"}, output_path)
    else:
        generate_provenance.write_jsonl({"name": "test"}, output_path)


def create_directory_redirect(link: Path, target: Path) -> None:
    if os.name == "nt":
        created = subprocess.run(
            ["cmd", "/d", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
        )
        assert created.returncode == 0, (
            created.stdout + created.stderr
        ).decode(errors="replace")
    else:
        link.symlink_to(target, target_is_directory=True)


def remove_directory_redirect(link: Path) -> None:
    if os.name == "nt":
        link.rmdir()
    else:
        link.unlink()


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
    digest = generate_checksums.sha256_file(path)
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


def test_checksums_writer_uses_lf_final_newline(tmp_path: Path) -> None:
    output = tmp_path / "artifacts" / "checksums.sha256"

    generate_checksums.write_checksums(["abc  artifacts/release-manifest.json"], output)

    assert output.read_bytes() == b"abc  artifacts/release-manifest.json\n"


def test_checksums_normalize_lf_crlf_and_cr_before_hashing(tmp_path: Path) -> None:
    lf_path = tmp_path / "lf.json"
    crlf_path = tmp_path / "crlf.json"
    cr_path = tmp_path / "cr.json"
    canonical = b'{"first":1}\n{"second":2}\n'
    lf_path.write_bytes(canonical)
    crlf_path.write_bytes(canonical.replace(b"\n", b"\r\n"))
    cr_path.write_bytes(canonical.replace(b"\n", b"\r"))
    expected = hashlib.sha256(canonical).hexdigest()

    assert generate_checksums.sha256_file(lf_path) == expected
    assert generate_checksums.sha256_file(crlf_path) == expected
    assert generate_checksums.sha256_file(cr_path) == expected


def test_verify_mode_passes_current_tree(capsys) -> None:
    result = generate_checksums.main(["--verify"])

    output = capsys.readouterr().out
    assert result == 0
    assert "MATCH artifacts/release-manifest.json" in output
    assert "verified checksum entries: 5" in output
    assert "Checksum verification passed." in output


def test_verify_mode_fails_without_rewriting_tampered_bundle(tmp_path: Path, capsys) -> None:
    bundle = write_release_bundle(tmp_path)
    output = tmp_path / "artifacts" / "checksums.sha256"
    generate_checksums.write_checksums(
        generate_checksums.build_checksum_lines(tmp_path, bundle["manifest"], output),
        output,
    )
    original_checksums = output.read_bytes()
    bundle["manifest"].write_bytes(bundle["manifest"].read_bytes() + b" ")

    result = generate_checksums.main(
        [
            "--repo-root",
            str(tmp_path),
            "--manifest",
            "artifacts/release-manifest.json",
            "--output",
            "artifacts/checksums.sha256",
            "--verify",
        ]
    )

    captured = capsys.readouterr().out
    assert result == 1
    assert "MISMATCH artifacts/release-manifest.json" in captured
    assert "Checksum verification failed." in captured
    assert output.read_bytes() == original_checksums


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


def test_reserved_release_artifact_registry_is_complete_and_checksum_owned(
    tmp_path: Path,
) -> None:
    assert generate_checksums.RESERVED_RELEASE_ARTIFACTS == (
        "artifacts/release-manifest.json",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
        "artifacts/checksums.sha256",
        "artifacts/checksums.txt",
        "artifacts/eval-report.json",
    )
    for relative_path in generate_checksums.CHECKSUM_OUTPUT_PATHS:
        generate_checksums.validate_release_output_path(
            tmp_path,
            tmp_path / relative_path,
            allowed_reserved_paths=generate_checksums.CHECKSUM_OUTPUT_PATHS,
            flag_name="--output",
        )
    generate_checksums.validate_release_output_path(
        tmp_path,
        tmp_path / "artifacts" / "custom-checksums.sha256",
        allowed_reserved_paths=generate_checksums.CHECKSUM_OUTPUT_PATHS,
        flag_name="--output",
    )


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


def test_physical_boundary_rejects_synthetic_symlink_component(
    tmp_path: Path, monkeypatch
) -> None:
    bundle = write_release_bundle(tmp_path)
    original = generate_checksums.stat.S_ISLNK

    def synthetic_symlink(mode: int) -> bool:
        return original(mode) or mode == bundle["manifest"].lstat().st_mode

    monkeypatch.setattr(generate_checksums.stat, "S_ISLNK", synthetic_symlink)

    with pytest.raises(ValueError, match="symlink or reparse point"):
        generate_checksums.read_regular_file(
            tmp_path, bundle["manifest"], "--manifest"
        )


@pytest.mark.parametrize("leaf", [False, True])
def test_release_paths_reject_junction_parent_and_leaf(
    tmp_path: Path, leaf: bool
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    artifacts = repo / "artifacts"
    if leaf:
        artifacts.mkdir()
        junction = artifacts / "release-manifest.json"
        path_arg = "artifacts/release-manifest.json"
    else:
        junction = artifacts
        path_arg = "artifacts/release-manifest.json"
    if os.name == "nt":
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
            check=False,
            capture_output=True,
        )
        assert created.returncode == 0, created.stderr.decode(errors="replace")
    else:
        junction.symlink_to(outside, target_is_directory=True)
    try:
        with pytest.raises(ValueError, match="symlink or reparse point"):
            generate_checksums.resolve_repo_path(repo, path_arg, "--manifest")
    finally:
        remove_directory_redirect(junction)


def test_release_input_rejects_multiply_linked_file(tmp_path: Path) -> None:
    bundle = write_release_bundle(tmp_path)
    os.link(bundle["manifest"], tmp_path / "manifest-alias.json")

    with pytest.raises(ValueError, match="multiply-linked"):
        generate_checksums.build_checksum_lines(
            tmp_path,
            bundle["manifest"],
            tmp_path / "artifacts" / "checksums.sha256",
        )


def test_writer_rejects_non_regular_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "artifacts" / "checksums.sha256"
    output.mkdir(parents=True)

    with pytest.raises(ValueError, match="regular file"):
        generate_checksums.write_checksums(
            ["abc  artifacts/release-manifest.json"], output
        )


def test_atomic_replace_rejects_target_identity_drift(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    output = artifacts / "checksums.sha256"
    output.write_bytes(b"original\n")
    temporary = artifacts / ".checksums.test.tmp"
    temporary.write_bytes(b"candidate\n")
    parent_identity = generate_checksums._path_identity(artifacts)
    target_identity = generate_checksums._path_identity(
        output, include_content_state=True
    )
    replacement = artifacts / "replacement"
    replacement.write_bytes(b"drifted\n")
    os.replace(replacement, output)

    with pytest.raises(ValueError, match="target identity changed"):
        generate_checksums._replace_validated_temp(
            tmp_path,
            temporary,
            output,
            parent_identity,
            target_identity,
        )
    assert output.read_bytes() == b"drifted\n"
    assert temporary.read_bytes() == b"candidate\n"


@pytest.mark.parametrize("writer_name", sorted(WRITER_OUTPUTS))
@pytest.mark.parametrize(
    "fault",
    ["junction_parent", "reparse_leaf", "hardlink_leaf", "target_identity_drift"],
)
def test_release_writer_adapter_rejects_physical_fault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    writer_name: str,
    fault: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_sentinel = outside / "sentinel.txt"
    outside_sentinel.write_bytes(b"outside\n")
    artifacts = repo / "artifacts"
    output = artifacts / WRITER_OUTPUTS[writer_name]
    redirect: Path | None = None
    original = b"original\n"
    drifted = b"drifted!\n"

    if fault == "junction_parent":
        redirect = artifacts
        create_directory_redirect(redirect, outside)
        expected = "symlink or reparse point"
    elif fault == "reparse_leaf":
        artifacts.mkdir()
        redirect = output
        create_directory_redirect(redirect, outside)
        expected = "symlink or reparse point"
    elif fault == "hardlink_leaf":
        artifacts.mkdir()
        output.write_bytes(original)
        os.link(output, tmp_path / f"{writer_name}-alias")
        expected = "multiply-linked"
    else:
        artifacts.mkdir()
        output.write_bytes(original)
        original_replace = generate_checksums._replace_validated_temp

        def replace_after_drift(
            repo_root: Path,
            temp_path: Path,
            output_path: Path,
            parent_identity: tuple[int, ...],
            target_identity: tuple[int, ...] | None,
        ) -> None:
            replacement = output_path.with_name(f".{output_path.name}.drift")
            replacement.write_bytes(drifted)
            os.replace(replacement, output_path)
            original_replace(
                repo_root,
                temp_path,
                output_path,
                parent_identity,
                target_identity,
            )

        monkeypatch.setattr(
            generate_checksums, "_replace_validated_temp", replace_after_drift
        )
        expected = "target identity changed"

    try:
        with pytest.raises(ValueError, match=expected):
            invoke_release_writer(writer_name, output)
    finally:
        if redirect is not None:
            remove_directory_redirect(redirect)

    assert outside_sentinel.read_bytes() == b"outside\n"
    assert not (outside / WRITER_OUTPUTS[writer_name]).is_file()
    if fault == "hardlink_leaf":
        assert output.read_bytes() == original
        assert (tmp_path / f"{writer_name}-alias").read_bytes() == original
    elif fault == "target_identity_drift":
        assert output.read_bytes() == drifted
    if artifacts.is_dir():
        assert list(artifacts.glob(f".{output.name}.*.tmp")) == []
    assert list(outside.glob(f".{output.name}.*.tmp")) == []
