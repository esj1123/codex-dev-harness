# Downstream Task Contract Validator Implementation Plan

## Purpose

Implement the Phase 11D standalone validator selected by
`docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_CANDIDATE_CONTRACT.md`.

The implementation validates one explicitly supplied Phase 11B-format JSON
contract. It is local-only, standard-library-only, read-only, and dry-run-only.
It does not inspect a downstream repository. It does not authenticate approval evidence,
parse or execute declared commands, use network access, write output files, or
grant authority for a downstream action.

## Allowed Files

Phase 11D is limited to:

- `docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md`
- `scripts/downstream_task_contract_validator.py`
- `tests/test_downstream_task_contract_validator.py`

The Phase 11B fixture, Phase 11C candidate contract, `STATUS.md`,
`ACCEPTANCE_TRACE.md`, the capability roadmap, schemas, gates, workflows,
artifacts, audits, evals, templates, profiles, examples, dependencies, release
evidence, and downstream repositories are excluded.

## Command Contract

```text
python scripts/downstream_task_contract_validator.py --contract <JSON_PATH> --contract-kind synthetic|filled --dry-run [--json]
```

`--contract` and `--contract-kind` are required CLI arguments. Validation runs
only when `--dry-run` is present. There is no stdin, write, output-path,
repository-access, network, or execution mode.

The default output is one bounded summary line. `--json` emits deterministic
compact JSON with sorted keys and one final newline. Exit codes are `0` for
`PASS` or `PASS WITH NOTES`, `1` for `BLOCKED`, `FAIL`, or
`ENVIRONMENT BLOCKED`, and `2` for `NOT RUN` or CLI usage error.

## Input Boundary

The validator reads exactly one regular UTF-8 `.json` file no larger than
64 KiB. A relative path must resolve inside this harness repository. An
absolute path must resolve inside the operating-system temporary root.

Directories, symlinks, junctions, reparse points, parent traversal, URLs,
repo-relative escape, other absolute paths, invalid UTF-8, malformed JSON, and
oversized files fail closed. The validator does not enumerate the input
directory or read sibling files. Input paths and payload values never appear in
output.

## Validation Flow

Common validation checks:

- exact Phase 11B top-level and nested key sets;
- fixed policy lists, status values, stop conditions, and 16 side-effect
  classes;
- bounded strings, commands, scope paths, and reason codes;
- safe repo-relative path syntax and rejection of URL, IP-like, absolute-path,
  backslash-path, parent-traversal, secret-like, control-character, and raw/live
  material;
- non-empty declared command effects with no unknown or duplicate class;
- deterministic safe issue categories without rejected-value echo.

Synthetic mode requires the exact Phase 11B fixture identity, all required
placeholders, false approval flags, unauthorized permission records,
`status="NOT RUN"`, and `performed_actions=[]`. Success is
`PASS WITH NOTES / SYNTHETIC_CONTRACT_VALID`.

Filled mode requires `synthetic=false`, no placeholders, bounded concrete
selected fields, all three approval/review flags, a safe approval reference,
an approved `repository_access` permission, and command effects covered by
declared permissions. The access class is enforced as a permission ceiling.
Success is `PASS` for internal validation only; it does not verify external
facts or authorize execution.

## Output Contract

JSON output has exactly:

- `schema_version`
- `validator_id`
- `dry_run`
- `contract_kind`
- `status`
- `reason_codes`
- `validation_summary`
- `declared_permission_summary`
- `external_state`
- `performed_actions`

Output is capped at 8 KiB. It includes only fixed reason codes, safe status
categories, counts, and side-effect class names. It excludes the input path,
payload values, repository identifiers, commands, approval references,
branches, commits, scope values, raw JSON, excerpts, and matched unsafe values.

`external_state` fixes downstream repository access, network read, command
execution, and downstream write to `NOT RUN`. `performed_actions` is always
`[]`. No output file, artifact, receipt, trace, audit log, cache, or temporary
output is created.

## Status Precedence

1. `NOT RUN`: `--dry-run` absent.
2. `ENVIRONMENT BLOCKED`: filesystem permission or runtime input inspection
   error.
3. `FAIL`: malformed, invalid-UTF-8, oversized, structurally invalid, unsafe,
   or output-limit violation.
4. `BLOCKED`: missing input, unresolved filled placeholder, missing approval,
   command-permission conflict, or access-ceiling conflict.
5. `PASS WITH NOTES`: valid synthetic contract.
6. `PASS`: valid filled contract's internal selected-field validation.

The validator never converts a blocked or failed condition into success and
never treats declared approval data as authenticated evidence.

## Tests

Focused tests use only the tracked synthetic fixture and temporary synthetic
JSON copies. They cover:

- valid synthetic and filled contracts;
- missing dry-run and deterministic plain/JSON output;
- repository-relative and temporary-root path acceptance;
- path escape, URL, suffix, directory, link/reparse, missing, malformed,
  invalid-UTF-8, and size failures;
- exact keys, fixed policy lists, placeholder and contract-kind rules;
- approvals, permission ceilings, command-effect authorization, and fixed
  external `NOT RUN` state;
- bounded values and unsafe URL/path/IP/secret-like rejection;
- no payload/path disclosure and no persistence.

Tests do not clone, fetch, open, render into, build, execute in, or modify a
downstream repository. They do not call external services or execute a
declared contract command.

## Verification

Phase 11D verification includes:

- `python -m pytest tests/test_downstream_task_contract_validator.py`
- `python -m pytest tests/test_downstream_task_contract_validator_candidate_contract.py`
- `python -m pytest tests/test_downstream_task_contract_synthetic_fixture.py`
- `python -m pytest tests/test_downstream_product_integration_boundary.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `python scripts/generate_checksums.py --verify`
- `python scripts/generate_corpus_digest.py --check --json`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Release evidence, eval report, and corpus digest bytes must remain unchanged.
`python scripts/run_eval.py` is `NOT RUN` because Phase 11D does not change eval
behavior and must not mutate eval evidence.

## Non-goals And Next Step

Phase 11D does not create or persist a filled contract, run a filled-contract
usage probe, access a downstream repository, execute a declared command,
authenticate an approval, write a receipt or trace, change a schema or gate,
edit a workflow, regenerate evidence, run MCP or Hermes, or perform a commit,
push, review, release, publication, deployment, or live action through the
validator.

After the implementation commit is separately approved, pushed, and passes
clean Local Verify, the next task may be a synthetic-only Phase 11D.1 usage
probe. A real downstream target remains blocked until a separate owner contract
names the repository authority, safe target alias, access class, exact commands,
data boundary, and every permitted side effect.
