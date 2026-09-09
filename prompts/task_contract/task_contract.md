# Task Contract Prompt

Use this prompt when requesting AI/Codex implementation, documentation, review, or verification work.

This template is documentation-only. It does not grant approval for side effects, execute automation, or override repository policy.

## Goal

[Describe the concrete outcome required.]

Define observable completion. When relevant, note decision-critical uncertainty,
reusable evidence, and Codex task ID/state; keep package `task_id` distinct.

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

Routing aid: deterministic check to script; narrow research/edit
to Terra Medium; settled implementation to Sol Medium; boundary judgment to
Astra Medium to High. This neither adopts roles nor proves provider behavior
or equivalence. Keep one owner unless independent; inspect
needed output, preserve evidence, and stop at completion. Cleanup is separate.

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

The package describes scope and conflicts. It does not grant approval.
`authorization_status=NOT_AUTHENTICATED` remains fixed even when structural
validation passes.

Record the returned `plan_digest`. After the lane has one coherent commit and
its focused verification is complete, run:

```text
python scripts/work_package_postflight.py --repo-root . --package <PACKAGE_JSON> [--package <PACKAGE_JSON> ...] --task-id <TASK_ID> --verification-status PASS --verification-interpreter-id <INTERPRETER_ID> --completed-command-id <COMMAND_ID> --json
```

Use the identical `--package-root` and package-relative name at postflight.
Never copy repository or package-root absolute paths into the package or JSON
evidence. Treat process exit status, reason codes, and command IDs as the
verification interface; stderr wording is diagnostic only.

Do not integrate the lane unless preflight and postflight use the same
`plan_digest`, postflight reports `PASS`, the frozen contract is unchanged, and
the required owner/side-effect approvals exist outside the package. Stop with
`CONTRACT_CHANGE_REQUIRED` and create a new contract basis when a feature lane
needs to change a frozen path. Do not report `PASS` when the agent omitted a
required command, selected a different runtime, or only the owner reran the
command afterward.

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

- Do not edit files outside the allowed list.
- Do not perform unrelated refactors.
- Do not delete, move, overwrite, or force-write files unless separately approved.
- Do not create or modify CI workflows unless separately approved.
- Do not generate release artifacts unless separately approved.
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

Keep required reading and verification. Use a representative only when
environment, call path, or reproduction is uncertain. Evidence links execution
ID/state, internal exit, and core result. Recover it before rerun; missing output
alone is no rerun reason, and shell success is no internal PASS. An unconfirmed
executed result is human `result not verified / NOT DONE`, not `NOT RUN`,
`ENVIRONMENT BLOCKED`, or a new JSON enum. Control only an exactly owned
execution; a shared virtual-environment path proves no ownership. Two
evidence-based changes failing for the same cause trigger diagnosis with
questions, evidence, and hypothesis. Missing input or authority is not a
reasoning problem.

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
