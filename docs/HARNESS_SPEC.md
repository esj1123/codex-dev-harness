# Harness Specification

## Definition

The harness is the reusable execution-control and verification layer inside a
governed AI-assisted development system. It coordinates work without becoming
the downstream product or an autonomous approval authority.

## Required Capabilities

The harness provides:

1. machine-readable authority and human sequencing;
2. task and work-package contracts;
3. base templates, profiles, and tiered rendering;
4. side-effect and downstream boundaries;
5. focused, V2, impact-extra, and manual V3 verification;
6. safe JSON evidence and checkout-independent integrity checks;
7. advisory approved-corpus retrieval;
8. repeated Agent Quality trial validation and aggregation; and
9. bounded closeout and handoff.

## Operating Invariants

- Read current authority before historical evidence.
- Inspect before mutation and dry-run before render.
- Keep feature-lane write sets disjoint.
- Freeze shared contracts before parallel implementation.
- Treat preflight, postflight, validation, and quality PASS as evidence, not
  authorization.
- Use synthetic or minimized inputs instead of private or live data.
- Keep raw prompts, transcripts, model output, secrets, and absolute local
  paths out of tracked evidence.
- Report unexecuted checks as `NOT RUN`.
- Separate local commits, remote push, workflow execution, artifact writes, and
  publication approvals.

## Repository Boundary

The repository contains harness policy, templates, scripts, schemas, examples,
tests, and approved evidence. It does not contain the application source of a
downstream project, PLC or device control code, live configuration, or
credentials.

## Verification Contract

Normal local verification is read-only with respect to tracked evidence and
runs pytest, standalone eval, quality gates, and profile dry-runs. Impact
planning adds only the checks required by changed paths.

Release verification is a separate artifact-writing path and requires explicit
authorization. Remote verification is manual, exact-SHA, read-only, and does
not upload artifacts.

## Extension Rule

Add a shared capability only after repeated use shows that it removes material
cost or prevents a demonstrated failure. Prefer a local contract or focused
test over a new global abstraction. New profiles, automation, runtime adapters,
and external integrations require separate owner decisions.
