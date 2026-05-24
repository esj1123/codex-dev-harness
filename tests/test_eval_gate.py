from pathlib import Path

from scripts import run_eval
from scripts.gates import eval_gate


def test_eval_gate_wraps_run_eval_summary(monkeypatch) -> None:
    summary = run_eval.EvalSummary(
        True,
        [
            run_eval.EvalResult("render_structure", True, ["ok"]),
            run_eval.EvalResult("policy_phrases", True, ["ok"]),
        ],
    )
    monkeypatch.setattr(eval_gate.run_eval, "run_all", lambda repo_root: summary)

    result = eval_gate.run(Path("."))

    assert result.name == "eval_gate"
    assert result.passed is True
    assert "PASS render_structure" in result.messages


def test_eval_gate_reports_failure(monkeypatch) -> None:
    summary = run_eval.EvalSummary(False, [run_eval.EvalResult("forbidden_artifacts", False, ["bad file"])])
    monkeypatch.setattr(eval_gate.run_eval, "run_all", lambda repo_root: summary)

    result = eval_gate.run(Path("."))

    assert result.passed is False
    assert "bad file" in result.messages
