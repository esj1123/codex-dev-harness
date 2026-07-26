from __future__ import annotations

import json
from pathlib import Path

from scripts import agent_quality
from tests.test_agent_quality_aggregation import make_aggregate, make_baseline
from tests.test_agent_quality_trial_validation import valid_run


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def test_validate_run_is_deterministic_and_does_not_echo_input(tmp_path: Path, capsys) -> None:
    path = tmp_path / "sensitive-name.json"
    write_json(path, valid_run())

    first_exit = agent_quality.main(["validate-run", "--run", str(path), "--json"])
    first = capsys.readouterr().out
    second_exit = agent_quality.main(["validate-run", "--run", str(path), "--json"])
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert str(path) not in first
    payload = json.loads(first)
    assert payload["status"] == "PASS"
    assert payload["validation_summary"] == {"comparability": "FULL", "run_count": 1}
    assert payload["performed_actions"] == []


def test_validate_run_rejects_outside_boundary_without_echo(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    allowed_root = tmp_path / "allowed"
    outside_root = tmp_path / "outside"
    allowed_root.mkdir()
    outside = outside_root / "run.json"
    write_json(outside, valid_run())
    monkeypatch.setattr(agent_quality, "READ_ROOTS", (allowed_root,))

    exit_code = agent_quality.main(["validate-run", "--run", str(outside), "--json"])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert json.loads(output)["reason_codes"] == ["JSON_INPUT_BOUNDARY_INVALID"]
    assert str(outside) not in output


def test_cli_usage_error_is_not_run_and_does_not_echo_raw_argument(capsys) -> None:
    exit_code = agent_quality.main(["validate-run", "--unknown", "private-value"])
    output = capsys.readouterr().out

    assert exit_code == 2
    assert json.loads(output)["status"] == "NOT RUN"
    assert "private-value" not in output


def test_validate_failure_is_read_only(tmp_path: Path, capsys) -> None:
    path = tmp_path / "case.json"
    write_json(
        path,
        {
            "schema_version": "1",
            "failure_id": "case-001",
            "task_class": "feature",
            "state": "OBSERVED",
            "safe_symptom_summary": "Synthetic invariant mismatch.",
            "minimal_synthetic_fixture_ref": "evals/agentic/fixtures/case-001.json",
            "minimal_synthetic_fixture_hash": "a" * 64,
            "expected_invariant_id": "INV-001",
            "grader_id": "grader-v1",
            "first_observed_date": "2026-07-26",
            "last_reproduced_date": None,
            "affected_configuration_hashes": ["b" * 64],
            "review_refs": [],
        },
    )
    before = path.read_bytes()

    exit_code = agent_quality.main(
        [
            "validate-failure",
            "--case",
            str(path),
            "--next-state",
            "QUARANTINED",
            "--json",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["status"] == "PASS"
    assert output["performed_actions"] == []
    assert path.read_bytes() == before


def test_write_baseline_refuses_wrong_path_and_existing_artifact(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    aggregate_path = tmp_path / "aggregate.json"
    write_json(aggregate_path, {"source_basis": {}})

    wrong = tmp_path / "wrong.json"
    wrong_exit = agent_quality.main(
        [
            "write-baseline",
            "--aggregate",
            str(aggregate_path),
            "--output",
            str(wrong),
            "--approval-ref",
            "test-approval",
            "--created-at",
            "2026-07-26T00:00:00Z",
        ]
    )
    wrong_output = json.loads(capsys.readouterr().out)

    exact = tmp_path / "agent-quality-baseline.json"
    exact.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(agent_quality, "BASELINE_PATH", exact)
    existing_exit = agent_quality.main(
        [
            "write-baseline",
            "--aggregate",
            str(aggregate_path),
            "--output",
            str(exact),
            "--approval-ref",
            "test-approval",
            "--created-at",
            "2026-07-26T00:00:00Z",
        ]
    )
    existing_output = json.loads(capsys.readouterr().out)

    assert wrong_exit == existing_exit == 1
    assert wrong_output["reason_codes"] == ["BASELINE_OUTPUT_PATH_INVALID"]
    assert existing_output["reason_codes"] == ["BASELINE_OVERWRITE_FORBIDDEN"]
    assert wrong.exists() is False


def test_compare_rejects_candidate_without_comparability(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    candidate = make_aggregate()
    candidate.pop("comparability")
    write_json(baseline_path, make_baseline())
    write_json(candidate_path, candidate)
    monkeypatch.setattr(agent_quality, "READ_ROOTS", (tmp_path,))

    exit_code = agent_quality.main(
        [
            "compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--json",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert output["status"] == "FAIL"
    assert output["reason_codes"] == ["AGENT_QUALITY_INPUT_INVALID"]


def test_write_baseline_rejects_incomplete_holdout_aggregate(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    aggregate_path = tmp_path / "aggregate.json"
    aggregate = make_aggregate()
    aggregate["metrics"]["holdout_passed_count"] = 1
    write_json(aggregate_path, aggregate)
    output_path = tmp_path / "agent-quality-baseline.json"
    monkeypatch.setattr(agent_quality, "READ_ROOTS", (tmp_path,))
    monkeypatch.setattr(agent_quality, "BASELINE_PATH", output_path)

    exit_code = agent_quality.main(
        [
            "write-baseline",
            "--aggregate",
            str(aggregate_path),
            "--output",
            str(output_path),
            "--approval-ref",
            "test-approval",
            "--created-at",
            "2026-07-26T00:00:00Z",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert output["status"] == "FAIL"
    assert output_path.exists() is False
