# AGENTS.md

## Purpose

This file defines the operating rules for AI/Codex work in this repository.

## Read Order

1. AGENTS.md
2. docs/AUTHORITY_MANIFEST.json
3. STATUS.md
4. docs/SAFETY_POLICY.md

Conditional read groups are defined only in
`docs/AUTHORITY_MANIFEST.json`. Load product scope for initial product
orientation or decisions about goals, scope, acceptance, capability selection,
or adoption. Load verification, capability selection, and handoff context
when the task requires them. Conditional reading does not remove required
checks; expand to original evidence for gaps, contradictions, stale candidates,
or new failures.

## Current Phase Rule

Do not hardcode the current repository state in this operating file. Read
`docs/AUTHORITY_MANIFEST.json` for the machine-readable state and `STATUS.md`
for its current human summary.

`docs/AUTHORITY_MANIFEST.json` separates current authority, durable policy, and
historical evidence. `STATUS.md` is the current implementation sequencing
source of truth; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` is consulted only
when selecting a capability. The manifest also declares bounded operational
inputs and the sole owner document for each protocol namespace without making
operational inputs current authority. A
feature lane that needs to change
`contract_frozen_paths` must stop with `CONTRACT_CHANGE_REQUIRED` and return to
the integration owner.

Allowed:
- Edit documentation, markdown templates, profiles, examples, tests, and quality gate scripts within the requested scope.
- Keep render behavior dry-run first for examples.
- Preserve the safety boundary around private data and live targets.
- Use separately approved disjoint feature lanes under the work-package schema v3 contract.

Not allowed by default:
- Add real application code.
- Add PLC/device connection code.
- Add live device write, start, stop, reset, or mode-change behavior.
- Add secrets, private inputs, customer data, equipment details, credentials, keys, or tokens.
- Broaden render targets to arbitrary repo-internal directories outside `examples/<name>`.

## Task Contract

Before editing, identify:
- Goal.
- Scope.
- Files expected to change.
- Files and areas that must not be touched.
- Verification expected for the task.

## Harness Utility Measurement

Improve the actual target outcome by reducing repeated inspection, rework,
errors, and avoidable user intervention. Usage accounting is an optional way
to evaluate an improvement, not a mandatory Harness feature, default output,
task prerequisite, or completion gate. Do not create work solely to collect
usage or make existing state/evidence checks depend on runtime logs.

When an improvement evaluation is requested, select only the measures needed
for that question before work starts. Name the
target outcome, candidate identity or its selection point, comparison basis,
one measurement owner, the existing evidence record, covered participants and
phases, and the milestones at which observations will be recorded. Use the
measurement rules in
`prompts/task_contract/task_contract.md` and
`prompts/task_contract/verification_closeout.md`; do not add fields to the
work-package schema or create a task solely for measurement.

Where selected for evaluation, distinguish four results: whether the target task reached its required
outcome with the required quality and authority; elapsed work, retries, rework,
and user interventions; total input, cached-input, and output tokens and calls
across coordination, implementation, review, repair, and handoff; and the
benefit relative to the Harness preparation and verification effort. Identify
the original usage source, unique event keys, cutoff, missing coverage, and a
comparable prior or alternative workflow before claiming an improvement. Treat
cached input as part of input, not an additional total. Compare total effort and
tokens per accepted outcome where a comparable outcome exists, retaining failed
attempts in the total. If comparison or usage evidence is unavailable, report
`NOT_MEASURED` rather than a saving. A
structural verification PASS alone does not establish utility or effectiveness.

Select further diagnostic measures only when they fit the evaluation, and state each measure's
denominator and evidence source in the request: first-pass acceptance and
defects found or missed; incorrect PASS/FAIL and safety or authority boundary
failures; exact-candidate evidence completeness, reproducibility, and drift
detection; preparation, verification, and review overhead; time to first useful
result and to diagnosis or recovery; model-routing mismatches and avoidable
human decisions; and actual cost when available. Do not collapse these into a
single score or trade quality and safety for fewer tokens. Unknown ground truth
is `UNKNOWN`, not evidence of zero errors.

## No-Touch Zones

Do not add or expose:
- Secrets or credentials.
- Private raw input.
- Sensitive business source text.
- Device addresses, equipment parameters, or live-control values.
- Generated application code outside an explicitly approved future phase.

## Side-Effect Policy

Default to read-only inspection first. File writes are allowed only for requested repository work. Delete, move, external send, database write, live target mutation, and device action require explicit confirmation.

## Verification Plan

For the current template repository, verify:
- README and AGENTS read order match.
- Required root documents exist.
- Base templates and profile templates are present.
- Render script supports dry-run example rendering.
- Quality gate includes docs, repo hygiene, template schema, secret scan, and example validation.
- No real application code or sensitive information was added.

## Handoff Rules

When work ends, report:
- Files changed.
- Commands or GitHub actions used.
- Verification result.
- Safety checks.
- Risks and assumptions.
- Next recommended step.

## Closeout Receipt

Every completed task should include outcome, changed files, verification result, safety checks, unresolved risks, and next step.
