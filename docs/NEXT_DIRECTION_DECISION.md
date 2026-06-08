# Next Direction Decision

## Purpose

Record the post-v0.1.0 direction decision and its Stage 5B update.

Current sequencing note: this record is historical transition evidence. It is
superseded for implementation sequencing by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, which sets read-only CI +
verification hygiene as the first implementation target.

Stage 5A established that `codex-dev-harness` is complete enough as a
local-first governed template baseline. Stage 5B keeps that baseline frozen,
defers Scenario-Simulator as an architecture/planning candidate, and selects
`stock` as the first practical probe candidate.

This is a decision document. It does not add a new profile, create an example,
install CI, publish release evidence, modify Scenario-Simulator production
code, modify `stock`, or execute any target render/write.

## Inputs Reviewed

`codex-dev-harness` inputs:

- `AGENTS.md`
- `STATUS.md`
- `docs/POST_V0.1.0_ROADMAP.md`
- `docs/POST_V0.1.0_EVIDENCE_BASELINE_CLOSEOUT.md`
- `docs/EVAL_INTEGRATION_DECISION.md`
- `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`
- `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md`
- `docs/STAGE_5B_TARGET_REPO_SELECTION_AND_PROBE_PLAN.md`

Scenario-Simulator inputs:

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/CODEX_WORKFLOW.md`
- `docs/HARNESS.md`
- `docs/SECRETS_RULES.md`

## Current Harness Baseline Summary

`codex-dev-harness` is sufficiently complete as a local-first governed
template baseline for downstream adoption.

Harness repository inspected:

- branch/ref at inspection: `main` / `origin/main`
- commit at inspection: `dbf12709833cd589296c5a98d8051029fc5d5282`

The current baseline includes:

- root contract documents and read-order rules
- safety, verification, profile, handoff, and acceptance-trace docs
- base Markdown templates and existing profile templates
- render tooling and dry-run-first examples
- local quality gate and local verification wrapper
- standalone local non-LLM eval runner with 14 named cases
- local release evidence generators and artifacts
- minimal local SBOM/provenance evidence
- Python runtime and development dependency reproducibility files
- optional CI templates kept inert and not installed
- prompt contract templates and governance policies
- downstream Scenario-Simulator base-template experiment evidence

The baseline is not an application project. It still intentionally excludes
real application code, device code, live-write behavior, active CI workflows,
release publication, release archives, signing, tag movement, RAG/model
tooling, audit log automation, and dedicated Scenario-Simulator profile or
example surfaces.

## Scenario-Simulator Readiness Summary

Scenario-Simulator repository inspected:

- path: local Scenario-Simulator checkout; absolute path intentionally omitted
- branch/ref at inspection: `main` / `origin/main`
- commit at inspection: `a5b8da2ed7ba7a0c156e97c6356aed21341480c6`
- current phase: P0.5 Coding Infrastructure

The repository currently contains safe project infrastructure only:

- repository operating rules
- project status and README
- project structure plan
- Codex workflow rules
- harness plan
- secrets rules
- placeholder `src/`, `tests/`, `harness/`, and `samples/` documentation
- placeholder verification scripts

The repository does not yet contain a real WPF solution or production feature
code. Its own rules explicitly defer WPF UI, `MainWindow`, Views, ViewModels,
Commands, bootstrapper code, `ScenarioStep`, Excel parsing, XML serialization,
simulation engine, RSID UDP communication, mock RSID runtime behavior, and
`.sln`, `.csproj`, `.xaml`, or production `.cs` files until later approved
phases.

One local ignored zero-byte hidden/system `.DOCX` file was observed at the
Scenario-Simulator repository root during inspection. This should not block P1
planning, but it should remain unmodified unless a separate cleanup task
explicitly approves local ignored artifact handling.

## Decision

Stage 5A decision: do minimal `codex-dev-harness` closeout cleanup and treat
the harness as sufficiently complete for downstream governance evidence.

Stage 5B historical update: keep `codex-dev-harness` stable as the
then-current local-first governed baseline, defer Scenario-Simulator as an
architecture/planning candidate, and select `stock` as the first practical
probe candidate.

The first stock probe is limited to test-only/dry-run evidence path safety
coverage. It is not a production implementation, broker/API integration,
trading, scheduling, CI, release, RAG, audit, or runtime-code task.

Stage 5A transition cleanup confirms that Stages 1-4 are complete:

- Stage 1 documentation drift cleanup.
- Stage 2 local post-v0.1.0 evidence baseline.
- Stage 3 eval integration decision: historical standalone runtime baseline.
- Stage 4 optional CI decision: historical template-only risk evidence.

The next strategic decision is now limited to the future `stock` probe or small
harness refinement only if the stock probe exposes a concrete harness
documentation gap. `plc_or_device_tool` actual target execution remains
deferred and is not the next default stage.

## Rationale

The harness has reached the intended local-first governed template baseline.
Additional work inside `codex-dev-harness` would mostly optimize already
deferred surfaces such as CI installation, eval integration, release
publication, RAG/model tooling, audit automation, or more target experiments.
Those are not current strategic priorities.

Scenario-Simulator remains useful, but as an architecture/planning candidate.
It is not the first practical probe because its next useful work is WPF/MVVM
and RSID-adjacent planning with a larger approval boundary.

`stock` is the better first practical probe because:

- the first task can be constrained to tests or dry-run behavior
- evidence-path safety can be tested without runtime implementation
- broker/finance risk gives useful signal for no-live-action governance
- synthetic fixtures and no-network expectations can be made explicit
- failure can be recorded as `BLOCKED` without adding production code

## Question Answers

| question | answer |
|---|---|
| Is `codex-dev-harness` sufficiently complete as a local-first governed template baseline? | Yes. It is sufficient for downstream development harness use. |
| Are there blocking cleanup tasks before using it downstream? | No blocking harness cleanup was found. Commit this decision document with the existing Stage 1-4 decisions as the closeout step. |
| Should the next phase move to Scenario-Simulator P1? | Not by default. Scenario-Simulator is deferred as an architecture/planning candidate. |
| What is the first safe practical task? | In the future `stock` target repo, create a test-only/dry-run evidence path safety probe without runtime code, broker/API/order/account/network behavior, secrets, or private data. |
| What must remain out of scope? | See explicit non-goals below. |
| What harness evidence should be carried forward? | Read-order discipline, task contracts, safety policy, dry-run/approval boundaries, local verification closeout, standalone eval decision, template-only CI decision, and source-basis evidence semantics. |
| Should a harness profile or example be added? | No. Current evidence supports target-repo-local planning and probe work, not adding `profiles/scenario_simulator`, `examples/scenario_simulator_minimal`, or a new `stock` profile/example. |

## Evidence To Carry Into Stock

Carry these practices forward, not repository-specific artifacts:

- read-order-first task setup
- explicit task contract before edits
- read-only inspection before mutation
- no raw private source or sensitive value capture
- source-index and data-scope thinking
- approval-gated side-effect boundaries
- dry-run or planning-first behavior before implementation
- honest `PASS` / `FAIL` / `NOT RUN` / `ENVIRONMENT BLOCKED` reporting
- local verification before closeout
- standalone eval as optional evidence, not default quality-gate integration
- CI as deferred/template-only unless separately approved
- release evidence source-basis versus artifact-containing commit semantics if
  `stock` later creates generated evidence

## Explicit Non-Goals

This decision does not approve:

- `plc_or_device_tool` actual target experiment
- `profiles/scenario_simulator`
- `examples/scenario_simulator_minimal`
- optional design-stage pack render/gate/example integration
- active GitHub Actions workflow installation
- required CI checks
- CI artifact upload
- release publication
- release archive creation
- tag creation, movement, rewrite, or signing
- RAG indexes, embeddings, vector stores, retrieval tooling, or model
  comparison tooling
- audit log automation or real audit session logs
- Scenario-Simulator production code changes in this decision task
- WPF UI, `MainWindow`, Views, ViewModels, Commands, or bootstrapper code in
  this decision task
- `.sln`, `.csproj`, `.xaml`, `.cs`, or build asset creation in this decision
  task
- Excel parser, XML serialization, simulation engine, RSID UDP communication,
  mock RSID runtime, live config, polling, tag maps, control actions, or
  live-write behavior
- copying raw design documents, private source, IP, equipment details, IP/port
  values, tags, live parameters, or sensitive requirement text
- stock runtime or application code changes in this decision task
- broker API integration, order placement, order modification, cancellation,
  scheduling, account mutation, live market data fetching, or network calls
- stock target repository writes, tests, reports, or generated artifacts from
  this harness decision task

## First Next Task Prompt

Use this as the next task in `stock`:

```text
Repository:
stock

Task:
Create a test-only/dry-run evidence path safety probe.

Read first:
- AGENTS.md
- README.md
- STATUS.md
- available safety, verification, and test documentation

Goal:
Verify that the stock repository can prove dry-run evidence path safety without
live broker/account/order/network behavior.

Allowed files:
- target-repo test files only, if explicitly approved by that future task
- target-repo documentation only, if needed to record NOT RUN/BLOCKED evidence

Forbidden actions:
- Do not add runtime or production code.
- Do not add broker API integration, order behavior, account mutation, live
  market data fetching, scheduling, or network calls.
- Do not use credentials, private account data, secrets, tokens, or live config.
- Do not install CI, generate release artifacts, add RAG, add audit automation,
  or deploy anything.

Plan requirements:
- inspect existing tests and safety boundaries first
- identify a dry-run/evidence path that can be tested with synthetic data
- add or propose only tests/docs within the approved target scope
- prove no live broker/account/order/network behavior is required
- record BLOCKED if no testable dry-run path exists without production changes

Verification:
- use stock repository local verification commands after reading its docs
- record NOT RUN or BLOCKED honestly if no safe command exists
```

## Verification Status

| repository | command | result | notes |
|---|---|---|---|
| `codex-dev-harness` | `python -m pytest` | ENVIRONMENT BLOCKED | Bare `python.exe` failed in this Codex desktop shell with the existing Windows logon session error |
| `codex-dev-harness` | `python scripts\quality_gate.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the same environment error |
| `codex-dev-harness` | `python scripts\run_eval.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the same environment error |
| `codex-dev-harness` | bundled Python `scripts\quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| `codex-dev-harness` | bundled Python `scripts\run_eval.py` | PASS | 14 named local eval cases passed |
| `codex-dev-harness` | bundled Python `-m pytest` | BLOCKED | bundled runtime is available but currently has no `pytest` module installed |
| `codex-dev-harness` | `powershell -ExecutionPolicy Bypass -File scripts\run_local_verify.ps1` | BLOCKED | wrapper stops at pytest because the bundled runtime has no `pytest` module installed |
| `codex-dev-harness` | `git diff --check` | PASS | no whitespace errors; Git reported LF-to-CRLF working-copy warnings |

No release artifacts were regenerated. No target render/write was executed.
No Scenario-Simulator production files were modified. No `stock` repository
scan, write, test run, report, generated artifact, runtime code, or live broker
behavior was performed by this decision task.

## Safety Checks

This decision keeps all of the following unchanged:

- no new codex-dev-harness profile
- no new codex-dev-harness example
- no active `.github/workflows/`
- no release archive
- no release publication
- no tag creation, movement, rewrite, or signing
- no RAG/model tooling
- no audit automation
- no Scenario-Simulator production code changes
- no stock repository writes, test runs, reports, generated artifacts, runtime
  code, broker/API/order/account/network behavior, or live market behavior
- no C# solution/project/source/XAML/build assets
- no PLC/device code
- no live config or live-write behavior
- no raw private source, secrets, or sensitive values copied into either repo
