# Downstream Task Contract Validator Candidate Contract

## Purpose

Record the Phase 11C contract for the first standalone downstream task-contract
validator candidate.

Phase 11C is documentation and focused synthetic-test only. It selects a future
read-only validator for the Phase 11B contract format and fixes the approval,
input, path, validation, output, and failure boundaries before implementation.
It does not implement or run a validator, create a filled contract, select or
access a downstream repository, or authorize any downstream action.

## Allowed Files

Phase 11C is limited to:

- `docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_CANDIDATE_CONTRACT.md`
- `tests/test_downstream_task_contract_validator_candidate_contract.py`

`STATUS.md`, `ACCEPTANCE_TRACE.md`,
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, the Phase 11B fixture, scripts,
schemas, gates, workflows, artifacts, audits, evals, templates, profiles,
examples, dependencies, release evidence, and downstream repositories are
intentionally excluded.

## Basis

This contract depends on:

- `AGENTS.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `docs/SAFETY_POLICY.md`
- `docs/AI_HANDOFF.md`
- `docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md`
- `docs/DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json`
- `tests/test_downstream_product_integration_boundary.py`
- `tests/test_downstream_task_contract_synthetic_fixture.py`

The digest-valid Phase 11 checkpoint is commit
`c4374781c71229b0134d28ab4235c36998c1d870`. Its clean Local Verify is run
`29179099000`, job `86613472333`, with 481 tests, nine quality gates, all three
profile render dry-runs, read-only contents permission, and no uploaded
artifacts.

Release evidence refresh remains `HOLD`. The checkpoint and existing harness
capabilities do not grant authority over another repository.

## Candidate Decision

Decision:
`standalone_downstream_task_contract_validator_candidate_selected_without_implementation`.

The selected candidate validates either the existing synthetic fixture or a
future filled contract as bounded JSON data. Validation is local and read-only.
It does not verify external approval evidence, inspect target-repository rules,
open a downstream worktree, execute declared commands, or grant permission for
any side effect.

Phase 11C does not authorize implementation or execution. A later Phase 11D
task must separately approve exact implementation files, code, tests, commands,
and verification.

## Selected Candidate

Candidate id: `standalone_downstream_task_contract_validator`.

Future candidate purpose:

- validate the exact Phase 11B contract structure and bounded field types;
- distinguish `synthetic` and `filled` contract intent explicitly;
- validate declared access, approval, command, and side-effect relationships;
- reject unsafe paths, URLs, raw/private/live values, and unbounded content;
- emit only a bounded deterministic validation summary;
- keep downstream access, network use, command execution, writes, and every
  remote or live side effect at `NOT RUN`.

The candidate is standard-library-only, local-only, read-only, and dry-run-only.
It is not a schema generator, command parser, command executor, approval
verifier, repository scanner, or policy-enforcement runtime.

## Future Implementation Contract

A separately approved Phase 11D task may propose only:

- `docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md`
- `scripts/downstream_task_contract_validator.py`
- `tests/test_downstream_task_contract_validator.py`

The future command contract is:

```text
python scripts/downstream_task_contract_validator.py --contract <JSON_PATH> --contract-kind synthetic|filled --dry-run [--json]
```

`--contract` and `--contract-kind` are required. `--dry-run` is required to run
validation. Omitting it returns `NOT RUN`. There is no write mode, stdin mode,
output-path option, repository-access option, network option, or execution
option.

This command is a contract placeholder only. Phase 11C does not create the
implementation plan, script, or runtime tests and does not run the command.

## Input And Path Contract

The future validator may read exactly one explicitly supplied JSON file:

- a repo-relative path that resolves inside the harness repository; or
- an absolute path that resolves inside the operating-system temporary root.

The input must be a regular `.json` file, UTF-8, and no larger than 64 KiB.
Directories, missing suffixes, symlinks, junctions, other reparse points, URLs,
parent traversal, repo-relative paths that escape the harness, absolute paths
outside the temporary root, and files larger than the limit are rejected.

The absolute temporary input path is control data only. It must never appear in
stdout, JSON output, errors, logs, evidence references, or tracked files. The
validator must not enumerate the input directory or read sibling files.

Payload values must not contain a URL, IP-like value, local absolute path,
backslash path, parent traversal, credential, token, secret-like value, raw
source, full diff, patch, prompt, approval text, transcript, stdout, stderr,
command log, tool-call body, private data, live configuration, endpoint, port,
device value, or downstream raw evidence. Repo-relative references use `/`, do
not begin with `/`, and contain no empty, `.` or `..` segment.

The entire input is bounded to 64 KiB. Each string is bounded to 512 UTF-8
bytes, `commands` is bounded to 32 entries, each scope path list is bounded to
64 entries, and `reason_codes` is bounded to 16 entries.

## Synthetic Contract Validation

`--contract-kind synthetic` requires:

- the exact Phase 11B top-level and nested key sets with no unknown keys;
- `schema_version="1"`;
- `fixture_id="phase_11b_synthetic_downstream_task_contract"`;
- the fixed Phase 11A human-contract reference;
- `synthetic=true`, `status="NOT RUN"`, and `performed_actions=[]`;
- every required Phase 11B placeholder;
- the exact 16 side-effect classes in the fixed order;
- owner, target, and target-rules approval flags set to `false`;
- every permission set to `authorized=false`, `approval_ref=null`, and
  `status="NOT RUN"`.

A valid synthetic contract returns `PASS WITH NOTES` with reason code
`SYNTHETIC_CONTRACT_VALID`. It remains non-runnable and grants no authority.

## Filled Contract Validation

`--contract-kind filled` requires the same Phase 11B key structure without
adding a schema or unknown field. It also requires:

- `schema_version="1"` and `synthetic=false`;
- a bounded safe `fixture_id` used as the filled contract instance id;
- no placeholder token anywhere in the payload;
- owner approval, target-repository approval, and target-rules review set to
  `true`;
- a bounded non-placeholder approval reference;
- a generalized safe repository identifier rather than a URL or private raw
  identifier;
- bounded branch, commit, upstream, scope, rollback, cleanup, verification,
  risk, and safe-evidence values;
- at least one command with declared effect classes;
- `status="NOT RUN"`, `performed_actions=[]`, no changed files, no commands
  reported as run, and no completed side effect.

A valid filled contract returns `PASS`. This means only that the selected JSON
fields are structurally and internally consistent. It does not authenticate an
approval reference, verify repository identity or instructions, or authorize
repository access, command execution, network use, writes, or downstream work.

## Permission And Command Contract

The exact side-effect classes remain:

- `repository_access`
- `network_read`
- `local_write`
- `execute`
- `stage`
- `commit`
- `push`
- `pull_request`
- `merge`
- `workflow_dispatch`
- `artifact_upload`
- `tag`
- `release`
- `publish`
- `deploy`
- `live_action`

Every class must appear exactly once. An authorized class requires
`authorized=true`, a bounded non-placeholder `approval_ref`, and
`status="NOT RUN"`. An unauthorized class requires `authorized=false`,
`approval_ref=null`, and `status="NOT RUN"`.

For a filled contract, `repository_access` must be authorized. The declared
access class is a permission ceiling:

- `local_read_only` permits only `repository_access` and optional `execute`;
- `remote_read_only` permits only `repository_access`, `network_read`, and
  optional `execute`;
- `local_write` permits only `repository_access`, `local_write`, `execute`,
  `stage`, and `commit`;
- `remote_write` may declare any of the 16 classes, but each remains separately
  approval-gated.

Every command effect class must name one of the 16 classes and must correspond
to an authorized permission. A command with an unauthorized, unknown, empty,
or duplicate effect class is blocked. The validator treats command strings as
opaque bounded data. It does not parse shell syntax, infer effects from command
text, invoke a shell, or execute a command. It does not claim that declared
effects are complete.

## Output Contract

Default stdout is a one-line bounded summary. `--json` emits one deterministic
JSON object with sorted keys and one final newline. The encoded output must not
exceed 8 KiB.

Future JSON output has exactly these top-level fields:

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

`performed_actions` is always `[]`. `external_state` records downstream
repository access, network read, command execution, and downstream write as
`NOT RUN`. Output reports only safe categories, fixed reason codes, counts, and
side-effect class names. It must not include input paths, payload values,
repository identifiers, commands, approval references, branches, commits,
scope values, raw JSON, excerpts, matched sensitive values, or shell output.

There is no output file, tracked evidence, artifact, receipt, trace, audit log,
temporary output, cache, or cleanup action.

## Status And Exit Codes

Status precedence is:

1. `NOT RUN` when `--dry-run` is absent;
2. `ENVIRONMENT BLOCKED` for filesystem permission or runtime inspection
   failures;
3. `FAIL` for malformed JSON, invalid UTF-8, size, key, type, path, kind, output,
   or data-safety violations;
4. `BLOCKED` for a missing input, unresolved filled placeholder, missing
   approval, command-permission conflict, or access-class permission conflict;
5. `PASS WITH NOTES` for a valid synthetic contract;
6. `PASS` for a valid filled contract's internal validation only.

Exit code `0` means `PASS` or `PASS WITH NOTES`. Exit code `1` means `BLOCKED`,
`FAIL`, or `ENVIRONMENT BLOCKED`. Exit code `2` means `NOT RUN` or CLI usage
error.

The `PASS` family never means that external approval evidence was authenticated
or that a downstream action is authorized.

## Failure Modes

Future implementation must fail closed for:

- missing, unreadable, malformed, invalid-UTF-8, or oversized input;
- contract-kind and `synthetic` flag mismatch;
- missing, extra, duplicate, or incorrectly typed fields;
- placeholder drift or unknown side-effect classes;
- unsafe URL, path, IP-like, secret-like, private, raw, or live value;
- missing approval or target-rules review;
- access-class and permission-ceiling conflict;
- command effect without matching authorization;
- non-empty `performed_actions` or pre-completed action status;
- output overflow or attempted raw-value disclosure;
- attempted file write, persistence, command execution, network call,
  downstream access, or external approval lookup.

No failure may echo the rejected value or be reported as silent success.

## Verification

Phase 11C verification must include:

- `python -m pytest tests/test_downstream_task_contract_validator_candidate_contract.py`
- `python -m pytest tests/test_downstream_task_contract_synthetic_fixture.py`
- `python -m pytest tests/test_downstream_product_integration_boundary.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `python scripts/generate_checksums.py --verify`
- `python scripts/generate_corpus_digest.py --check --json`
- `git diff --check`
- `git ls-files --others --exclude-standard`

The expected current counts are six Phase 11C focused tests, six Phase 11B
focused tests, five Phase 11A focused tests, 487 full-suite tests, nine quality
gates, five matching release checksums, and 34 valid corpus sources with no
stale source.

Release evidence, eval report, and corpus digest hashes must remain unchanged.
`python scripts/run_eval.py` is `NOT RUN` because Phase 11C does not change eval
behavior and must not mutate eval evidence.

## Non-goals

Phase 11C does not:

- create `docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md`;
- implement `scripts/downstream_task_contract_validator.py`;
- create `tests/test_downstream_task_contract_validator.py`;
- modify the Phase 11B fixture or create a filled contract;
- create a JSON Schema or change an existing schema;
- add a gate, quality-gate integration, workflow, dependency, or runtime;
- update `STATUS.md`, the capability roadmap, `ACCEPTANCE_TRACE.md`, or the
  exact 34-source corpus digest;
- generate an artifact, receipt, trace, audit log, eval report, or release
  evidence;
- locate, inspect, clone, fetch, render into, write, test, build, execute in,
  commit in, or push to a downstream repository;
- open a pull request, merge, dispatch a workflow, upload an artifact, tag,
  release, publish, deploy, or perform a live action;
- execute MCP or Hermes, add AgentOps or memory behavior, or access an external
  service.

## Next Step

After the Phase 11C contract commit is separately approved, pushed, and passes
clean Local Verify, the next candidate is a separately approved Phase 11D task
limited to the exact future implementation files and CLI named above.

Phase 11D must implement and test the standalone validator before any filled
contract usage probe. Neither Phase 11C nor its Local Verify authorizes a filled
contract, real downstream access, command execution, persistence, or any
downstream side effect.
