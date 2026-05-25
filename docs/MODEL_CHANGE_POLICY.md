# Model Change Policy

## Purpose

Define planning-level controls for model and prompt changes in
codex-dev-harness.

This policy is documentation-only. It does not implement model comparison code,
capture prompts or outputs, call external services, add dependencies, install
CI workflows, or change application/device/live-write behavior.

## Tracked Fields

Future model or prompt change evidence should track:

- `model_id`
- `prompt_template_id`
- `eval_run_id`
- `approved_corpus_digest`
- `side_effect_class`

These fields may appear in future audit, closeout, release, or evaluation
evidence. They should be identifiers, hashes, or summaries, not raw prompts,
private input, raw source, model output, or tool-call bodies.

## Model ID Tracking

`model_id` should identify the model used for a task or comparison at the level
needed for reproducibility.

Model IDs should be recorded when:

- changing the default model used for a workflow
- comparing model behavior for repository tasks
- producing release or audit evidence that depends on model behavior
- closing out approval-gated AI-assisted work

If a precise model identifier is unavailable, record `UNKNOWN` rather than
guessing.

## Prompt Template Tracking

`prompt_template_id` should reference a reusable prompt template or task
contract when one is used.

Examples include prompt templates under `prompts/task_contract/`. The identifier
must not include raw prompt text unless a separate task explicitly approves
prompt capture and redaction.

Prompt template changes should be reviewed like policy changes when they affect
side-effect boundaries, verification expectations, approval language, or
release closeout behavior.

## Eval Run Tracking

`eval_run_id` should identify the eval evidence used to compare or accept a
model or prompt change.

The current eval harness is minimal and standalone. Once an eval harness exists
for the affected behavior, a model or prompt change should not be adopted
without eval evidence and a closeout record. If no applicable eval exists,
record `NOT RUN` with a reason and identify the residual risk.

## Approved Corpus Digest Tracking

`approved_corpus_digest` should identify the exact approved corpus basis used
by any future retrieval-assisted workflow.

The digest should represent approved, safe corpus material only. It must not be
computed from private raw source, live configuration, secrets, prompt/session
transcripts, model outputs, or downstream generated target output.

## Side-Effect Class Tracking

`side_effect_class` should classify what the model or prompt change is allowed
to influence.

Suggested classes:

- `read_only_review`
- `documentation_edit`
- `local_generation`
- `release_evidence`
- `approval_required_side_effect`
- `forbidden_live_target`

A model or prompt change must not broaden side-effect permissions. Human
approval remains required for actions governed by `docs/HUMAN_APPROVALS.md`.

## Compare-Before-Adopt Principle

Model and prompt changes should be compared before adoption. A comparison should
include:

- baseline model or prompt identifier
- candidate model or prompt identifier
- affected workflow or task class
- eval result or `NOT RUN` explanation
- safety boundary review
- scope creep review
- verification closeout
- recommendation to adopt, defer, or reject

The comparison should prefer summaries, identifiers, hashes, and evidence paths
over raw prompt or output capture.

## Adoption Rule

Do not adopt a model or prompt change for a governed workflow without:

- an explicit task approval or documented decision
- model and prompt identifiers where applicable
- eval evidence once an applicable eval harness exists
- closeout evidence
- unresolved risk notes
- confirmation that side-effect boundaries did not expand

For high-risk work, defer adoption if evidence is missing.

## Relationship To Audit Evidence

Future audit evidence may reference `model_id`, `prompt_template_id`,
`eval_run_id`, `approved_corpus_digest`, and `side_effect_class`.

Those fields are evidence aids only. Recording them does not approve prompt
capture, model output capture, external service calls, RAG tooling, or live
side effects.

## Non-Goals

This policy does not add:

- model comparison code
- model evaluation services
- prompt/session capture
- model output capture
- RAG indexing
- embeddings
- external-service calls
- CI workflows
- application/device/live-write code
