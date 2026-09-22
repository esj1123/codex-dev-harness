import json
import os
from pathlib import Path
import subprocess

import pytest

from scripts import ai_readiness_scanner as scanner


def write(path: Path, content: str = "# doc\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_ready_repo(root: Path) -> None:
    write(root / "README.md", "# Demo\n\nPurpose: project overview and current state.\n")
    write(root / "AGENTS.md", "read-only first\nside effects require approval\nverification required\n")
    write(root / "STATUS.md", "Current phase: seed\nNext recommended step: plan small batch work.\n")
    write(root / "ACCEPTANCE_TRACE.md", "acceptance evidence PASS FAIL NOT RUN\n")
    write(root / "docs" / "SAFETY_POLICY.md", "side effects\nprivate data\nsecrets prohibited\nread-only\n")
    write(root / "docs" / "VERIFICATION.md", "run scripts/quality_gate.py and local verification\n")
    write(root / "scripts" / "quality_gate.py", "print('synthetic')\n")
    write(root / "tests" / "test_demo.py", "def test_demo():\n    assert True\n")
    write(root / ".gitignore", ".env\n")


def test_ready_repo_scores_ready(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)

    result = scanner.scan_target(tmp_path)

    assert result.score == 16
    assert result.result == "READY_FOR_AI_ASSISTED_WORK"
    assert not [dimension for dimension in result.dimensions if dimension.status == "INSUFFICIENT_EVIDENCE"]


def test_missing_agents_reports_insufficient_evidence(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    (tmp_path / "AGENTS.md").unlink()

    result = scanner.scan_target(tmp_path)

    ai_rules = next(dimension for dimension in result.dimensions if dimension.name == "AI operating rules")
    assert ai_rules.score == 0
    assert ai_rules.status == "INSUFFICIENT_EVIDENCE"
    assert any("AGENTS.md missing" in item for item in ai_rules.evidence)


def test_missing_safety_policy_reports_insufficient_evidence(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    (tmp_path / "docs" / "SAFETY_POLICY.md").unlink()

    result = scanner.scan_target(tmp_path)

    safety = next(dimension for dimension in result.dimensions if dimension.name == "Safety boundary")
    assert safety.score == 0
    assert safety.status == "INSUFFICIENT_EVIDENCE"
    assert "safety policy missing" in safety.evidence


def test_high_risk_domain_path_names_are_flagged(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    write(tmp_path / "docs" / "plc_live_target_notes.md", "synthetic note\n")
    write(tmp_path / "outlook_mail" / "README.md", "synthetic note\n")
    write(tmp_path / "broker_finance" / "README.md", "synthetic note\n")
    write(tmp_path / "RSID" / "README.md", "synthetic note\n")

    result = scanner.scan_target(tmp_path)
    flag_names = {flag.name for flag in result.risk_flags}

    assert "PLC_DEVICE_LIVE_TARGET" in flag_names
    assert "OUTLOOK_MAIL" in flag_names
    assert "BROKER_FINANCE" in flag_names
    assert "RSID" in flag_names


def test_forbidden_folders_are_skipped(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    write(tmp_path / "node_modules" / "plc_device" / "README.md", "synthetic note\n")
    write(tmp_path / "artifacts" / "secret_report.md", "synthetic note\n")
    write(tmp_path / "local" / "snapshot" / "quality_gate.py", "synthetic note\n")

    result = scanner.scan_target(tmp_path)
    skipped = "\n".join(result.skipped_paths)
    risk_paths = [path for flag in result.risk_flags for path in flag.paths]

    assert "node_modules" in skipped
    assert "artifacts" in skipped
    assert "local" in skipped
    assert all("node_modules/plc_device" not in path for path in risk_paths)
    assert all("artifacts/secret_report.md" not in path for path in risk_paths)
    assert all("local/snapshot" not in path for path in risk_paths)


def test_json_output_is_valid(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    result = scanner.scan_target(tmp_path)

    payload = json.loads(scanner.results_to_json([result]))

    assert payload[0]["target"] == str(tmp_path.resolve())
    assert payload[0]["score"] == 16
    assert payload[0]["result"] == "READY_FOR_AI_ASSISTED_WORK"


def test_markdown_output_contains_korean_report_sections(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    result = scanner.scan_target(tmp_path)

    markdown = scanner.results_to_markdown([result])

    assert "# AI 준비도 점검 보고서" in markdown
    assert "## 결론" in markdown
    assert "## 근거" in markdown
    assert "## 실행 체크리스트" in markdown
    assert "## Repo 점수표" in markdown


def test_scanner_does_not_write_into_scanned_target(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    scanner.scan_target(tmp_path)
    scanner.results_to_markdown([scanner.scan_target(tmp_path)])
    scanner.results_to_json([scanner.scan_target(tmp_path)])

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert after == before


def test_cli_json_output_is_stdout_only(tmp_path: Path, capsys) -> None:
    make_ready_repo(tmp_path)

    exit_code = scanner.main(["--json", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload[0]["score"] == 16
    assert captured.err == ""


def test_profile_policy_docs_count_as_equivalent_safety_and_verification(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "# Demo\n\nPurpose: project overview and current state.\n")
    write(tmp_path / "AGENTS.md", "read-only first\nside effects require approval\nverification required\n")
    write(tmp_path / "STATUS.md", "Current phase: seed\nNext recommended step: plan small batch work.\n")
    write(tmp_path / "ACCEPTANCE_TRACE.md", "acceptance evidence PASS FAIL NOT RUN\n")
    write(
        tmp_path / "SAFETY_POLICY.profile.md",
        "side effects\nprivate data\nsecrets prohibited\nread-only\n",
    )
    write(tmp_path / "VERIFICATION.profile.md", "document local verification expectations\n")

    result = scanner.scan_target(tmp_path)

    safety = next(dimension for dimension in result.dimensions if dimension.name == "Safety boundary")
    verification = next(dimension for dimension in result.dimensions if dimension.name == "Verification script")
    assert safety.score == 2
    assert safety.status == "PASS"
    assert verification.score == 1
    assert verification.status == "PARTIAL"
    assert "SAFETY_POLICY.profile.md" in result.inspected_paths
    assert "VERIFICATION.profile.md" in result.inspected_paths


def test_policy_read_does_not_follow_parent_link(tmp_path: Path) -> None:
    target = tmp_path / "target"
    outside = tmp_path / "outside"
    target.mkdir()
    outside.mkdir()
    write(outside / "SAFETY_POLICY.md", "read-only side effect private data synthetic marker\n")
    link = target / "docs"
    if os.name == "nt":
        command = (
            "New-Item -ItemType Junction "
            "-Path $env:HARNESS_TEST_JUNCTION_LINK "
            "-Target $env:HARNESS_TEST_JUNCTION_TARGET "
            "-ErrorAction Stop | Out-Null"
        )
        created = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            check=False,
            env={
                **os.environ,
                "HARNESS_TEST_JUNCTION_LINK": str(link),
                "HARNESS_TEST_JUNCTION_TARGET": str(outside),
            },
        )
        if created.returncode != 0:
            pytest.fail("Windows junction creation unavailable")
        assert link.is_junction()
    else:
        os.symlink(outside, link, target_is_directory=True)
        assert link.is_symlink()

    try:
        assert scanner.has_file(target, "docs/SAFETY_POLICY.md") is False
        assert scanner.safe_read_text(target, "docs/SAFETY_POLICY.md") == ""
        result = scanner.scan_target(target)
        safety = next(item for item in result.dimensions if item.name == "Safety boundary")
        assert safety.status == "INSUFFICIENT_EVIDENCE"
        assert "docs/SAFETY_POLICY.md" not in result.inspected_paths
        assert any(item.startswith("docs:") for item in result.skipped_paths)
    finally:
        if os.name == "nt":
            link.rmdir()
        else:
            link.unlink()
    assert (outside / "SAFETY_POLICY.md").is_file()


def _synthetic_tree_snapshot(root: Path) -> dict[str, bytes | None]:
    # Used only before synthetic link creation and after link cleanup.
    return {
        path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
        for path in root.rglob("*")
    }


def _create_scanner_test_link(link: Path, destination: Path) -> None:
    if os.name == "nt":
        # Junctions need no file-symlink privilege; use a directory even when
        # the blocked leaf has a policy/script filename.
        assert destination.is_dir()
        created = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "New-Item -ItemType Junction "
                "-Path $env:HARNESS_TEST_JUNCTION_LINK "
                "-Target $env:HARNESS_TEST_JUNCTION_TARGET "
                "-ErrorAction Stop | Out-Null",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
            env={
                **os.environ,
                "HARNESS_TEST_JUNCTION_LINK": str(link),
                "HARNESS_TEST_JUNCTION_TARGET": str(destination),
            },
        )
        if created.returncode != 0:
            pytest.fail("Windows junction creation unavailable")
        assert link.is_junction()
    else:
        os.symlink(destination, link, target_is_directory=destination.is_dir())
        assert link.is_symlink()


def _remove_scanner_test_link(link: Path) -> None:
    if os.name == "nt":
        if link.is_junction():
            link.rmdir()
    elif link.is_symlink():
        link.unlink()


@pytest.mark.parametrize(
    "relative", ["tests", "SAFETY_POLICY.profile.md", "verify.py", "plc_live_target"]
)
def test_blocked_links_are_not_score_or_inspected_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str,
) -> None:
    target = tmp_path / "target with spaces"
    outside = tmp_path / "outside with spaces"
    target.mkdir()
    outside.mkdir()
    write(target / "docs" / "VERIFICATION.md", "local verification policy\n")
    destination = outside
    if relative != "tests":
        write(outside / "source.txt", "read-only private data synthetic marker\n")
        if os.name != "nt" and relative != "plc_live_target":
            destination = outside / "source.txt"
    # The tests-Junction case deliberately points to an empty external dir.
    before_target = _synthetic_tree_snapshot(target)
    before_outside = _synthetic_tree_snapshot(outside)
    link = target / relative
    try:
        _create_scanner_test_link(link, destination)
        result = scanner.scan_target(target)
        dimensions = {item.name: item for item in result.dimensions}
        tests = dimensions["Tests or smoke checks"]
        verification = dimensions["Verification script"]
        assert (tests.score, tests.status) == (0, "INSUFFICIENT_EVIDENCE")
        assert tests.evidence == ["tests or smoke checks missing"]
        assert (verification.score, verification.status) == (1, "PARTIAL")
        assert verification.evidence == ["verification doc present"]
        assert dimensions["Safety boundary"].status == "INSUFFICIENT_EVIDENCE"
        assert result.inspected_paths == ["docs/VERIFICATION.md"]
        assert result.skipped_paths == [f"{relative}: link or reparse skipped"]
        paths, skipped = scanner.iter_repo_paths(target)
        assert link not in paths and all(link not in path.parents for path in paths)
        assert skipped == result.skipped_paths
        if relative == "SAFETY_POLICY.profile.md":
            assert scanner.has_file(target, relative) is False
            assert scanner.safe_read_text(target, relative) == ""
        if relative == "plc_live_target":
            risk = next(item for item in result.risk_flags if item.name == "PLC_DEVICE_LIVE_TARGET")
            assert risk.paths == [relative]
        assert all(
            not path.startswith(f"{relative}/")
            for flag in result.risk_flags for path in flag.paths
        )

        original_exists = Path.exists
        original_read_text = Path.read_text

        def guarded_exists(path: Path, *args, **kwargs):
            if path == link or link in path.parents:
                raise AssertionError("blocked entry must not reach exists()")
            return original_exists(path, *args, **kwargs)

        def guarded_read_text(path: Path, *args, **kwargs):
            if path == link or link in path.parents or path == outside or outside in path.parents:
                raise AssertionError("blocked external content must not be read")
            return original_read_text(path, *args, **kwargs)

        with monkeypatch.context() as guarded:
            guarded.setattr(Path, "exists", guarded_exists)
            guarded.setattr(Path, "read_text", guarded_read_text)
            assert scanner.scan_target(target) == result
    finally:
        _remove_scanner_test_link(link)
    assert _synthetic_tree_snapshot(target) == before_target
    assert _synthetic_tree_snapshot(outside) == before_outside


def test_normal_empty_tests_directory_and_policy_evidence_are_preserved(tmp_path: Path) -> None:
    make_ready_repo(tmp_path)
    (tmp_path / "tests" / "test_demo.py").unlink()
    before = _synthetic_tree_snapshot(tmp_path)

    paths, skipped = scanner.iter_repo_paths(tmp_path)
    result = scanner.scan_target(tmp_path)

    assert tmp_path / "tests" in paths
    assert scanner.has_dir(tmp_path, "tests") is True
    assert skipped == result.skipped_paths == []
    assert result.score == 16
    assert result.result == "READY_FOR_AI_ASSISTED_WORK"
    assert all(item.status == "PASS" for item in result.dimensions)
    assert result.inspected_paths == sorted([
        "README.md", "AGENTS.md", "STATUS.md", "ACCEPTANCE_TRACE.md",
        "docs/SAFETY_POLICY.md", "docs/VERIFICATION.md", "scripts/quality_gate.py",
    ])
    assert _synthetic_tree_snapshot(tmp_path) == before


@pytest.mark.parametrize("relative", ["tests", "verify.py"])
def test_unavailable_entries_are_not_score_or_inspected_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    write(target / "docs" / "VERIFICATION.md", "local verification policy\n")
    unavailable = target / relative
    if relative == "tests":
        unavailable.mkdir()
    else:
        write(unavailable, "synthetic verification stub\n")
    before = _synthetic_tree_snapshot(target)
    original_lstat = Path.lstat

    def denied_lstat(path: Path, *args, **kwargs):
        if path == unavailable:
            raise PermissionError("synthetic lstat denial")
        return original_lstat(path, *args, **kwargs)

    with monkeypatch.context() as guarded:
        guarded.setattr(Path, "lstat", denied_lstat)
        paths, skipped = scanner.iter_repo_paths(target)
        result = scanner.scan_target(target)

    dimensions = {item.name: item for item in result.dimensions}
    assert unavailable not in paths
    assert skipped == result.skipped_paths == [f"{relative}: unavailable skipped"]
    assert (dimensions["Tests or smoke checks"].score,
            dimensions["Tests or smoke checks"].status) == (0, "INSUFFICIENT_EVIDENCE")
    assert (dimensions["Verification script"].score,
            dimensions["Verification script"].status) == (1, "PARTIAL")
    assert result.inspected_paths == ["docs/VERIFICATION.md"]
    assert _synthetic_tree_snapshot(target) == before
