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
Aggregation binds each run to the suite task's declared source basis, lane,
verification contract, required invariant IDs, and invariant grader ID. The
suite fixes a safe interpreter identity and exact argument arrays for every
required command. A current run must provide exactly one result for every
declared invariant. Each result records the bound grader ID, `PASS`, `FAIL`, or
`NOT RUN`, and a SHA-256 result hash. Only all-`PASS` invariant evidence is
eligible for strict pass.
Run evidence records the execution-specific work-package digest and must show
all required command IDs complete before a `PASS` is eligible for strict pass.
All trials for one task must share one package digest.

The canonical suite does not embed an execution-specific package digest because
approval references and fixture instances can differ between governed runs.
Legacy suite manifests that contain a declared package digest remain readable
for historical aggregation, and historical unbound run envelopes remain
readable with their historical suite. They cannot satisfy the current tracked
suite or become evidence for a new bound baseline.
A suite manifest hash prevents comparison across different task definitions
that happen to reuse the same suite ID.

Canonical compact JSON with sorted keys is hashed with SHA-256 to produce:

- `configuration_id`
- `run_fingerprint_id`

Unavailable values are recorded as `UNKNOWN`, never guessed. Any unknown
fingerprint field makes the run `PARTIAL` and prevents baseline adoption.

## Trial Evidence

Historical v1 run envelopes are bounded manually supplied safe summaries and
remain readable only as historical evidence. New adoption evidence uses
`agent-run-v2`: the recorder executes the package verification commands and
owner-held grader itself, observes Git state, and records only exit codes,
counts, identifiers, and SHA-256 values. Manual `execution.status=PASS` and
manual completed-command declarations are not v2 evidence.

The launch receipt binds the requested role profile, safe agent identifier, and
request hash. It records `model_selection_source=ADAPTER_REQUEST` and
`model_observation_status=NOT_INDEPENDENTLY_OBSERVABLE`; it does not claim
independent provider-side model attestation.

Run envelopes must not contain:

- raw prompts, transcripts, command logs, or model output;
- private or live source;
- secrets, tokens, account values, IPs, ports, or endpoints;
- local absolute paths;
- raw downstream rows, cells, or rules payloads.

Trial envelopes and owner-held fixtures remain under ignored `local/` or an
approved OS temporary directory. The tracked baseline contains aggregate
counts, a bounded per-run evidence manifest, identifiers, hashes, and safe
evidence references only. Run, baseline, and failure references use the same
Windows-safe repository-relative path policy. Failure fixtures must additionally
remain under `evals/agentic/fixtures/`.

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

## Role-Aware Profiles

`evals/agentic/agent-role-profiles.json` is the machine-readable role profile
set. The initial set keeps `gpt-5.6-sol` fixed and varies reasoning only:
contract planning uses `high`, ordinary feature implementation uses `medium`,
critical implementation and integration ownership use `high`, and blinded
semantic review uses `xhigh`. These profiles apply to future subagent launch
requests, not to the current interactive chat.

Work-package plan digests bind `agent_profile_id` and `agent_profile_hash`.
Agentic regression v2 aggregates one configuration per role and derives an
ordered `profile_set_hash` and `system_configuration_id`. Comparisons are made
only within the same role/profile set. A profile-set mismatch is `HOLD`, not a
quality regression. Profile calibration is required before a fresh nineteen
trial adoption run.

## Semantic Review

Deterministic grading checks public symbols, reason-code vocabulary, output
schema, dependency changes, import direction, duplicate definitions, and
deterministic output. An integration owner who did not implement the trial
reviews blinded trial summaries for naming, abstraction, validation, exception,
and cross-lane consistency.

Human adjudication is required for any critical disagreement or semantic
blocker. Agent majority voting is not sufficient.

Observed failure families may be named as required task invariants before they
become tracked regression fixtures. This makes the next trial contract
fail-closed without claiming that lifecycle promotion occurred. The current
parser invariants cover bounded finite Decimal forms, malformed numeric bounds,
and non-encodable Unicode. The integration invariants require historical
evidence preservation and malformed-schema regression coverage.

An invariant result proves only that the declared grader produced the recorded
safe status and result hash for that run. The binding is structural evidence;
it does not authenticate grader ownership, owner approval, or human review.

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
declared review references. Reproduction dates and review references are
forbidden before their lifecycle stage. Transition validation accepts complete
current and next case JSON records, preserves identity fields, and requires
reproduction dates and review references to advance monotonically.
Adding an invariant ID to a suite is not a `HUMAN_REVIEWED`,
`GRADER_VALIDATED`, or `REGRESSION` lifecycle transition.

## Baseline And Adoption

`artifacts/agent-quality-baseline.json` is non-release quality evidence. It is
not part of the five-file release checksum set. Initial creation requires a
separate approval reference; overwrite is rejected by default.

The baseline writer reads the canonical suite and every sanitized run envelope,
recomputes the aggregate, and refuses ineligible results. It does not accept a
caller-supplied aggregate summary. Candidate comparison likewise recomputes the
candidate from its suite and run directory, reads only the exact tracked
baseline path, and validates both baseline and candidate against the same
canonical suite. Malformed input fails first; suite
or configuration non-comparability holds without metric comparison; only a
comparable quality regression is rejected.

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
