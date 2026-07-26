from __future__ import annotations

import copy
import json
from pathlib import Path
import re

import pytest

from scripts import authority_manifest_check as checker
from scripts.gates.docs_gate import BASELINE_REQUIRED_DOCS


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / checker.MANIFEST_PATH


def load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def materialize_manifest_repo(tmp_path: Path, payload: dict[str, object]) -> Path:
    repo = tmp_path / "repo"
    classifications = [
        path
        for key in checker.CLASSIFICATION_KEYS
        for path in payload[key]
    ]
    for relative in classifications:
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"# STATUS.md\n\n## Current State\n\n`{payload['current_state']}`\n"
            if relative == "STATUS.md"
            else "fixture\n"
        )
        path.write_text(content, encoding="utf-8", newline="\n")
    manifest = repo / checker.MANIFEST_PATH
    manifest.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return repo


def test_current_tree_manifest_passes_with_exact_required_doc_coverage() -> None:
    raw_manifest = MANIFEST_PATH.read_text(encoding="utf-8")
    manifest = json.loads(raw_manifest)
    result = checker.inspect_manifest(repo_root=REPO_ROOT)

    assert raw_manifest == json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    assert "\r" not in raw_manifest
    assert re.search(r"\b[0-9a-f]{40}\b", raw_manifest) is None
    assert "run_id" not in raw_manifest
    assert result["status"] == "PASS"
    assert result["reason_codes"] == []
    assert result["current_state"] == "AGENT_QUALITY_BASELINE_NOT_ESTABLISHED"
    assert result["manifest_summary"]["required_doc_count"] == len(BASELINE_REQUIRED_DOCS) == 76
    assert result["manifest_summary"]["classified_required_doc_count"] == 76
    assert result["manifest_summary"]["default_read_order_count"] == 6
    assert result["manifest_summary"]["conditional_read_order_count"] == 4
    assert result["performed_actions"] == []


@pytest.mark.parametrize(
    ("mutation", "reason_code"),
    [
        (
            lambda payload: payload["historical_evidence"].pop(),
            "REQUIRED_DOC_CLASSIFICATION_MISSING",
        ),
        (
            lambda payload: payload["durable_policy"].append(payload["current_authority"][0]),
            "CLASSIFICATION_DUPLICATE",
        ),
    ],
)
def test_classification_gaps_and_duplicates_fail(mutation, reason_code: str) -> None:
    payload = load_manifest()
    mutation(payload)

    result = checker.validate_manifest(payload, repo_root=REPO_ROOT)

    assert result["status"] == "FAIL"
    assert reason_code in result["reason_codes"]


def test_default_read_order_is_exact_ordered_current_authority_subset() -> None:
    payload = load_manifest()

    assert payload["default_read_order"] == checker.EXPECTED_DEFAULT_READ_ORDER
    assert set(payload["default_read_order"]).issubset(set(payload["current_authority"]))
    assert "ACCEPTANCE_TRACE.md" not in payload["default_read_order"]
    assert "docs/PROFILE_MATRIX.md" not in payload["default_read_order"]
    assert payload["conditional_read_order"] == checker.EXPECTED_CONDITIONAL_READ_ORDER
    assert (
        payload["unlisted_document_policy"]
        == "non_authoritative_reference_only"
    )

    changed = copy.deepcopy(payload)
    changed["default_read_order"] = list(reversed(changed["default_read_order"]))
    result = checker.validate_manifest(changed, repo_root=REPO_ROOT)
    assert result["status"] == "FAIL"
    assert "DEFAULT_READ_ORDER_INVALID" in result["reason_codes"]


def test_status_current_state_must_match_manifest(tmp_path: Path) -> None:
    payload = load_manifest()
    repo = materialize_manifest_repo(tmp_path, payload)
    (repo / "STATUS.md").write_text(
        "# STATUS.md\n\n## Current State\n\n`READY_FOR_GREENFIELD_INITIALIZATION`\n",
        encoding="utf-8",
        newline="\n",
    )

    result = checker.inspect_manifest(repo_root=repo)

    assert result["status"] == "FAIL"
    assert "STATUS_CURRENT_STATE_MISMATCH" in result["reason_codes"]


@pytest.mark.parametrize(
    ("mutation", "reason_code"),
    [
        (
            lambda payload: payload.update(unexpected_key=True),
            "MANIFEST_KEY_SET_INVALID",
        ),
        (
            lambda payload: payload["historical_evidence"].append("../outside.md"),
            "CLASSIFICATION_PATH_UNSAFE",
        ),
    ],
)
def test_unknown_keys_and_unsafe_paths_fail(mutation, reason_code: str) -> None:
    payload = load_manifest()
    mutation(payload)

    result = checker.validate_manifest(payload, repo_root=REPO_ROOT)

    assert result["status"] == "FAIL"
    assert reason_code in result["reason_codes"]


@pytest.mark.parametrize(
    "unsafe_path",
    ["docs/CON", "docs/nul.txt", "docs/file?.md", "docs/file:stream"],
)
def test_shared_windows_path_policy_rejects_unsafe_authority_paths(
    unsafe_path: str,
) -> None:
    payload = load_manifest()
    payload["historical_evidence"].append(unsafe_path)

    result = checker.validate_manifest(payload, repo_root=REPO_ROOT)

    assert "CLASSIFICATION_PATH_UNSAFE" in result["reason_codes"]


def test_declared_file_must_exist_and_be_regular(tmp_path: Path) -> None:
    payload = load_manifest()
    repo = materialize_manifest_repo(tmp_path, payload)
    missing = repo / payload["durable_policy"][0]
    missing.unlink()

    result = checker.inspect_manifest(repo_root=repo)

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["DECLARED_FILE_MISSING_OR_NOT_REGULAR"]


def test_json_cli_is_deterministic_bounded_and_newline_terminated(capsys) -> None:
    args = ["--repo-root", str(REPO_ROOT), "--json"]

    first_exit = checker.main(args)
    first = capsys.readouterr().out
    second_exit = checker.main(args)
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert len(first.encode("utf-8")) <= checker.MAX_OUTPUT_BYTES
    assert str(REPO_ROOT) not in first
    result = json.loads(first)
    assert result["status"] == "PASS"
    assert result["performed_actions"] == []


def test_integration_only_path_definitions_match_final_boundary() -> None:
    payload = load_manifest()

    assert set(payload["integration_only_exact"]) == checker.EXPECTED_INTEGRATION_ONLY_EXACT
    assert set(payload["integration_only_prefixes"]) == checker.EXPECTED_INTEGRATION_ONLY_PREFIXES
    assert payload["integration_only_exact"] == sorted(payload["integration_only_exact"])
    assert payload["integration_only_prefixes"] == sorted(payload["integration_only_prefixes"])
