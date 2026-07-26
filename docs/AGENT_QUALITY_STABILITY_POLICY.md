# Agent Quality Stability Policy

## Purpose

Define a local-first, approval-gated method for measuring whether repeated
AI-assisted implementations preserve quality. This policy supplements the
deterministic repository checks; it does not replace pytest, the standalone
eval runner, the quality gate, work-package preflight/postflight, or human
approval.

## Quality Dimensions

Every governed trial is graded independently on:

1. `functional_correctness`
2. `contract_adherence`
3. `scope_adherence`
4. `semantic_consistency`
5. `architectural_consistency`
6. `safety_compliance`
7. `reproducibility`

Passing tests alone is not sufficient. A critical failure, contract reopen,
scope violation, safety violation, or semantic blocker prevents baseline
adoption.

## Evaluation Classes

- `static_regression`: the existing deterministic repository evals.
- `agentic_regression`: bounded implementation tasks with deterministic
  graders and repeated trials.
- `capability`: difficult or incomplete tasks used to measure progress; these
  are informational and do not block the baseline unless separately promoted.
- `owner_held_holdout`: synthetic graders kept outside agent worktrees. Only
  safe identifiers and hashes may be tracked.

The first agentic regression suite uses five historical, synthetic-safe
`local-data-quality-cli` task classes and nineteen total trials. It does not
modify the target repository main branch.

## Fingerprint And Comparability

Each run records repository and contract bases, work-package plan digest,
agent/model configuration, prompt and tool-policy hashes, dependency and corpus
hashes, environment profile, verification suite, and grader version.
Aggregation binds each run to the suite task's declared source basis, lane, and
work-package plan digest. A suite manifest hash prevents comparison across
different task definitions that happen to reuse the same suite ID.

Canonical compact JSON with sorted keys is hashed with SHA-256 to produce:

- `configuration_id`
- `run_fingerprint_id`

Unavailable values are recorded as `UNKNOWN`, never guessed. Any unknown
fingerprint field makes the run `PARTIAL` and prevents baseline adoption.

## Trial Evidence

Run envelopes are bounded safe summaries. They must not contain:

- raw prompts, transcripts, command logs, or model output;
- private or live source;
- secrets, tokens, account values, IPs, ports, or endpoints;
- local absolute paths;
- raw downstream rows, cells, or rules payloads.

Trial envelopes and owner-held fixtures remain under ignored `local/` or an
approved OS temporary directory. The tracked baseline contains aggregate
counts, identifiers, hashes, and safe evidence references only.

## Repeated Trial Metrics

The policy uses explicit empirical metrics rather than ambiguous probability
notation:

- `strict_pass_3_task_rate`
- `strict_pass_5_critical_rate`
- `critical_failure_count`
- `scope_violation_count`
- `safety_violation_count`
- `postflight_block_count`
- `contract_reopen_count`
- `semantic_blocker_count`
- `integration_fix_file_count`
- `integration_fix_line_count`

The first provisional baseline requires both strict-pass rates to equal `1.0`
and every blocker count to equal zero. Agentic regression v1 also requires
exactly one owner-held holdout result per run; every holdout must pass.

## Semantic Review

Deterministic grading checks public symbols, reason-code vocabulary, output
schema, dependency changes, import direction, duplicate definitions, and
deterministic output. An integration owner who did not implement the trial
reviews blinded trial summaries for naming, abstraction, validation, exception,
and cross-lane consistency.

Human adjudication is required for any critical disagreement or semantic
blocker. Agent majority voting is not sufficient.

## Failure-To-Eval Lifecycle

Failures move only through:

`OBSERVED -> QUARANTINED -> SANITIZED -> REPRODUCED -> HUMAN_REVIEWED ->
GRADER_VALIDATED -> REGRESSION -> DEPRECATED`.

Pre-regression evidence stays local and ignored. A tracked regression contains
only a minimal synthetic fixture, safe symptom summary, invariant and grader
identifiers, dates, and affected configuration hashes. Failure evidence is not
automatically written to memory, RAG, audit logs, or release evidence.
Lifecycle validation checks structural evidence, date order, and adjacent state
transitions. It does not authenticate that a human or grader supplied the
declared review references.

## Baseline And Adoption

`artifacts/agent-quality-baseline.json` is non-release quality evidence. It is
not part of the five-file release checksum set. Initial creation requires a
separate approval reference; overwrite is rejected by default.

A candidate model, prompt, tool, or skill configuration must run the same
suite. Adoption is blocked if:

- fingerprint comparability is not full;
- any critical, scope, safety, contract, or semantic blocker exists;
- strict-pass rates regress;
- required holdout cases fail.

Cost or duration growth without a quality regression requires owner review; it
is not an automatic adoption decision.

## Boundaries

This policy does not authorize agent runtime adapters, network access, CI
triggers, quality-gate execution of agent trials, release blocking, LLM judges,
prompt/output capture, automatic failure promotion, memory writes, RAG writes,
push, release, deployment, or live action.
