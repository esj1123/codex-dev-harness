# Stage 5B Target Repo Selection And Probe Plan

## Purpose

Define the next post-v0.1.0 step without expanding `codex-dev-harness`.

Current sequencing note: this record is historical Stage 5B handoff evidence.
It is superseded for implementation sequencing by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`. Its freeze decision remains useful
risk evidence for small scoped phases, but it is not a permanent blocker to the
roadmap targets.

Stage 5B recorded this repository as stable at the then-current local-first
governed baseline, selected `stock` as the first practical probe candidate, and
defined a low-risk test-only/dry-run evidence path safety probe to run later in
the target repository under that repository's own rules.

This is a planning document. It does not scan `stock`, modify any downstream
repository, generate release evidence, install CI, add runtime code, add RAG or
audit automation, or start Scenario-Simulator production implementation.

## Decision

Stage 5B decision: keep `codex-dev-harness` stable as the then-current
local-first governed baseline, select `stock` as the first practical probe
candidate, and defer Scenario-Simulator to architecture/planning work.

The Stage 5B flow was:

1. target repository selection
2. `stock` practical probe
3. probe closeout review

This decision does not approve harness automation expansion. Repeated practical
probe evidence is required before adding new harness code, gates, profiles,
examples, CI, RAG/index tooling, audit automation, or release automation.

## Stage 5B Harness Position

`codex-dev-harness` was treated as stable because it already contained the
baseline surfaces needed for governed AI/Codex work:

- read-order and task-contract rules
- safety and side-effect boundaries
- base templates and selected existing profiles
- dry-run-first render tooling
- local quality gate and local verification wrapper
- standalone local eval runner
- local release evidence policies and generators
- AI readiness scanner documentation and standalone local tooling
- current roadmap, status, and acceptance trace records

Additional work inside this repository would mostly pull deferred surfaces into
the baseline: CI installation, eval quality-gate integration, RAG/index tooling,
audit automation, release publication, new profiles, new examples, application
code, or downstream implementation. Those are not needed to learn whether the
governance model works in a practical target.

The correct next evidence should come from a small target-repo probe, not from
more harness surface area.

## Scenario-Simulator Deferral

Scenario-Simulator remains a valid downstream architecture and planning
candidate, but it is deferred as the first practical probe.

Reasons:

- its next useful work is architecture/P1 planning, not a narrow safety probe
- it is WPF/MVVM and RSID-adjacent, which increases scope and approval burden
- production implementation would require project files, UI, commands,
  serialization, simulation, or RSID behavior that remains explicitly deferred
- prior harness evidence already showed Scenario-Simulator can be handled as a
  downstream candidate without a dedicated profile or example

Do not add `profiles/scenario_simulator` or
`examples/scenario_simulator_minimal`. Do not start Scenario-Simulator
production implementation from this Stage 5B plan.

## Selected First Practical Probe Candidate

Selected candidate: `stock`.

`stock` is selected because the first probe can be constrained to evidence-path
safety instead of product implementation. A stock or broker-adjacent repository
has real domain risk, but that risk makes it useful for proving that AI/Codex
work can remain inside dry-run, synthetic, test-only, no-live-action boundaries.

The first practical probe is not a trading, broker, data-ingestion, scheduler,
automation, or production feature task. It is a low-risk verification task that
should prove whether existing or proposed safety boundaries prevent live or
private-data side effects.

## Candidate Criteria

A target repo is a good Stage 5B practical probe candidate only if it meets
these criteria:

| criterion | requirement |
|---|---|
| local-first | Work can happen locally without network services, external APIs, CI, or deployment. |
| narrow evidence path | The first task can be limited to tests or dry-run behavior. |
| no live mutation | No live target, device, broker, account, order, send, deploy, or write behavior is needed. |
| synthetic data | Tests can use synthetic fixtures or existing safe sample data only. |
| clear safety boundary | Forbidden data and side effects can be stated before edits. |
| small touch surface | The first probe can avoid runtime code and avoid broad refactors. |
| verifiable closeout | The repo has, or can define, local verification commands and honest `PASS` / `FAIL` / `NOT RUN` reporting. |
| useful signal | The result teaches whether harness-style governance works outside the harness. |

Candidates that require live credentials, real account data, production writes,
network calls, scheduler activation, release publication, deployment, or large
architecture decisions should be deferred.

## Candidate Evaluation

| candidate | Stage 5B treatment | rationale |
|---|---|---|
| `codex-dev-harness` | frozen baseline | It already contains the governed local-first template baseline and is not the active product implementation target. |
| `stock` | selected first practical probe candidate | It can provide useful broker/finance safety signal while staying limited to tests, dry-run evidence paths, synthetic data, and no live action. |
| Scenario-Simulator | deferred architecture/planning candidate | Its next useful work is WPF/MVVM and RSID-adjacent planning, not the smallest practical safety probe. |
| `outlook-history-view` | fallback governance-only probe candidate | It may be useful later if `stock` is blocked, but only for low-risk governance or documentation evidence under its own repo rules. |

## First Stock Probe Scope

First stock probe: test-only/dry-run evidence path safety coverage.

The probe should be performed in the `stock` repository in a separate future
task. It should start with read-only inspection of that repository's rules,
status, tests, and safety boundaries. The first write, if any, should be limited
to target-repo test or documentation files explicitly approved by that future
task.

The first stock probe should verify safety coverage for an evidence path such
as:

- dry-run command behavior
- report/output path boundary
- synthetic fixture handling
- no broker/order/account mutation
- no network call requirement
- no secret, token, account, email, private input, or live config exposure
- fail-closed behavior when a live-action flag, credential, or unsafe output
  path is present

If the target repository lacks a testable dry-run/evidence path, the probe
should stop and record `BLOCKED` or create a planning-only recommendation. Do
not add production code to create the path during the first probe.

## Stock Probe Non-Goals

The first stock probe must not:

- add runtime code
- add application code
- add broker API integration
- place, simulate through a live broker, cancel, modify, or schedule orders
- fetch live market data or call external APIs
- use private account data, credentials, tokens, keys, or customer data
- add a scheduler, daemon, background worker, or automation trigger
- add CI workflows or required checks
- generate release artifacts
- add RAG, indexes, embeddings, vector stores, or retrieval tooling
- add audit logging automation
- modify production trading, portfolio, account, notification, or persistence
  behavior
- broaden `codex-dev-harness` profiles, examples, gates, or runtime behavior

## Risks / Assumptions

- `stock` remains the preferred first practical probe only while local
  verification and dry-run/live-write boundaries remain available.
- Practical probes must stay low-risk, small, and close to existing target-repo
  tests or documentation.
- This harness decision does not approve live broker work, live vault writes,
  private data use, credential handling, account mutation, order behavior,
  market-data fetching, or network calls.
- Repeated probe evidence is required before adding new harness automation,
  profiles, examples, gates, CI, RAG/index tooling, audit automation, or
  release automation.

## Verification Commands

For this Stage 5B planning task in `codex-dev-harness`, run:

- `python -m pytest`
- `python scripts/quality_gate.py`
- `python scripts/run_eval.py`
- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`
- `git diff --check`

For the later `stock` probe, verification commands must be discovered from the
`stock` repository after reading its local instructions. If no safe local
verification command exists, record `NOT RUN` or `BLOCKED` instead of inventing
one.

## Closeout Format

Every Stage 5B closeout should report:

1. Outcome.
2. Changed files or produced artifacts.
3. Verification result for each requested command.
4. Safety checks, including no runtime code, no live action, no CI, no RAG, no
   audit automation, no release artifact generation, and no downstream
   implementation.
5. `NOT RUN`, `BLOCKED`, or `ENVIRONMENT BLOCKED` items.
6. Risks and assumptions.
7. Next recommended stock probe.

## Explicit Non-Goals

This plan does not approve:

- runtime code
- application code
- PLC/device code
- live target behavior
- broker, account, order, notification, scheduler, or live market behavior
- CI workflow installation
- eval integration into `scripts/quality_gate.py`
- RAG/index/vector store implementation
- audit automation
- release artifact generation
- tag or release publication
- Scenario-Simulator production implementation
- a Scenario-Simulator profile or example
- stock repository writes from this harness-planning task
- sibling repository scanning from this harness-planning task

## Next Recommended Stock Probe

Run a future task in the `stock` repository:

```text
Task:
Create a test-only/dry-run evidence path safety probe.

Goal:
Verify that the stock repository can prove safety boundaries for dry-run
evidence paths without live broker/account/order/network behavior.

Read first:
- AGENTS.md
- README.md
- STATUS.md
- available safety, verification, and test docs

Allowed by default:
- read-only inspection first
- tests or documentation only, if explicitly allowed by the target task
- synthetic fixtures only

Forbidden:
- no runtime or production code
- no broker/API/order/account/live market behavior
- no credentials, private account data, secrets, tokens, or live config
- no scheduler, CI, release, RAG, audit automation, or deployment

Closeout:
Report changed files, verification, safety checks, NOT RUN/BLOCKED items,
risks, and the next smallest follow-up.
```
