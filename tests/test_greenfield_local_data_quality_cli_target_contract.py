from __future__ import annotations

import re
from pathlib import Path

from scripts.render_template import BASE_OUTPUTS_BY_TIER, PROFILE_OUTPUTS_BY_TIER


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "GREENFIELD_LOCAL_DATA_QUALITY_CLI_TARGET_CONTRACT.md"


def contract_text() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def test_candidate_identity_and_contract_only_boundary_are_fixed() -> None:
    text = contract_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = normalize_ws(section(text, "Basis"))
    decision = section(text, "Candidate Decision")

    assert "greenfield_local_data_quality_cli_target_selected_without_repository_creation_or_implementation" in decision
    assert "Status: CONTRACT_ONLY" in decision
    assert "Target alias: local-data-quality-cli" in decision
    assert "Runtime profile: python_cli" in decision
    assert "Render tier: standard" in decision
    assert "Rendered file count: 14" in decision
    assert "does not create, inspect, initialize, render into, or implement" in purpose
    assert "owner-selected target path was absent" in basis
    assert "does not create it" in basis
    assert not re.search(r"[A-Za-z]:[\\/]", text)

    for allowed_file in [
        "docs/GREENFIELD_LOCAL_DATA_QUALITY_CLI_TARGET_CONTRACT.md",
        "tests/test_greenfield_local_data_quality_cli_target_contract.py",
    ]:
        assert f"`{allowed_file}`" in allowed

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`",
        "scripts",
        "templates",
        "examples",
        "schemas",
        "gates",
        "workflows",
        "artifacts",
        "corpus membership",
    ]:
        assert no_touch in allowed


def test_csv_input_and_exact_json_rule_schema_are_defined() -> None:
    text = contract_text()
    cli = normalize_ws(section(text, "Future CLI"))
    csv_input = normalize_ws(section(text, "CSV Input Contract"))
    rules = normalize_ws(section(text, "JSON Rules Contract"))

    assert (
        "python -m local_data_quality_cli \\ --input <CSV_PATH> \\ "
        "--rules <RULES_JSON> \\ [--json]"
    ) in cli
    for expected in [
        "one regular CSV file",
        "UTF-8 or UTF-8 with BOM",
        "delimiter is a comma",
        "exactly one header row",
        "header names are non-empty and unique",
        "every data row has the same field count as the header",
    ]:
        assert expected in csv_input

    expected_rule_keys = [
        "schema_version",
        "required_columns",
        "non_empty_columns",
        "unique_columns",
        "numeric_columns",
    ]
    for key in expected_rule_keys:
        assert f"`{key}`" in rules
    assert rules.count("- `") == len(expected_rule_keys)
    assert '`schema_version` must be the string `"1"`' in rules
    assert "exactly these keys" in rules
    assert "independent per-column uniqueness" in rules
    assert "Composite keys and cross-column uniqueness are not part of version 1" in rules


def test_validation_meaning_and_bounded_limits_are_explicit() -> None:
    text = contract_text()
    product = normalize_ws(section(text, "Product Contract"))
    csv_input = normalize_ws(section(text, "CSV Input Contract"))
    rules = normalize_ws(section(text, "JSON Rules Contract"))
    semantics = normalize_ws(section(text, "Validation Semantics"))

    for expected in [
        "required-column presence",
        "empty values in configured non-empty columns",
        "duplicate non-empty values in configured unique columns",
        "numeric conversion failures in configured numeric columns",
        "input data-row and column counts",
    ]:
        assert expected in product

    for expected in ["10 MiB", "100,000 data rows", "256 columns", "row-width mismatch"]:
        assert expected in csv_input
    assert "no more than 64 columns" in rules

    for expected in [
        "trimming surrounding whitespace",
        "repeated non-empty decoded values after the first occurrence",
        "Empty values are excluded from uniqueness counting",
        "standard-library decimal parsing",
        "Non-finite values are rejected",
        "aggregate counts only",
    ]:
        assert expected in semantics


def test_stdout_output_status_and_exit_contracts_are_bounded() -> None:
    text = contract_text()
    cli = normalize_ws(section(text, "Future CLI"))
    output = normalize_ws(section(text, "Output Contract"))
    statuses = normalize_ws(section(text, "Status And Exit Codes"))

    for expected in [
        "Default stdout is one bounded summary line",
        "deterministic JSON object with sorted keys and exactly one final newline",
        "must not exceed 8 KiB",
        "`performed_actions` is always `[]`",
        "must not contain raw rows, cell values, absolute paths",
        "No report, artifact, receipt, trace, or audit file is persisted",
    ]:
        assert expected in output

    top_level_fields = [
        "schema_version",
        "tool_id",
        "status",
        "reason_codes",
        "input_summary",
        "rule_summary",
        "issue_summary",
        "performed_actions",
    ]
    for field in top_level_fields:
        assert f"`{field}`" in output
    assert "The JSON top-level fields are exactly" in output
    assert "There is no output-path option, write option" in cli

    for expected in [
        "`PASS`: both inputs are valid and no violation is present; exit `0`",
        "`FAIL`: CSV or rules are malformed",
        "`ENVIRONMENT BLOCKED`: an input cannot be opened",
        "`NOT RUN`: required CLI arguments are missing",
    ]:
        assert expected in statuses
    assert statuses.count("exit `1`") == 2
    assert "exit `2`" in statuses


def test_python_cli_standard_render_surface_is_exactly_fourteen_files() -> None:
    render_contract = section(contract_text(), "Render Contract")
    documented = re.findall(r"^\d+\. `([^`]+)`$", render_contract, flags=re.MULTILINE)
    expected = [
        *BASE_OUTPUTS_BY_TIER["standard"],
        *PROFILE_OUTPUTS_BY_TIER["standard"],
    ]

    assert "runtime profile: `python_cli`" in render_contract
    assert "render tier: `standard`" in render_contract
    assert "exact rendered file count: `14`" in render_contract
    assert documented == expected
    assert len(documented) == 14
    assert "The contract does not authorize a\nrender, target write, overwrite" in render_contract


def test_safety_non_goals_verification_and_next_step_remain_separate() -> None:
    text = contract_text()
    safety = normalize_ws(section(text, "Safety And Data Boundary"))
    non_goals = normalize_ws(section(text, "Non-goals"))
    verification = normalize_ws(section(text, "Verification"))
    next_step = normalize_ws(section(text, "Next Step"))

    for expected in [
        "Only synthetic CSV and JSON fixtures",
        "Actual business, personal, customer, private",
        "absolute path must not be added",
        "Target repository creation, `git init`, rendering, package installation",
        "`performed_actions=[]`",
    ]:
        assert expected in safety

    for forbidden in [
        "CSV modification or cleanup",
        "output-file or report persistence",
        "recursive directory scanning",
        "JSON, Excel, spreadsheet, database, or archive data input",
        "network, API, remote storage, AI, or LLM use",
        "visualization or dashboard generation",
        "an external dependency",
        "target creation, `git init`, render, implementation",
        "corpus digest or release-evidence regeneration",
    ]:
        assert forbidden in non_goals

    for expected in [
        "focused contract suite reports six passing tests",
        "standalone eval reports all cases passing",
        "all nine quality gates pass",
        "all five release checksums match",
        "exact approved 34-source corpus remains valid",
        "only the two allowed files differ",
    ]:
        assert expected in verification

    assert "Greenfield Repository Initialization" in next_step
    assert "exact target path, directory creation, `git init`" in next_step
    assert "operating-system temporary `python_cli` plus `standard` render probe" in next_step
    assert "CSV CLI implementation remains a later, separately approved step" in next_step
