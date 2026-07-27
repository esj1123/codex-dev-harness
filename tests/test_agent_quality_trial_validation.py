from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.agent_quality_lib import (
    canonical_json_bytes,
    load_json_file,
    normalize_fingerprint,
    sha256_json,
    validate_run,
)
from scripts.agent_quality_lib.contracts import (
    AgentQualityValidationError,
    MAX_JSON_BYTES,
)
from scripts.agent_quality_lib.fingerprint import CONFIGURATION_FIELDS


def base_fingerprint() -> dict:
    return {
        "harness_commit": "a" * 40,
        "target_base_commit": "b" * 40,
        "contract_basis_sha": "c" * 40,
        "work_package_plan_digest": "d" * 64,
        "agent_adapter_id": "codex-local",
        "agent_adapter_version": "1.0.0",
        "model_id": "gpt-5.6-sol",
        "reasoning_profile": "high",
        "task_contract_hash": "e" * 64,
        "tool_policy_hash": "f" * 64,
        "skill_set_hash": "0" * 64,
        "approved_corpus_digest": "1" * 64,
        "dependency_lock_hash": "2" * 64,
        "environment_profile_id": "windows-python-3.12",
        "verification_suite_id": "agentic-v1",
        "grader_version": "1.0.0",
    }


def valid_run() -> dict:
    required_command_ids = ["focused_pytest"]
    return {
        "schema_version": "1",
        "run_id": "run-001",
        "task_id": "numeric-range-parser",
        "trial_id": "trial-001",
        "suite_id": "agentic-regression-v1",
        "task_class": "feature",
        "criticality": "normal",
        "fingerprint": normalize_fingerprint(base_fingerprint()),
        "execution": {
            "status": "PASS",
            "reason_codes": [],
            "verification_contract_hash": "3" * 64,
            "interpreter_id": "python-3.12.13-pytest-9.0.3",
            "required_command_ids": required_command_ids,
            "completed_command_ids": required_command_ids,
        },
        "grading": {
            "functional_correctness": "PASS",
            "contract_adherence": "PASS",
            "scope_adherence": "PASS",
            "semantic_consistency": "PASS",
            "architectural_consistency": "PASS",
            "safety_compliance": "PASS",
            "reproducibility": "PASS",
            "blocker_count": 0,
            "invariant_results": [
                {
                    "invariant_id": "FINITE_DECIMAL_FORMS_ACCEPTED",
                    "grader_id": "numeric-rules-grader-v1",
                    "status": "PASS",
                    "result_hash": "4" * 64,
                }
            ],
        },
        "metrics": {
            "critical_failure_count": 0,
            "scope_violation_count": 0,
            "safety_violation_count": 0,
            "postflight_block_count": 0,
            "contract_reopen_count": 0,
            "semantic_blocker_count": 0,
            "integration_fix_file_count": 0,
            "integration_fix_line_count": 0,
            "holdout_passed_count": 2,
            "holdout_failed_count": 0,
        },
        "evidence_refs": ["local/agent-quality/run-001/summary.json"],
        "performed_actions": ["local_write", "execute", "commit", "review"],
    }


def assert_run_issues(payload: object, expected: list[str]) -> None:
    with pytest.raises(AgentQualityValidationError) as error:
        validate_run(payload)
    assert list(error.value.issues) == expected


def test_canonical_json_and_hash_are_compact_sorted_and_stable() -> None:
    left = {"z": [3, 2, 1], "a": {"text": "safe"}}
    right = {"a": {"text": "safe"}, "z": [3, 2, 1]}
    expected = b'{"a":{"text":"safe"},"z":[3,2,1]}'

    assert canonical_json_bytes(left) == expected
    assert canonical_json_bytes(right) == expected
    assert sha256_json(left) == hashlib.sha256(expected).hexdigest()


def test_normalize_fingerprint_computes_stable_ids_without_mutation() -> None:
    source = base_fingerprint()
    before = copy.deepcopy(source)
    first = normalize_fingerprint(source)
    second = normalize_fingerprint(dict(reversed(list(source.items()))))
    configuration = {key: source[key] for key in CONFIGURATION_FIELDS}

    assert source == before
    assert first == second
    assert first["configuration_id"] == sha256_json(configuration)
    run_material = {key: value for key, value in first.items() if key != "run_fingerprint_id"}
    assert first["run_fingerprint_id"] == sha256_json(run_material)
    assert first["comparability"] == "FULL"
    assert first["unknown_fields"] == []


@pytest.mark.parametrize(
    "field",
    [
        "agent_adapter_version",
        "model_id",
        "reasoning_profile",
        "approved_corpus_digest",
        "dependency_lock_hash",
    ],
)
def test_unknown_fingerprint_value_forces_partial_comparability(field: str) -> None:
    source = base_fingerprint()
    source[field] = "UNKNOWN"

    normalized = normalize_fingerprint(source)

    assert normalized["comparability"] == "PARTIAL"
    assert normalized["unknown_fields"] == [field]
    payload = {**valid_run(), "fingerprint": normalized}
    assert validate_run(payload) == payload


def test_validate_run_accepts_exact_safe_schema_and_is_deterministic() -> None:
    payload = valid_run()

    first = validate_run(payload)
    second = validate_run(copy.deepcopy(payload))

    assert first == payload == second
    assert first is not payload
    assert first["fingerprint"] is not payload["fingerprint"]


def test_validate_run_rejects_unknown_top_level_and_nested_fields() -> None:
    payload = valid_run()
    payload["prompt"] = "hidden"
    assert_run_issues(payload, ["RUN_KEY_SET_INVALID"])

    payload = valid_run()
    payload["execution"]["raw"] = "hidden"
    assert_run_issues(payload, ["EXECUTION_KEY_SET_INVALID"])


def test_validate_run_requires_complete_bound_verification_for_pass() -> None:
    payload = valid_run()
    payload["execution"]["completed_command_ids"] = []

    assert_run_issues(payload, ["VERIFICATION_COMMANDS_INCOMPLETE"])


def test_validate_run_accepts_historical_unbound_execution_summary() -> None:
    payload = valid_run()
    payload["execution"] = {"status": "FAIL", "reason_codes": ["HISTORICAL_RUN"]}
    payload["grading"].pop("invariant_results")

    assert validate_run(payload) == payload


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda run: run["grading"]["invariant_results"].append(
                copy.deepcopy(run["grading"]["invariant_results"][0])
            ),
            "INVARIANT_ID_DUPLICATE",
        ),
        (
            lambda run: run["grading"]["invariant_results"][0].__setitem__(
                "grader_id", "C:/private"
            ),
            "INVARIANT_GRADER_ID_INVALID",
        ),
        (
            lambda run: run["grading"]["invariant_results"][0].__setitem__(
                "status", "BLOCKED"
            ),
            "INVARIANT_STATUS_INVALID",
        ),
        (
            lambda run: run["grading"]["invariant_results"][0].__setitem__(
                "result_hash", "short"
            ),
            "INVARIANT_RESULT_HASH_INVALID",
        ),
    ],
)
def test_validate_run_rejects_invalid_invariant_evidence(
    mutation: object, expected: str
) -> None:
    payload = valid_run()
    mutation(payload)

    with pytest.raises(AgentQualityValidationError) as error:
        validate_run(payload)
    assert expected in error.value.issues


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda run: run.__setitem__("run_id", "C:/private"), "RUN_ID_INVALID"),
        (
            lambda run: run.__setitem__("task_id", "raw-output-review"),
            "TASK_ID_INVALID",
        ),
        (
            lambda run: run["evidence_refs"].__setitem__(0, "/absolute/path.json"),
            "EVIDENCE_REFS_INVALID",
        ),
        (
            lambda run: run["evidence_refs"].__setitem__(0, "local\\summary.json"),
            "EVIDENCE_REFS_INVALID",
        ),
        (
            lambda run: run["evidence_refs"].__setitem__(0, "local/../summary.json"),
            "EVIDENCE_REFS_INVALID",
        ),
        (
            lambda run: run["evidence_refs"].__setitem__(
                0, "local/agent-quality/transcript.json"
            ),
            "EVIDENCE_REFS_INVALID",
        ),
    ],
)
def test_validate_run_rejects_unsafe_identifiers_paths_and_text(
    mutate: object, expected: str
) -> None:
    payload = valid_run()
    mutate(payload)

    with pytest.raises(AgentQualityValidationError) as error:
        validate_run(payload)
    assert expected in error.value.issues


def test_validate_run_rejects_stale_fingerprint_derivations() -> None:
    payload = valid_run()
    payload["fingerprint"]["configuration_id"] = "9" * 64
    payload["fingerprint"]["comparability"] = "PARTIAL"
    payload["fingerprint"]["unknown_fields"] = ["model_id"]
    payload["fingerprint"]["run_fingerprint_id"] = "8" * 64

    assert_run_issues(
        payload,
        [
            "COMPARABILITY_MISMATCH",
            "CONFIGURATION_ID_MISMATCH",
            "RUN_FINGERPRINT_ID_MISMATCH",
            "UNKNOWN_FIELDS_MISMATCH",
        ],
    )


def test_validate_run_rejects_invalid_fingerprint_derivation_types() -> None:
    payload = valid_run()
    payload["fingerprint"]["configuration_id"] = 1
    payload["fingerprint"]["run_fingerprint_id"] = None
    payload["fingerprint"]["comparability"] = "READY"
    payload["fingerprint"]["unknown_fields"] = ["not_a_fingerprint_field"]

    assert_run_issues(
        payload,
        [
            "COMPARABILITY_INVALID",
            "CONFIGURATION_ID_INVALID",
            "RUN_FINGERPRINT_ID_INVALID",
            "UNKNOWN_FIELDS_INVALID",
        ],
    )


def test_validate_run_rejects_bool_metrics_duplicate_lists_and_bad_grades() -> None:
    payload = valid_run()
    payload["metrics"]["critical_failure_count"] = True
    payload["grading"]["safety_compliance"] = "PASS WITH NOTES"
    payload["execution"]["reason_codes"] = ["CHECK_FAILED", "CHECK_FAILED"]
    payload["performed_actions"] = ["execute", "execute"]

    assert_run_issues(
        payload,
        [
            "EXECUTION_REASON_CODES_INVALID",
            "GRADING_SAFETY_COMPLIANCE_INVALID",
            "METRICS_CRITICAL_FAILURE_COUNT_INVALID",
            "PERFORMED_ACTIONS_INVALID",
        ],
    )


def test_normalize_fingerprint_rejects_bad_keys_hashes_and_sensitive_values() -> None:
    source = base_fingerprint()
    source["model_id"] = "secret-model"
    source["task_contract_hash"] = "short"
    source["unexpected"] = "value"

    with pytest.raises(AgentQualityValidationError) as error:
        normalize_fingerprint(source)

    assert error.value.issues == ("FINGERPRINT_KEY_SET_INVALID",)

    del source["unexpected"]
    with pytest.raises(AgentQualityValidationError) as error:
        normalize_fingerprint(source)

    assert error.value.issues == ("MODEL_ID_INVALID", "TASK_CONTRACT_HASH_INVALID")


def test_load_json_file_accepts_bounded_utf8_without_writing(tmp_path: Path) -> None:
    source = tmp_path / "run.json"
    source.write_text('{"safe":"value"}\n', encoding="utf-8", newline="\n")
    before = source.read_bytes()

    assert load_json_file(source) == {"safe": "value"}
    assert source.read_bytes() == before
    assert sorted(path.name for path in tmp_path.iterdir()) == ["run.json"]


@pytest.mark.parametrize(
    ("content", "issue"),
    [
        (b'{"key":1,"key":2}', "JSON_DUPLICATE_KEY"),
        (b"{invalid", "JSON_INPUT_MALFORMED"),
        (b'{"value":NaN}', "JSON_INPUT_MALFORMED"),
        (b"\xff", "JSON_INPUT_UTF8_INVALID"),
        (b" " * (MAX_JSON_BYTES + 1), "JSON_INPUT_TOO_LARGE"),
    ],
    ids=("duplicate-key", "malformed", "non-json-number", "invalid-utf8", "oversized"),
)
def test_load_json_file_rejects_unsafe_inputs(
    tmp_path: Path, content: bytes, issue: str
) -> None:
    source = tmp_path / "run.json"
    source.write_bytes(content)

    with pytest.raises(AgentQualityValidationError) as error:
        load_json_file(source)

    assert error.value.issues == (issue,)


def test_load_json_file_rejects_missing_and_directory_inputs(tmp_path: Path) -> None:
    with pytest.raises(AgentQualityValidationError) as missing:
        load_json_file(tmp_path / "missing.json")
    with pytest.raises(AgentQualityValidationError) as directory:
        load_json_file(tmp_path)

    assert missing.value.issues == ("JSON_INPUT_NOT_REGULAR_FILE",)
    assert directory.value.issues == ("JSON_INPUT_NOT_REGULAR_FILE",)
