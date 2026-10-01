# Task Contract Prompt

Use for AI/Codex implementation, documentation, review, or verification.

This documentation template executes nothing and cannot override repo policy or approval.

## Goal

[Describe the concrete outcome required.]

Define observable completion; keep Codex and package IDs distinct. For feature/
artifact checks, map the goal to actual inputs/options/path. Derive expectations
from requirements, templates or contracts; never adjust them just to pass output.

Lead dispatch with the goal, current candidate, write/no-touch scope, required
reading, reusable evidence, unresolved issues and next action. Link long
background to exact existing records; retain the required package fields below.

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

## Dispatch Metadata

These Markdown fields are task coordination metadata, not work-package schema v3:

When this task selects closeout mechanization, also record the exact
package-root-relative evidence spec, physical target input root and optional
runtime root at actual start. Use an empty `runtime` list and omit the runtime
root unless usage evaluation is requested. Accounting is not a prerequisite
for state/evidence inspection, task execution or completion. The target owner supplies selectors, state
mappings, candidate SHA and receipt links. See
[Bounded closeout state and usage](../../docs/LOCAL_USAGE.md#bounded-closeout-state-and-usage).
Pass these declared inputs to the existing postflight invocation at each
selected closeout/handoff milestone; its optional in-process hook performs
the projection and counter aggregation. Do not discover logs or infer gates.

- Role: [coordination / retrieval / implementation / verification / review / integration]
- Requested model: [exact model name]
- Requested reasoning effort: [exact effort]
- Task-fit reason: [one line]
- Actual model/effort and evidence: [original runtime evidence, or unverified]
- Routing mismatch disposition: [none / correction and next safe boundary / unresolved]

Apply the global `AGENTS.md` model-routing policy. Preserve an agreed choice when
the same role and scope resume, even when a later message omits the model name.
Keep primary-task configuration separate from explicit delegation arguments.
Record original runtime evidence once at start, resumption or settings change;
self-report is not evidence. Correct a mismatch before expanding work while
preserving useful output and tests; do not rerun solely to relabel. Remedy
permission or environment blocks directly. Dispatch settings grant no authority.

Keep one responsible owner for each write scope. Delegate independent outputs
or independent review when needed, using the smallest relevant context.
Before async/delegated start, choose an existing-format result location. Retain
execution ID/state, internal exit and core result/evidence; recover empty bodies by
receipt. Candidate/refs precede review. Collisions get a new attempt; retain receipts.

When measurement is requested for this work scope, including resumed or delegated
phases, name one measurement owner and the existing record before work starts.
Select measures for the actual improvement question; usage accounting is optional,
not a mandatory Harness feature, default output or completion gate.
Update it at actual start, verification, independent review, rework and closeout
transitions, covering coordination and handoff as well. Do not create stages solely
to measure them. Use `verification_closeout.md` for source, deduplication, cutoff
and coverage rules.

After required reading, inspect the current entrypoints and changed areas first.
Select tool output before returning it: inspected scope, verdict, mismatches or
failures, and evidence locations. Retain necessary originals; expand relevant
source reads for contradictions, missing evidence, stale candidates or new failures.
Reuse a completed verification only for its recorded candidate/input identities,
command and runtime basis, acceptance scope and original result. Confirm that
these dependencies still match before reuse. A changed dependency, incomplete
scope or new finding requires the affected checks; a new cumulative integration
candidate still needs the checks selected by the verification policy. A hash
match or summary alone cannot replace required native or independent review.
When the selected commands are the two standalone Harness checkers, apply the
sole caller example in [Standalone checker JSON results](../../docs/LOCAL_USAGE.md#standalone-checker-json-results)
and start with the candidate, actual and reported exits, checked JSON decision
and raw stdout/stderr evidence references. The task and impact policy still
select the required verification tier and independent review.

For parallel work, save packages under ignored `local/work-packages/` and run:

```text
python scripts/work_package_conflict_check.py --repo-root . --package <PACKAGE_JSON> [--package <PACKAGE_JSON> ...] --json
```

For approved external packages, use a name relative to the control-plane root:

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
and command IDs are the verification interface; stderr wording is diagnostic only.

For the selected mechanized path, append `--task-evidence-spec <SPEC_JSON>`
and `--task-evidence-input-root <TARGET_ROOT>`, plus
`--task-evidence-runtime-root <RUNTIME_ROOT>` when the spec names runtime
sources. Spec location follows the same package root. This is a fixed reader,
not execution of commands from a package. A valid pending target remains
pending even when structural postflight passes; an invalid projection blocks
an otherwise passing postflight. Store only the selected safe JSON in the
existing task-owned evidence record when that write is approved.

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
- Eval, audit logging, RAG, application, device or live-write additions need separate approval.
- No secrets, private raw input, sensitive source text, equipment details, live parameters or credentials.
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
