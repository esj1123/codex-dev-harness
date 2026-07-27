from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_ROOT = REPO_ROOT / "evals" / "agentic"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_defines_quality_dimensions_and_boundaries() -> None:
    policy = (REPO_ROOT / "docs" / "AGENT_QUALITY_STABILITY_POLICY.md").read_text(
        encoding="utf-8"
    )
    for dimension in (
        "functional_correctness",
        "contract_adherence",
        "scope_adherence",
        "semantic_consistency",
        "architectural_consistency",
        "safety_compliance",
        "reproducibility",
    ):
        assert dimension in policy
    assert "raw prompts" in policy
    assert "not part of the five-file release checksum set" in policy
    assert "does not authorize agent runtime adapters" in policy
    assert "suite manifest hash" in policy.lower()
    assert "exactly one owner-held holdout result per run" in policy
    assert "does not authenticate" in policy


def test_agentic_schemas_are_strict_and_safe() -> None:
    schemas = {
        path.name: load_json(path)
        for path in sorted((AGENTIC_ROOT / "schemas").glob("*.schema.json"))
    }
    assert set(schemas) == {
        "agent-quality-baseline.schema.json",
        "agent-role-profiles.schema.json",
        "agent-run-v2.schema.json",
        "agent-run.schema.json",
        "failure-case.schema.json",
    }
    for schema in schemas.values():
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"]

    run_required = set(schemas["agent-run.schema.json"]["properties"]["fingerprint"]["required"])
    assert {
        "harness_commit",
        "target_base_commit",
        "contract_basis_sha",
        "work_package_plan_digest",
        "model_id",
        "task_contract_hash",
        "tool_policy_hash",
        "skill_set_hash",
        "approved_corpus_digest",
        "dependency_lock_hash",
        "verification_suite_id",
        "grader_version",
    } <= run_required
    execution = schemas["agent-run.schema.json"]["properties"]["execution"]
    assert len(execution["oneOf"]) == 2
    grading = schemas["agent-run.schema.json"]["properties"]["grading"]
    assert len(grading["oneOf"]) == 2
    invariant_results = grading["properties"]["invariant_results"]
    assert invariant_results["minItems"] == 1
    assert set(invariant_results["items"]["required"]) == {
        "invariant_id",
        "grader_id",
        "status",
        "result_hash",
    }
    baseline_required = set(schemas["agent-quality-baseline.schema.json"]["required"])
    assert {"suite_manifest_hash", "run_evidence_manifest"} <= baseline_required
    manifest = schemas["agent-quality-baseline.schema.json"]["properties"][
        "run_evidence_manifest"
    ]
    assert manifest["minItems"] == manifest["maxItems"] == 19
    assert set(manifest["items"]["required"]) == {
        "run_id",
        "task_id",
        "trial_id",
        "criticality",
        "run_hash",
        "run_fingerprint_id",
        "work_package_plan_digest",
        "strict_pass",
        "holdout_status",
    }
    for schema_name in ("agent-run.schema.json", "agent-quality-baseline.schema.json"):
        pattern = schemas[schema_name]["properties"]["evidence_refs"]["items"]["pattern"]
        assert "(?!/)" in pattern
        assert "\\.\\." in pattern
    failure = schemas["failure-case.schema.json"]
    assert failure["properties"]["affected_configuration_hashes"]["minItems"] == 1
    assert failure["properties"]["minimal_synthetic_fixture_ref"]["pattern"].startswith(
        "^evals/agentic/fixtures/"
    )
    assert len(failure["allOf"]) == 4
    run_v2 = schemas["agent-run-v2.schema.json"]
    assert run_v2["properties"]["schema_version"]["const"] == "2"
    assert {"agent_profile", "repository"} <= set(run_v2["required"])
    command_result = run_v2["$defs"]["commandResult"]
    assert {"argv_hash", "exit_code", "stdout_sha256", "stderr_sha256"} <= set(
        command_result["required"]
    )
    profile_schema = schemas["agent-role-profiles.schema.json"]
    assert profile_schema["properties"]["profiles"]["items"]["additionalProperties"] is False


def test_regression_suite_has_exact_tasks_and_trial_budget() -> None:
    suite = load_json(AGENTIC_ROOT / "suites" / "agentic-regression-v1.json")
    assert suite["suite_id"] == "agentic-regression-v1"
    assert suite["total_trials"] == 19
    assert suite["target_checkpoint"] == "da88f12d38d5cd6109a3a532b880bc4b723aef36"
    assert suite["required_configuration"]["model_id"] == "gpt-5.6-sol"
    assert suite["required_configuration"]["reasoning_profile"] == "high"
    assert [task["trials"] for task in suite["tasks"]] == [3, 5, 3, 3, 5]
    assert [task["task_id"] for task in suite["tasks"]] == [
        "numeric-range-parser",
        "numeric-range-evaluator",
        "allowed-values-parser",
        "allowed-values-evaluator",
        "allowed-values-integration",
    ]
    assert all(task["lane"] in {"feature", "integration"} for task in suite["tasks"])
    assert all(task["required_invariant_ids"] for task in suite["tasks"])
    assert all(task["invariant_grader_id"].endswith("-grader-v1") for task in suite["tasks"])
    assert all(
        task["verification_contract"]["interpreter_id"]
        == "python-3.12.13-pytest-9.0.3"
        for task in suite["tasks"]
    )
    assert all(
        task["verification_contract"]["commands"][0]["argv"][:3]
        == ["{PYTHON}", "-m", "pytest"]
        for task in suite["tasks"]
    )
    integration = suite["tasks"][-1]
    assert {
        "HISTORICAL_EVIDENCE_PRESERVED",
        "MALFORMED_SCHEMA_REGRESSION_COVERED",
    } <= set(integration["required_invariant_ids"])
    parser = suite["tasks"][2]
    assert "NON_ENCODABLE_UNICODE_FAILS_CLOSED" in parser[
        "required_invariant_ids"
    ]
    assert sum(task["trials"] for task in suite["tasks"]) == 19


def test_capability_suite_is_non_blocking_and_not_run() -> None:
    suite = load_json(AGENTIC_ROOT / "suites" / "capability-v1.json")
    assert suite["status"] == "NOT RUN"
    assert suite["suite_class"] == "capability"
    assert all(task["baseline_blocking"] is False for task in suite["tasks"])


def test_trial_prompt_excludes_raw_and_remote_surfaces() -> None:
    prompt = (
        REPO_ROOT / "prompts" / "task_contract" / "agent_quality_trial.md"
    ).read_text(encoding="utf-8")
    assert "exactly one local commit" in prompt
    assert "Do not access network" in prompt
    assert "owner-held holdouts" in prompt
    assert "Do not report raw test" in prompt
