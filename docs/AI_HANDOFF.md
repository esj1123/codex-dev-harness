# AI_HANDOFF.md

## Purpose

Provide a compact handoff index without duplicating current authority.

## Authority

Read `docs/AUTHORITY_MANIFEST.json` for the machine-readable current state,
default Read Order, conditional read groups, document classifications, and the
sole normative owner of each protocol namespace.
Read `STATUS.md` for the current human summary, held items, and next
recommended action. Those two files are authoritative when older phase or run
records differ.

`ACCEPTANCE_TRACE.md` and phase-specific closeouts are historical evidence, not
default operating context.

## Work Guidance

Optional engineering authoring, diagram and review skills are indexed in
`docs/PROMPT_PATTERNS.md#optional-workflow-skills`. Their repository sources are
shared by personal Codex and Claude installations; project rules and formats
remain target-owned.

Start target work from `README.md` and the short workflows in
`docs/PROMPT_PATTERNS.md`. Detailed package and execution fields apply only when
selected or required. The tools below support their declared scopes; they are
not a checklist for every explanation or document. Target policies and inherited
global instructions remain applicable. Agent Quality is frozen/not adopted;
Hermes/MCP is held and Local RAG remains advisory/frozen, as recorded in `STATUS.md`.

## Control Surface

- Work-package planning and collision checks:
  `scripts/work_package_conflict_check.py`
- Actual-diff postflight:
  `scripts/work_package_postflight.py`
- Optional bounded state/evidence closeout:
  `scripts/task_evidence_summary.py`; target-owned exact selectors and bindings
  supply meaning. See `docs/LOCAL_USAGE.md#bounded-closeout-state-and-usage`.
- Verification impact planning:
  `scripts/verification_plan.py`
- Agent Quality validation and aggregation:
  `scripts/agent_quality.py`
- Core-only quality gate:
  `scripts/quality_gate.py`
- Current `LOCAL_INTEGRATION (V2)` verification:
  `scripts/run_local_verify.ps1`
- Manual `HOSTED_EXACT_SHA (V3)` verification:
  `.github/workflows/local-verify.yml`
- Selected manual release-evidence export contract:
  `manual_github_release_evidence_export` (implementation state in `STATUS.md`)

Ignored package, trial, and checkpoint envelopes under `local/` remain local
control-plane evidence. They do not authenticate approval and must not contain
raw prompts, transcripts, private payloads, secrets, absolute paths, or command
logs.

## State And Evidence Navigation

Read `STATUS.md` for Agent Quality/provider availability, held items, and the
next authorized sequencing decision. Core readiness and structural evidence
do not imply provider execution, trial, calibration, baseline, or adoption.

Read [Historical Local Checkpoints](../ACCEPTANCE_TRACE.md#historical-local-checkpoints)
for source-bound local closeouts, recovery results, and earlier HOLDs.
Historical observations do not update current refs or grant successor action.

## Required Boundaries

- Structural PASS does not grant execution or side-effect permission.
- A frozen contract change stops with `CONTRACT_CHANGE_REQUIRED`.
- Agent-quality baseline creation remains separately approval-gated.
- Read `STATUS.md` for the tracked release bundle's current state. Keep the
  source-basis commit, artifact-containing commit, local Git state, transient
  transport context, and publication authority distinct.
- The selected manual GitHub export capability does not authorize automatic
  triggers, durable distribution, tag, signing, publication, deployment,
  `origin/main` mutation, or downstream access.
- Push, workflow dispatch, release, upload, downstream access, MCP/Hermes
  execution, and live/private data use require separate authority.
- Tracked authority does not store workflow run IDs.

## Task Handoff

The current three-role expansion is recorded in
`local/checkpoints/engineering-workflows-20261005/closeout.json`. Read the exact
candidate, preservation checks, independent review, synthetic cases, required
verification and each personal installation/loading result before claiming
completion. Conditional references cover broad document families, design
derivation, review perspectives and electrical/I/O and CAD examples; real project
technical criteria remain target-owned. Review-only stays read-only, and the
review role remains usable without optional sibling references.

The preceding two-skill implementation and loading observations remain historical
at `local/checkpoints/workflow-skills-20261005/closeout.json`; they do not verify
this expanded candidate. Installed files are distributions, not proof of native
document behavior, automatic selection for all requests or adoption by existing
sessions. No global AGENTS/CLAUDE settings, downstream documents/pins, executable
interfaces or release artifacts are changed by this expansion.

The prior workflow-guidance and base-template closeout remains historical at
`local/checkpoints/task-workflows-20261005/closeout.json`; its source changes and
earlier acceptance-scope edits are preserved. Education/knowledge and legacy
analysis are designed catalog entries only. Inherited model-recording and
reporting rules remain applicable. Target utility remains NOT_MEASURED.

### Historical Reader Integration And Target Probe

The completed historical local closeout integration's reviewed candidate, cumulative
main-base scope, source integration and repair commits, digest-only commit,
exact final SHA, independent
review, new V2/Full results and package postflights are linked in
`local/checkpoints/evidence-closeout-main-20261001/closeout.json`.
The same 34 digest sources retain a clean committed source basis; membership
is unchanged. Read the receipt's result before claiming local verification.

Launchpad adoption is target-owned. Preserve its existing pinned checkout,
whose exact identity is in that receipt, until the target owner authorizes
an exact successor pin/caller change and revalidates the target's current
acceptance inputs. The saved state probe retained 11 completed, zero pending
and one UNKNOWN gate, with `TARGET_OWNER_RESOLVE_UNKNOWN_GATES` as its next
action at that checkpoint. `v5_option_restoration` was UNKNOWN in that saved
probe; it is not a current target verdict. Reconcile the target owner's latest
scoped decisions before repeating a question or execution. This record grants
no new target execution or blanket reversal of earlier document acceptance. Office, protected
inputs, remote, Hosted and release remain outside this local handoff.
Usage evaluation was not selected; token savings is NOT_MEASURED.

Use the manifest's `handoff` conditional group for this file. Before continuing,
re-read `STATUS.md`, run the verification plan for the intended diff, and
report commands not executed as `NOT RUN`.
