from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from scripts.agent_quality_lib import failure, semantic


def write_python(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def valid_failure_case(state: str = "OBSERVED") -> dict:
    payload = {
        "schema_version": "1",
        "failure_id": "failure.safe-case",
        "task_class": "synthetic-task",
        "state": state,
        "safe_symptom_summary": "Synthetic invariant mismatch without raw values.",
        "minimal_synthetic_fixture_ref": "evals/agentic/fixtures/safe-case.json",
        "minimal_synthetic_fixture_hash": "a" * 64,
        "expected_invariant_id": "invariant.safe-case",
        "grader_id": "grader.safe-case",
        "first_observed_date": "2026-07-26",
        "last_reproduced_date": None,
        "affected_configuration_hashes": ["b" * 64],
        "review_refs": ["local/reviews/safe-case.json"],
    }
    state_index = failure.LIFECYCLE.index(state)
    if state_index >= failure.LIFECYCLE.index("REPRODUCED"):
        payload["last_reproduced_date"] = "2026-07-26"
    if state_index >= failure.LIFECYCLE.index("GRADER_VALIDATED"):
        payload["review_refs"].append("local/reviews/grader-safe-case.json")
    return payload


def test_semantic_summary_is_sorted_deterministic_and_source_free(tmp_path: Path) -> None:
    write_python(
        tmp_path,
        "src/sample.py",
        "\n".join(
            (
                "import zeta",
                "from alpha.beta import item",
                'FAILURE = "QUALITY_FAILURE"',
                "_private = 'SENSITIVE_CANARY'",
                "class PublicClass:",
                "    pass",
                "def public_api():",
                '    return "SECOND_REASON"',
                "def public_api():",
                "    return 2",
            )
        )
        + "\n",
    )

    first = semantic.summarize_python_files(tmp_path, ["src/sample.py"])
    second = semantic.summarize_python_files(tmp_path, ["src/sample.py"])

    assert first == second
    assert first["performed_actions"] == []
    item = first["files"][0]
    assert item["path"] == "src/sample.py"
    assert item["line_count"] == 10
    assert item["imports"] == ["alpha.beta", "zeta"]
    assert item["reason_code_values"] == ["QUALITY_FAILURE", "SECOND_REASON", "SENSITIVE_CANARY"]
    assert item["duplicate_top_level_definitions"] == ["public_api"]
    assert item["public_top_level_symbols"] == [
        {"kind": "variable", "name": "FAILURE"},
        {"kind": "class", "name": "PublicClass"},
        {"kind": "function", "name": "public_api"},
    ]
    assert "return 2" not in str(first)


@pytest.mark.parametrize(
    ("relative", "reason"),
    [
        ("../outside.py", "PYTHON_PATH_INVALID"),
        ("src\\sample.py", "PYTHON_PATH_INVALID"),
        ("/absolute.py", "PYTHON_PATH_INVALID"),
        ("C:/absolute.py", "PYTHON_PATH_INVALID"),
        ("src/sample.txt", "PYTHON_PATH_INVALID"),
    ],
)
def test_semantic_summary_rejects_unsafe_paths(
    tmp_path: Path, relative: str, reason: str
) -> None:
    with pytest.raises(semantic.SemanticInputError, match=reason):
        semantic.summarize_python_files(tmp_path, [relative])


def test_semantic_summary_rejects_symlink_oversize_and_invalid_syntax(
    tmp_path: Path,
) -> None:
    write_python(tmp_path, "src/real.py", "value = 1\n")
    link = tmp_path / "src" / "link.py"
    try:
        link.symlink_to(tmp_path / "src" / "real.py")
    except OSError:
        pass
    else:
        with pytest.raises(
            semantic.SemanticInputError, match="PYTHON_SYMLINK_NOT_ALLOWED"
        ):
            semantic.summarize_python_files(tmp_path, ["src/link.py"])

    (tmp_path / "src" / "large.py").write_bytes(
        b"x" * (semantic.MAX_SOURCE_BYTES + 1)
    )
    with pytest.raises(semantic.SemanticInputError, match="PYTHON_FILE_TOO_LARGE"):
        semantic.summarize_python_files(tmp_path, ["src/large.py"])

    write_python(tmp_path, "src/bad.py", "def broken(:\n")
    with pytest.raises(semantic.SemanticInputError, match="PYTHON_SYNTAX_INVALID"):
        semantic.summarize_python_files(tmp_path, ["src/bad.py"])


def test_semantic_comparison_reports_contract_blockers_without_source(
    tmp_path: Path,
) -> None:
    write_python(
        tmp_path,
        "baseline/api.py",
        'import decimal\nREASON = "OLD_REASON"\ndef public(value):\n    return value\n',
    )
    write_python(
        tmp_path,
        "candidate/api.py",
        'import fractions\nREASON = "NEW_REASON"\ndef changed(value):\n    return value\n'
        "def changed(value):\n    return value\n",
    )
    baseline = semantic.summarize_python_files(tmp_path, ["baseline/api.py"])
    candidate = semantic.summarize_python_files(tmp_path, ["candidate/api.py"])
    baseline["files"][0]["path"] = "api.py"
    candidate["files"][0]["path"] = "api.py"

    result = semantic.compare_semantic_summaries(baseline, candidate)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == [
        "DEPENDENCY_SET_CHANGED",
        "DUPLICATE_TOP_LEVEL_DEFINITION",
        "PUBLIC_API_CHANGED",
        "REASON_CODE_VOCABULARY_CHANGED",
    ]
    assert result["blockers"] == [
        {
            "categories": result["reason_codes"],
            "path": "api.py",
        }
    ]
    assert "return value" not in str(result)
    assert result["performed_actions"] == []


def test_semantic_comparison_passes_identical_surfaces(tmp_path: Path) -> None:
    write_python(tmp_path, "api.py", 'import json\nSTATUS = "PASS"\ndef run():\n    pass\n')
    summary = semantic.summarize_python_files(tmp_path, ["api.py"])
    assert semantic.compare_semantic_summaries(summary, deepcopy(summary)) == {
        "schema_version": "1",
        "status": "PASS",
        "reason_codes": [],
        "blockers": [],
        "comparison_summary": {
            "baseline_file_count": 1,
            "blocker_count": 0,
            "candidate_file_count": 1,
        },
        "performed_actions": [],
    }


def test_failure_case_accepts_exact_safe_shape_without_mutation() -> None:
    payload = valid_failure_case()
    original = deepcopy(payload)

    first = failure.validate_failure_case(payload)
    second = failure.validate_failure_case(payload)

    assert first == second
    assert first["status"] == "PASS"
    assert first["reason_codes"] == []
    assert first["performed_actions"] == []
    assert payload == original


@pytest.mark.parametrize(
    ("mutate", "reason"),
    [
        (lambda item: item.update({"raw_payload": "x"}), "FAILURE_CASE_KEY_SET_INVALID"),
        (lambda item: item.pop("grader_id"), "FAILURE_CASE_KEY_SET_INVALID"),
        (
            lambda item: item.update({"safe_symptom_summary": "raw_payload: private-value"}),
            "SAFE_SYMPTOM_SUMMARY_INVALID",
        ),
        (
            lambda item: item.update({"safe_symptom_summary": "Observed at C:/private/input.txt"}),
            "SAFE_SYMPTOM_SUMMARY_INVALID",
        ),
        (
            lambda item: item.update({"minimal_synthetic_fixture_ref": "../private.json"}),
            "MINIMAL_SYNTHETIC_FIXTURE_REF_INVALID",
        ),
        (
            lambda item: item.update({"review_refs": ["C:/private/review.json"]}),
            "REVIEW_REFS_INVALID",
        ),
        (
            lambda item: item.update({"review_refs": ["local/reviews/review."]}),
            "REVIEW_REFS_INVALID",
        ),
        (
            lambda item: item.update({"review_refs": ["local/reviews/review "]}),
            "REVIEW_REFS_INVALID",
        ),
        (
            lambda item: item.update({"review_refs": ["local/reviews/review?.json"]}),
            "REVIEW_REFS_INVALID",
        ),
        (
            lambda item: item.update(
                {
                    "minimal_synthetic_fixture_ref":
                        "evals/agentic/fixtures/case./input.json"
                }
            ),
            "MINIMAL_SYNTHETIC_FIXTURE_REF_INVALID",
        ),
        (
            lambda item: item.update({"affected_configuration_hashes": ["not-a-hash"]}),
            "AFFECTED_CONFIGURATION_HASHES_INVALID",
        ),
        (
            lambda item: item.update({"affected_configuration_hashes": []}),
            "AFFECTED_CONFIGURATION_HASHES_INVALID",
        ),
        (
            lambda item: item.update({"first_observed_date": "2026-02-30"}),
            "FIRST_OBSERVED_DATE_INVALID",
        ),
    ],
)
def test_failure_case_rejects_malformed_or_unsafe_content(
    mutate, reason: str
) -> None:
    payload = valid_failure_case()
    mutate(payload)
    result = failure.validate_failure_case(payload)
    assert result["status"] == "FAIL"
    assert reason in result["reason_codes"]
    assert "private-value" not in str(result)
    assert "C:/private" not in str(result)


def test_failure_lifecycle_allows_only_exact_adjacent_transitions() -> None:
    for current_state, next_state in zip(
        failure.LIFECYCLE, failure.LIFECYCLE[1:]
    ):
        result = failure.validate_transition(current_state, next_state)
        assert result["status"] == "PASS"
        assert result["reason_codes"] == []
        assert result["performed_actions"] == []

    for current_state, next_state in (
        ("OBSERVED", "SANITIZED"),
        ("SANITIZED", "QUARANTINED"),
        ("REGRESSION", "REGRESSION"),
        ("DEPRECATED", "OBSERVED"),
    ):
        result = failure.validate_transition(current_state, next_state)
        assert result["status"] == "BLOCKED"
        assert result["reason_codes"] == ["LIFECYCLE_TRANSITION_INVALID"]

    invalid = failure.validate_transition("UNKNOWN", "OBSERVED")
    assert invalid["status"] == "FAIL"
    assert invalid["reason_codes"] == ["STATE_INVALID"]


@pytest.mark.parametrize(
    ("state", "mutation", "reason"),
    [
        (
            "REPRODUCED",
            {"last_reproduced_date": None},
            "REPRODUCED_STATE_EVIDENCE_MISSING",
        ),
        (
            "HUMAN_REVIEWED",
            {"review_refs": []},
            "HUMAN_REVIEW_EVIDENCE_MISSING",
        ),
        (
            "REGRESSION",
            {"review_refs": ["local/reviews/safe-case.json"]},
            "GRADER_VALIDATION_EVIDENCE_MISSING",
        ),
    ],
)
def test_failure_case_requires_state_specific_evidence(
    state: str, mutation: dict, reason: str
) -> None:
    payload = valid_failure_case(state)
    payload.update(mutation)

    result = failure.validate_failure_case(payload)

    assert result["status"] == "FAIL"
    assert reason in result["reason_codes"]


def test_failure_case_rejects_reproduction_date_before_observation() -> None:
    payload = valid_failure_case("REPRODUCED")
    payload["last_reproduced_date"] = "2026-07-25"

    result = failure.validate_failure_case(payload)

    assert result["status"] == "FAIL"
    assert "REPRODUCTION_DATE_ORDER_INVALID" in result["reason_codes"]


def test_failure_transition_validates_case_and_does_not_write() -> None:
    payload = valid_failure_case("QUARANTINED")
    original = deepcopy(payload)

    result = failure.validate_failure_transition(payload, "SANITIZED")

    assert result["status"] == "PASS"
    assert result["transition_summary"] == {
        "current_state": "QUARANTINED",
        "next_state": "SANITIZED",
    }
    assert payload == original
