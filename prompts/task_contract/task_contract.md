# Task Contract Prompt

Use for AI/Codex implementation, documentation, review, or verification.

This documentation template executes nothing and cannot override repo policy or approval.

## Goal

[Describe the concrete outcome required.]

Define observable completion; keep Codex and package IDs distinct. For feature/
artifact checks, map the goal to actual inputs/options/path. Derive expectations
from requirements, templates or contracts; never adjust them just to pass output.

## Target Repo / Path

- Repository: [repo name or URL]
- Local path: [absolute or repo-relative path]
- Package root: [same as repository / separate local control-plane root]
- Basis ref or commit, if relevant: [branch, tag, or commit]

## Work Package

- Task ID: [safe task identifier]
- Schema version: [3]
- Lane: [contract / feature / integration]
- Base SHA: [40-character commit SHA]
- Contract basis SHA: [same 40-character commit SHA]
- Contract frozen paths: [shared exact repo-relative interface paths]
- Dependencies: [task IDs, or none]
- Read set: [exact repo-relative paths]
- Write set: [exact repo-relative paths]
- Generated outputs: [exact repo-relative paths, or none]
- Verification tier: [V0 / V1 / V2 / V3]
- Verification runtime ID: [safe runtime identity, for example python-3.12.13-pytest-9.0.3]
- Verification command IDs and exact argv: [command ID plus argument-list tokens]
- Declared side effects: [classes requested by this task]
- Approval reference: [safe reference, or none]

Routing: script for deterministic checks, Terra Medium for narrow edits,
Sol Medium for settled implementation, Astra Medium/High for boundaries.
This adopts no roles and proves no provider equivalence. Keep one owner unless independent.
Before async/delegated start, choose an existing-format result location. Retain
execution ID/state, internal exit and core result/evidence; recover empty bodies by
receipt. Candidate/refs precede review. Collisions get a new attempt; retain receipts.

For parallel work, save the machine-readable package under the ignored
`local/work-packages/` directory and run:

```text
python scripts/work_package_conflict_check.py --repo-root . --package <PACKAGE_JSON> [--package <PACKAGE_JSON> ...] --json
```

For an approved external control-plane package, keep each package name relative
to that root and run:

```text
python scripts/work_package_conflict_check.py --repo-root <TARGET_ROOT> --package-root <CONTROL_PLANE_ROOT> --package <PACKAGE_ROOT_RELATIVE_JSON> --json
```

Packages describe scope, not approval; structural PASS keeps
`authorization_status=NOT_AUTHENTICATED`.

Record `plan_digest`. After one coherent lane commit and focused verification, run:

```text
python scripts/work_package_postflight.py --repo-root . --package <PACKAGE_JSON> [--package <PACKAGE_JSON> ...] --task-id <TASK_ID> --verification-status PASS --verification-interpreter-id <INTERPRETER_ID> --completed-command-id <COMMAND_ID> --json
```

Postflight uses identical `--package-root` and package-relative name. No absolute
repo/package-root paths in packages or JSON evidence. Process exit, reason codes
and command IDs are the verification interface; stderr is diagnostic.

Integration requires matching pre/postflight `plan_digest`, postflight `PASS`,
unchanged frozen contract and separate owner/side-effect approvals. A feature
change to frozen paths stops with `CONTRACT_CHANGE_REQUIRED` for a new basis.
No `PASS` for an omitted command, different runtime or owner-only rerun.

## Write Scope

Choose one:

- Read-only. Do not edit files.
- Documentation-only writes.
- Code/test writes within the allowed files below.
- Other: [describe and require explicit approval]

## Allowed Files

- [file or directory]
- [file or directory]

## Forbidden Files / Actions

- Edit only allowed files.
- No unrelated refactors.
- No delete/move/overwrite/force-write without separate approval.
- CI workflow changes need separate approval.
- Release artifacts need separate approval.
- Do not add eval, audit logging, RAG, application, device, or live-write behavior unless separately approved.
- Do not include secrets, private raw input, sensitive source text, equipment details, live parameters, or credentials.
- Feature and contract lanes must not edit integration-only authority,
  workflow, gate, golden, corpus-source-set, or artifact paths.

## Verification Commands

Run when safe and available:

- [V0 work-package and scope checks]
- [V1 focused tests, or V2/V3 integration checks]
- [command]
- [command]

If a command is not run, report `NOT RUN` or `ENVIRONMENT BLOCKED` with the reason.

Keep required reading and verification. Representatives are only for uncertain
environment, call path or reproduction. For validator/error-test changes, check
known valid acceptance and defect rejection; trace production errors through the
final result. Setters/messages alone are no flow PASS; state mock/actual scope.
Bind execution ID/state, internal exit, core result. Recover before rerun:
missing output is no rerun reason, nor shell success internal PASS. Unconfirmed
execution is `result not verified / NOT DONE`, not `NOT RUN`, `ENVIRONMENT
BLOCKED`, or a new JSON enum. Control only an exactly owned run; shared env proves no
ownership. Two evidence-based same-cause failures trigger diagnosis with
questions, evidence, hypothesis; missing input/authority is no reasoning gap.

## Side-Effect Approval Boundary

The following actions require separate explicit human approval before execution:

- external sends, messages, notifications, or publication
- deletion, move, overwrite, force, or broad filesystem changes
- dependency installation or environment mutation outside the requested scope
- tag creation, tag movement, release publication, manifest/checksum/SBOM/provenance generation
- workflow installation or external service changes
- database mutation, live target mutation, PLC/device write, start, stop, reset, or mode change

## Completion Report Format

1. Files changed
2. Behavior or document summary
3. Verification result
4. Safety checks
5. Unresolved risks or assumptions
6. Recommended next step
