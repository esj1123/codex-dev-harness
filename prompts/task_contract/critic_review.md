# Critic Review Prompt

Use this prompt when requesting a review-only pass over a task, diff, design, or repository state.

This template is documentation-only. It does not authorize edits, side effects, or implementation work.

## Goal

Review [target] and report correctness, safety, scope, and evidence gaps.

## Target

- Repository/path: [target path]
- Basis ref or diff: [branch, commit, PR, or local diff]
- Relevant documents or files: [list]

## Review Mode

Review-only. Do not edit files unless a separate task explicitly approves changes.

## Correctness Review

Check:

- the actual task identifier, execution state, completion conditions, and
  decision-critical uncertainty are explicit
- stated behavior matches implementation or documentation
- acceptance trace evidence supports the claim
- verification commands match the changed surface
- a low-cost representative case or reproduction confirmed the execution path
  before implementation when applicable
- two evidence-based corrections failing for the same cause trigger diagnostic
  escalation, and missing input or authority is not treated as a reasoning gap
- PASS, FAIL, NOT RUN, and ENVIRONMENT BLOCKED are used accurately
- historical records are not rewritten as current facts

## Safety Review

Check:

- no secrets, private raw input, sensitive source text, equipment details, live values, or credentials are introduced
- side-effect boundaries are explicit
- approval-gated actions remain approval-gated
- no live/device/runtime behavior is added without approval

## Scope Creep Review

Check:

- changed files match the allowed scope
- no unrelated refactor is included
- no new profile, example, CI workflow, eval harness, audit logging, RAG index, release artifact, or application/device code is added unless explicitly approved
- new reusable surface is justified by the task contract

## Missing Evidence Review

Check:

- verification commands were run or clearly marked NOT RUN / ENVIRONMENT BLOCKED
- evidence paths are listed
- status and acceptance trace are updated when durable repo state changes
- unresolved risks and assumptions are stated
- review breadth matches change risk without weakening required or independent
  review
- completed verification is not repeated without a new failure, input,
  environment or contract change, or concrete unresolved concern

## Completion Report Format

1. Findings ordered by severity
2. Missing or weak evidence
3. Scope and safety assessment
4. Verification reviewed
5. Recommended next action
