from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "DOWNSTREAM_TASK_CONTRACT_VALIDATOR_CANDIDATE_CONTRACT.md"


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


def test_phase_11c_scope_basis_and_candidate_decision_are_documented() -> None:
    text = contract_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Candidate Decision"))

    assert "Phase 11C is documentation and focused synthetic-test only" in purpose
    assert "does not implement or run a validator" in purpose
    assert "`standalone_downstream_task_contract_validator_candidate_selected_without_implementation`" in decision
    assert "does not authorize implementation or execution" in decision

    for allowed_file in [
        "docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_CANDIDATE_CONTRACT.md",
        "tests/test_downstream_task_contract_validator_candidate_contract.py",
    ]:
        assert f"`{allowed_file}`" in allowed

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`",
        "Phase 11B fixture",
        "scripts",
        "schemas",
        "gates",
        "workflows",
        "artifacts",
        "release evidence",
        "downstream repositories",
    ]:
        assert no_touch in allowed

    for basis_item in [
        "AGENTS.md",
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
        "docs/SAFETY_POLICY.md",
        "docs/AI_HANDOFF.md",
        "docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md",
        "docs/DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json",
        "tests/test_downstream_product_integration_boundary.py",
        "tests/test_downstream_task_contract_synthetic_fixture.py",
        "c4374781c71229b0134d28ab4235c36998c1d870",
        "29179099000",
        "86613472333",
    ]:
        assert f"`{basis_item}`" in basis


def test_selected_candidate_is_local_read_only_and_grants_no_authority() -> None:
    selected = normalize_ws(section(contract_text(), "Selected Candidate"))

    assert "Candidate id: `standalone_downstream_task_contract_validator`" in selected
    for expected in [
        "validate the exact Phase 11B contract structure",
        "distinguish `synthetic` and `filled` contract intent explicitly",
        "validate declared access, approval, command, and side-effect relationships",
        "reject unsafe paths, URLs, raw/private/live values",
        "bounded deterministic validation summary",
        "downstream access, network use, command execution, writes",
        "standard-library-only, local-only, read-only, and dry-run-only",
        "not a schema generator, command parser, command executor, approval verifier",
    ]:
        assert expected in selected


def test_future_implementation_files_and_cli_are_fixed_without_implementation() -> None:
    implementation = normalize_ws(section(contract_text(), "Future Implementation Contract"))

    for future_file in [
        "docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md",
        "scripts/downstream_task_contract_validator.py",
        "tests/test_downstream_task_contract_validator.py",
    ]:
        assert f"`{future_file}`" in implementation

    assert (
        "python scripts/downstream_task_contract_validator.py --contract <JSON_PATH> "
        "--contract-kind synthetic|filled --dry-run [--json]"
    ) in implementation
    for expected in [
        "`--contract` and `--contract-kind` are required",
        "`--dry-run` is required",
        "There is no write mode, stdin mode, output-path option",
        "contract placeholder only",
        "Phase 11C does not create the implementation plan, script, or runtime tests",
    ]:
        assert expected in implementation


def test_input_path_data_and_output_contracts_are_bounded() -> None:
    text = contract_text()
    input_contract = normalize_ws(section(text, "Input And Path Contract"))
    output = normalize_ws(section(text, "Output Contract"))

    for expected in [
        "repo-relative path that resolves inside the harness repository",
        "absolute path that resolves inside the operating-system temporary root",
        "regular `.json` file, UTF-8, and no larger than 64 KiB",
        "symlinks, junctions, other reparse points",
        "must never appear in stdout, JSON output, errors, logs, evidence references, or tracked files",
        "must not enumerate the input directory or read sibling files",
        "local absolute path",
        "backslash path",
        "parent traversal",
        "secret-like value",
        "Each string is bounded to 512 UTF-8 bytes",
        "`commands` is bounded to 32 entries",
        "scope path list is bounded to 64 entries",
    ]:
        assert expected in input_contract

    for field in [
        "schema_version",
        "validator_id",
        "dry_run",
        "contract_kind",
        "status",
        "reason_codes",
        "validation_summary",
        "declared_permission_summary",
        "external_state",
        "performed_actions",
    ]:
        assert f"`{field}`" in output

    for expected in [
        "one-line bounded summary",
        "deterministic JSON object with sorted keys and one final newline",
        "must not exceed 8 KiB",
        "`performed_actions` is always `[]`",
        "repository access, network read, command execution, and downstream write as `NOT RUN`",
        "must not include input paths, payload values, repository identifiers, commands, approval references",
        "There is no output file, tracked evidence, artifact, receipt, trace, audit log",
    ]:
        assert expected in output


def test_synthetic_filled_permission_status_and_exit_contracts_are_explicit() -> None:
    text = contract_text()
    synthetic = normalize_ws(section(text, "Synthetic Contract Validation"))
    filled = normalize_ws(section(text, "Filled Contract Validation"))
    permissions = normalize_ws(section(text, "Permission And Command Contract"))
    statuses = normalize_ws(section(text, "Status And Exit Codes"))

    for expected in [
        "exact Phase 11B top-level and nested key sets",
        "`schema_version=\"1\"`",
        "`synthetic=true`, `status=\"NOT RUN\"`, and `performed_actions=[]`",
        "exact 16 side-effect classes",
        "`PASS WITH NOTES`",
        "`SYNTHETIC_CONTRACT_VALID`",
    ]:
        assert expected in synthetic

    for expected in [
        "`schema_version=\"1\"` and `synthetic=false`",
        "no placeholder token anywhere",
        "owner approval, target-repository approval, and target-rules review",
        "at least one command with declared effect classes",
        "A valid filled contract returns `PASS`",
        "does not authenticate an approval reference",
        "authorize repository access, command execution, network use, writes, or downstream work",
    ]:
        assert expected in filled

    for side_effect in [
        "repository_access",
        "network_read",
        "local_write",
        "execute",
        "stage",
        "commit",
        "push",
        "pull_request",
        "merge",
        "workflow_dispatch",
        "artifact_upload",
        "tag",
        "release",
        "publish",
        "deploy",
        "live_action",
    ]:
        assert f"`{side_effect}`" in permissions

    for expected in [
        "`repository_access` must be authorized",
        "`local_read_only` permits only",
        "`remote_read_only` permits only",
        "`local_write` permits only",
        "`remote_write` may declare any of the 16 classes",
        "Every command effect class",
        "does not parse shell syntax",
        "does not claim that declared effects are complete",
    ]:
        assert expected in permissions

    for status in ["`NOT RUN`", "`ENVIRONMENT BLOCKED`", "`FAIL`", "`BLOCKED`", "`PASS WITH NOTES`", "`PASS`"]:
        assert status in statuses
    for expected in [
        "Exit code `0` means `PASS` or `PASS WITH NOTES`",
        "Exit code `1` means `BLOCKED`, `FAIL`, or `ENVIRONMENT BLOCKED`",
        "Exit code `2` means `NOT RUN` or CLI usage error",
        "never means that external approval evidence was authenticated",
    ]:
        assert expected in statuses


def test_failure_verification_non_goals_and_phase_11d_handoff_are_bounded() -> None:
    text = contract_text()
    failure = normalize_ws(section(text, "Failure Modes"))
    verification = section(text, "Verification")
    verification_normalized = normalize_ws(verification)
    non_goals = normalize_ws(section(text, "Non-goals"))
    next_step = normalize_ws(section(text, "Next Step"))

    for expected in [
        "missing, unreadable, malformed, invalid-UTF-8, or oversized input",
        "contract-kind and `synthetic` flag mismatch",
        "missing, extra, duplicate, or incorrectly typed fields",
        "unsafe URL, path, IP-like, secret-like, private, raw, or live value",
        "access-class and permission-ceiling conflict",
        "command effect without matching authorization",
        "non-empty `performed_actions`",
        "attempted file write, persistence, command execution, network call, downstream access",
        "must fail closed",
    ]:
        assert expected in failure

    for command in [
        "python -m pytest tests/test_downstream_task_contract_validator_candidate_contract.py",
        "python -m pytest tests/test_downstream_task_contract_synthetic_fixture.py",
        "python -m pytest tests/test_downstream_product_integration_boundary.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "python scripts/generate_checksums.py --verify",
        "python scripts/generate_corpus_digest.py --check --json",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert f"`{command}`" in verification
    for expected in ["487 full-suite tests", "nine quality gates", "five matching release checksums", "34 valid corpus sources"]:
        assert expected in verification_normalized
    assert "`python scripts/run_eval.py` is `NOT RUN`" in verification

    for forbidden in [
        "create `docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md`",
        "implement `scripts/downstream_task_contract_validator.py`",
        "create `tests/test_downstream_task_contract_validator.py`",
        "modify the Phase 11B fixture or create a filled contract",
        "create a JSON Schema",
        "add a gate, quality-gate integration, workflow, dependency, or runtime",
        "update `STATUS.md`, the capability roadmap, `ACCEPTANCE_TRACE.md`",
        "generate an artifact, receipt, trace, audit log, eval report, or release evidence",
        "locate, inspect, clone, fetch, render into, write, test, build, execute in",
        "execute MCP or Hermes",
    ]:
        assert forbidden in non_goals

    assert "separately approved Phase 11D task" in next_step
    assert "implement and test the standalone validator before any filled contract usage probe" in next_step
    assert "Neither Phase 11C nor its Local Verify authorizes a filled contract" in next_step
