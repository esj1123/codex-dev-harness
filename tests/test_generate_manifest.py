import hashlib
import io
import json
from pathlib import Path
import subprocess

import pytest

from scripts import generate_manifest


OID_A = "a" * 40
OID_B = "b" * 40


def write(path: Path, content: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git(
    repo_root: Path,
    *args: str,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    return result


def batch_frame(
    object_id: str,
    body: bytes,
    *,
    object_type: str = "blob",
    size: str | None = None,
    delimiter: bytes = b"\n",
) -> bytes:
    raw_size = str(len(body)) if size is None else size
    return (
        f"{object_id} {object_type} {raw_size}\n".encode("ascii")
        + body
        + delimiter
    )


def commit_repo(repo_root: Path) -> str:
    git(repo_root, "init", "-q")
    git(repo_root, "config", "user.name", "Test User")
    git(repo_root, "config", "user.email", "test@example.invalid")
    git(repo_root, "add", "-A")
    git(repo_root, "commit", "-q", "-m", "fixture")
    return git(repo_root, "rev-parse", "HEAD").stdout.decode("ascii").strip()


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
    write(tmp_path / ".pytest_cache" / "cache")
    write(tmp_path / "__pycache__" / "module.pyc")
    write(tmp_path / "local" / "scratch.md")
    commit_repo(tmp_path)

    manifest = generate_manifest.build_manifest(tmp_path)
    paths = [entry["path"] for entry in manifest["files"]]

    assert "README.md" in paths
    assert "docs/policy.md" in paths
    assert not any(path.startswith("artifacts/") for path in paths)
    assert not any(path.startswith(".pytest_cache/") for path in paths)
    assert not any(path.startswith("__pycache__/") for path in paths)
    assert not any(path.startswith("local/") for path in paths)


def test_manifest_file_list_is_sorted(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "z.md")
    write(tmp_path / "docs" / "a.md")
    write(tmp_path / "README.md")
    commit_repo(tmp_path)

    manifest = generate_manifest.build_manifest(tmp_path)
    paths = [entry["path"] for entry in manifest["files"]]

    assert paths == sorted(paths)


def test_manifest_includes_runtime_reproducibility_files(tmp_path: Path) -> None:
    write(tmp_path / ".python-version", "3.12.13\n")
    write(tmp_path / "requirements-dev.txt", "pytest==9.0.3\n")
    write(tmp_path / "requirements-dev.lock", "pytest==9.0.3\n")
    commit_repo(tmp_path)

    manifest = generate_manifest.build_manifest(tmp_path)
    paths = {entry["path"] for entry in manifest["files"]}

    assert ".python-version" in paths
    assert "requirements-dev.txt" in paths
    assert "requirements-dev.lock" in paths


def test_manifest_includes_repository_license_and_security_policy(tmp_path: Path) -> None:
    write(tmp_path / "LICENSE", "MIT License\n")
    write(tmp_path / "SECURITY.md", "# Security Policy\n")
    commit_repo(tmp_path)

    manifest = generate_manifest.build_manifest(tmp_path)
    paths = {entry["path"] for entry in manifest["files"]}

    assert "LICENSE" in paths
    assert "SECURITY.md" in paths


def test_manifest_has_required_top_level_fields(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "hello\n")
    head = commit_repo(tmp_path)

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
    assert manifest["git_commit"] == head
    assert len(manifest["git_commit"]) == 40
    assert manifest["git_tag"] is None
    assert manifest["verification_commands"][0]["result"] == "NOT_RUN"
    assert [gate["name"] for gate in manifest["quality_gates"]] == [
        "docs_gate",
        "repo_hygiene_gate",
        "template_schema_gate",
        "example_gate",
        "example_render_drift_gate",
        "rendered_golden_content_gate",
        "secret_scan_gate",
        "json_evidence_gate",
    ]


def test_manifest_file_records_use_committed_git_blob_bytes(tmp_path: Path) -> None:
    write(tmp_path / ".gitattributes", "*.md text eol=crlf\n")
    write(tmp_path / "README.md", "hello\r\n")
    commit_repo(tmp_path)

    manifest = generate_manifest.build_manifest(tmp_path)
    readme = next(entry for entry in manifest["files"] if entry["path"] == "README.md")
    committed = git(tmp_path, "show", "HEAD:README.md").stdout

    assert readme["size_bytes"] == len(committed)
    assert readme["sha256"] == hashlib.sha256(committed).hexdigest()


def test_manifest_output_json_is_stable_shape(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "hello\n")
    commit_repo(tmp_path)
    output = tmp_path / "artifacts" / "release-manifest.json"

    manifest = generate_manifest.build_manifest(tmp_path)
    generate_manifest.write_manifest(manifest, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))

    assert loaded["files"][0]["path"] == "README.md"
    assert output.read_text(encoding="utf-8").endswith("\n")


@pytest.mark.parametrize("dirty_kind", ["tracked", "untracked"])
def test_manifest_rejects_dirty_repository(tmp_path: Path, dirty_kind: str) -> None:
    write(tmp_path / "README.md", "clean\n")
    commit_repo(tmp_path)
    if dirty_kind == "tracked":
        write(tmp_path / "README.md", "dirty\n")
    else:
        write(tmp_path / "UNTRACKED.md", "dirty\n")

    with pytest.raises(ValueError, match="must be clean"):
        generate_manifest.build_manifest(tmp_path)


def test_manifest_rejects_non_git_root(tmp_path: Path) -> None:
    write(tmp_path / "README.md")

    with pytest.raises(ValueError, match="Git repository inspection failed"):
        generate_manifest.build_manifest(tmp_path)


def test_manifest_rejects_repository_without_head(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")

    with pytest.raises(ValueError, match="Git repository inspection failed"):
        generate_manifest.build_manifest(tmp_path)


def test_git_tree_inventory_ignores_untracked_files(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "tracked\n")
    head = commit_repo(tmp_path)
    write(tmp_path / "docs" / "untracked.md", "untracked\n")

    records = generate_manifest.git_tree_file_records(tmp_path, head)

    assert [record["path"] for record in records] == ["README.md"]


def test_git_tree_inventory_uses_one_ls_tree_and_one_batch_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path / "README.md", "same\n")
    write(tmp_path / "docs" / "same.md", "same\n")
    write(tmp_path / "docs" / "empty.txt", "")
    binary = b"\x00binary\nbytes\xff"
    (tmp_path / "docs" / "binary.bin").write_bytes(binary)
    head = commit_repo(tmp_path)
    original_run = generate_manifest.subprocess.run
    calls: list[
        tuple[tuple[str, ...], object, bytes | None, object, object]
    ] = []

    def recording_run(*args, **kwargs):
        calls.append(
            (
                tuple(args[0]),
                kwargs.get("stdout"),
                kwargs.get("input"),
                kwargs.get("timeout"),
                kwargs.get("stderr"),
            )
        )
        return original_run(*args, **kwargs)

    monkeypatch.setattr(generate_manifest.subprocess, "run", recording_run)

    records = generate_manifest.git_tree_file_records(tmp_path, head)

    assert len(records) == 4
    assert [call[0][3] for call in calls] == ["ls-tree", "cat-file"]
    assert calls[1][0][3:] == ("cat-file", "--batch")
    assert calls[1][1] is not subprocess.PIPE
    assert hasattr(calls[1][1], "write")
    assert getattr(calls[1][1], "closed", False) is True
    assert calls[1][3] == generate_manifest.GIT_TIMEOUT_SECONDS
    assert calls[1][4] is subprocess.DEVNULL
    requested = calls[1][2]
    assert requested is not None
    requested_ids = requested.decode("ascii").splitlines()
    assert len(requested_ids) == len(records)
    assert len(set(requested_ids)) == 3
    by_path = {record["path"]: record for record in records}
    assert by_path["docs/empty.txt"]["size_bytes"] == 0
    assert by_path["docs/binary.bin"]["sha256"] == hashlib.sha256(binary).hexdigest()


def test_cat_file_batch_parser_supports_repeated_empty_and_binary_blobs() -> None:
    binary = b"\x00binary\nbytes\xff"
    raw = batch_frame(OID_A, b"") + batch_frame(OID_A, binary)

    metadata = generate_manifest._parse_cat_file_batch(
        io.BytesIO(raw), [OID_A, OID_A]
    )

    assert metadata == [
        (0, hashlib.sha256(b"").hexdigest()),
        (len(binary), hashlib.sha256(binary).hexdigest()),
    ]


class BoundedReadBytesIO(io.BytesIO):
    def __init__(self, value: bytes) -> None:
        super().__init__(value)
        self.body_read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        assert 0 <= size <= generate_manifest._BATCH_READ_CHUNK_BYTES
        self.body_read_sizes.append(size)
        return super().read(size)

    def readline(self, size: int = -1) -> bytes:
        assert 0 <= size <= generate_manifest._BATCH_HEADER_LIMIT_BYTES
        return super().readline(size)


def test_cat_file_batch_parser_hashes_large_blob_with_bounded_reads() -> None:
    body = b"x" * (generate_manifest._BATCH_READ_CHUNK_BYTES * 2 + 17)
    stream = BoundedReadBytesIO(batch_frame(OID_A, body))

    metadata = generate_manifest._parse_cat_file_batch(stream, [OID_A])

    assert metadata == [(len(body), hashlib.sha256(body).hexdigest())]
    assert stream.body_read_sizes.count(
        generate_manifest._BATCH_READ_CHUNK_BYTES
    ) == 2


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        f"{OID_A} missing\n".encode("ascii"),
        batch_frame(OID_B, b""),
        batch_frame(OID_A, b"", object_type="tree"),
        batch_frame(OID_A, b"", size="-1"),
        batch_frame(OID_A, b"", size="1x"),
        f"{OID_A} blob 4\nabc".encode("ascii"),
        f"{OID_A} blob {10**30}\nabc".encode("ascii"),
        batch_frame(OID_A, b"abc", delimiter=b"X"),
        batch_frame(OID_A, b"abc") + b"trailing",
        b"\xff\n",
        b"x" * 256,
    ],
)
def test_cat_file_batch_parser_rejects_malformed_output(raw: bytes) -> None:
    with pytest.raises(ValueError, match="batch output is malformed"):
        generate_manifest._parse_cat_file_batch(io.BytesIO(raw), [OID_A])


def test_cat_file_batch_parser_rejects_missing_expected_frame() -> None:
    with pytest.raises(ValueError, match="batch output is malformed"):
        generate_manifest._parse_cat_file_batch(
            io.BytesIO(batch_frame(OID_A, b"first")),
            [OID_A, OID_A],
        )


@pytest.mark.parametrize("failure", ["oserror", "timeout", "nonzero"])
def test_run_git_cat_file_batch_fails_closed_on_process_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    def fail_run(*args, **kwargs):
        if failure == "oserror":
            raise OSError("synthetic process failure")
        if failure == "timeout":
            raise subprocess.TimeoutExpired(
                args[0], generate_manifest.GIT_TIMEOUT_SECONDS
            )
        return subprocess.CompletedProcess(
            args[0], 1, stdout=None, stderr=b"synthetic"
        )

    monkeypatch.setattr(generate_manifest.subprocess, "run", fail_run)

    with pytest.raises(ValueError, match="Git repository inspection failed"):
        generate_manifest._run_git_cat_file_batch(tmp_path, [OID_A])


def test_run_git_cat_file_batch_fails_closed_on_tempfile_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_temporary_file(*args, **kwargs):
        raise OSError("synthetic temporary file failure")

    monkeypatch.setattr(
        generate_manifest.tempfile, "TemporaryFile", fail_temporary_file
    )

    with pytest.raises(ValueError, match="Git repository inspection failed"):
        generate_manifest._run_git_cat_file_batch(tmp_path, [OID_A])


def test_run_git_cat_file_batch_fails_closed_on_tempfile_read_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def successful_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, stdout=None, stderr=None)

    def fail_parse(*args, **kwargs):
        raise OSError("synthetic temporary file read failure")

    monkeypatch.setattr(generate_manifest.subprocess, "run", successful_run)
    monkeypatch.setattr(generate_manifest, "_parse_cat_file_batch", fail_parse)

    with pytest.raises(ValueError, match="Git repository inspection failed"):
        generate_manifest._run_git_cat_file_batch(tmp_path, [OID_A])


@pytest.mark.parametrize("failure", ["oserror", "timeout", "nonzero"])
def test_run_git_bytes_fails_closed_on_process_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    def fail_run(*args, **kwargs):
        if failure == "oserror":
            raise OSError("synthetic process failure")
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args[0], generate_manifest.GIT_TIMEOUT_SECONDS)
        return subprocess.CompletedProcess(args[0], 1, stdout=b"", stderr=b"synthetic")

    monkeypatch.setattr(generate_manifest.subprocess, "run", fail_run)

    with pytest.raises(ValueError, match="Git repository inspection failed"):
        generate_manifest.run_git_bytes(
            tmp_path,
            ["cat-file", "--batch"],
            input_bytes=(OID_A + "\n").encode("ascii"),
        )


@pytest.mark.parametrize("second_path", ["docs/A.md", "docs/a.md"])
def test_git_tree_inventory_rejects_exact_or_casefold_duplicate_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    second_path: str,
) -> None:
    raw = (
        f"100644 blob {OID_A}\tdocs/A.md\0"
        f"100644 blob {OID_A}\t{second_path}\0"
    ).encode("ascii")
    monkeypatch.setattr(
        generate_manifest,
        "run_git_bytes",
        lambda *_args, **_kwargs: raw,
    )

    with pytest.raises(ValueError, match="duplicate manifest paths"):
        generate_manifest.git_tree_file_records(tmp_path, OID_B)


def test_git_tree_inventory_rejects_malformed_object_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = b"100644 blob not-a-sha\tREADME.md\0"
    monkeypatch.setattr(
        generate_manifest,
        "run_git_bytes",
        lambda *_args, **_kwargs: raw,
    )

    with pytest.raises(ValueError, match="tree entry is malformed"):
        generate_manifest.git_tree_file_records(tmp_path, OID_B)


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_manifest_rejects_non_regular_git_tree_entries(
    tmp_path: Path,
    mode: str,
) -> None:
    write(tmp_path / "README.md", "tracked\n")
    head = commit_repo(tmp_path)
    if mode == "120000":
        object_id = git(
            tmp_path,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=b"README.md",
        ).stdout.decode("ascii").strip()
    else:
        object_id = head
    git(
        tmp_path,
        "update-index",
        "--add",
        "--cacheinfo",
        f"{mode},{object_id},docs/non-regular",
    )
    git(tmp_path, "commit", "-q", "-m", "non-regular")
    non_regular_head = git(tmp_path, "rev-parse", "HEAD").stdout.decode("ascii").strip()

    with pytest.raises(ValueError, match="not a regular blob"):
        generate_manifest.git_tree_file_records(tmp_path, non_regular_head)


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


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        ("https://github.com/owner/repo.git", "owner/repo"),
        ("ssh://git@github.com/owner/repo.git", "owner/repo"),
        ("git@github.com:owner/repo.git", "owner/repo"),
    ],
)
def test_manifest_normalizes_github_repository_identity(
    remote: str,
    expected: str,
) -> None:
    assert generate_manifest.normalize_repository(remote) == expected


def test_manifest_hashes_non_github_repository_without_exposing_remote() -> None:
    remote = "https://user:synthetic@git.example.invalid:8443/org/repo.git?token=synthetic#fragment"
    expected_hash = hashlib.sha256(
        b"git.example.invalid/org/repo"
    ).hexdigest()[:16]

    identity = generate_manifest.normalize_repository(remote)

    assert identity == f"external-repository/{expected_hash}"
    assert "user" not in identity
    assert "synthetic" not in identity
    assert "token" not in identity
    assert "git.example.invalid" not in identity


@pytest.mark.parametrize("remote", [None, "", "not-a-remote", "file:///tmp/repo.git"])
def test_manifest_uses_unknown_for_unparseable_repository(remote: str | None) -> None:
    assert generate_manifest.normalize_repository(remote) == "UNKNOWN"


def test_manifest_allows_only_its_reserved_output_or_custom_output(
    tmp_path: Path,
) -> None:
    canonical = generate_manifest.resolve_output_path(
        tmp_path,
        "artifacts/release-manifest.json",
    )
    custom = generate_manifest.resolve_output_path(tmp_path, "artifacts/custom-manifest.json")

    assert canonical == (tmp_path / "artifacts" / "release-manifest.json").resolve()
    assert custom == (tmp_path / "artifacts" / "custom-manifest.json").resolve()
    for reserved in [
        "artifacts/checksums.sha256",
        "artifacts/checksums.txt",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
        "artifacts/eval-report.json",
    ]:
        assert_output_rejected(tmp_path, reserved, "reserved release artifact")
