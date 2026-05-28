import json
from pathlib import Path

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
