# Next Direction Decision

## Purpose

Decide whether post-v0.1.0 work should continue optimizing
`codex-dev-harness` or transition to the downstream Scenario-Simulator
repository for P1 implementation planning.

This is a decision document. It does not add a new profile, create an example,
install CI, publish release evidence, modify Scenario-Simulator production
code, or execute any target render/write.

## Inputs Reviewed

`codex-dev-harness` inputs:

- `AGENTS.md`
- `STATUS.md`
- `docs/POST_V0.1.0_ROADMAP.md`
- `docs/POST_V0.1.0_EVIDENCE_BASELINE_CLOSEOUT.md`
- `docs/EVAL_INTEGRATION_DECISION.md`
- `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`
- `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md`

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

- path: `C:\Users\KSLV-II\codex_projects\ScenarioSimulator`
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

Decision: Option C, do minimal codex-dev-harness closeout cleanup, then move
to Scenario-Simulator P1 planning.

The minimal harness closeout cleanup for this stage is this decision document.
No further codex-dev-harness optimization is required before using the harness
as downstream governance evidence.

## Rationale

The harness has reached the intended local-first governed template baseline.
Additional work inside `codex-dev-harness` would mostly optimize already
deferred surfaces such as CI installation, eval integration, release
publication, RAG/model tooling, audit automation, or more target experiments.
Those are not current strategic priorities.

Scenario-Simulator is the more useful next work area because:

- it has a clear P0.5 to P1 transition point
- it already carries local safety and Codex workflow rules
- it has no production code yet, so P1 scope can be planned cleanly
- the harness downstream experiment already showed that the base template is
  sufficient without creating a dedicated Scenario-Simulator profile
- P1 can be planned without copying raw design documents or sensitive values

## Question Answers

| question | answer |
|---|---|
| Is `codex-dev-harness` sufficiently complete as a local-first governed template baseline? | Yes. It is sufficient for downstream development harness use. |
| Are there blocking cleanup tasks before using it downstream? | No blocking harness cleanup was found. Commit this decision document with the existing Stage 1-4 decisions as the closeout step. |
| Should the next phase move to Scenario-Simulator P1? | Yes, move to Scenario-Simulator P1 planning, not immediate production implementation. |
| What is the first safe P1 task? | Create a P1 WPF/MVVM shell implementation plan and acceptance contract in Scenario-Simulator without adding `.sln`, `.csproj`, `.xaml`, `.cs`, production code, RSID behavior, or sensitive input. |
| What must remain out of scope? | See explicit non-goals below. |
| What harness evidence should be carried forward? | Read-order discipline, task contracts, safety policy, dry-run/approval boundaries, local verification closeout, standalone eval decision, template-only CI decision, and source-basis evidence semantics. |
| Should a harness profile or example be added? | No. Current evidence supports using base templates and Scenario-Simulator repo-local planning docs, not adding `profiles/scenario_simulator` or `examples/scenario_simulator_minimal`. |

## Evidence To Carry Into Scenario-Simulator

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
  Scenario-Simulator later creates generated evidence

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

## First Next Task Prompt

Use this as the next task in Scenario-Simulator:

```text
Repository:
C:\Users\KSLV-II\codex_projects\ScenarioSimulator

Task:
Create a P1 WPF/MVVM shell implementation plan and acceptance contract.

Read first:
- AGENTS.md
- README.md
- STATUS.md
- docs/CODEX_WORKFLOW.md
- docs/PROJECT_STRUCTURE.md
- docs/HARNESS.md
- docs/SECRETS_RULES.md

Goal:
Plan P1 WPF/MVVM shell implementation without creating production code yet.

Allowed files:
- docs/P1_WPF_MVVM_SHELL_PLAN.md
- STATUS.md

Forbidden actions:
- Do not create `.sln`, `.csproj`, `.xaml`, `.cs`, or build assets.
- Do not implement WPF UI, MainWindow, Views, ViewModels, Commands, or bootstrapper code.
- Do not implement ScenarioStep, Excel parsing, XML serialization, simulation engine, RSID UDP communication, mock RSID runtime behavior, polling, connections, tag maps, control actions, live config, or live-write behavior.
- Do not copy raw design documents, private source, secrets, equipment details, IPs, ports, tags, or live parameter values.
- Do not modify Obsidian vault files.

Plan requirements:
- define P1 scope and non-goals
- propose solution/project/file layout for a later approved implementation task
- define acceptance criteria for app launch, visible shell window, one command, and ObservableCollection binding
- define verification commands and expected results
- identify approval boundary before actual code/project creation
- record risks and NOT RUN items honestly

Verification:
- scripts/build.ps1
- scripts/test.ps1
- scripts/smoke.ps1
- scripts/quality_gate.ps1
```

## Verification Status

| repository | command | result | notes |
|---|---|---|---|
| `codex-dev-harness` | `python scripts\quality_gate.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed in this Codex desktop shell with the existing Windows logon session error |
| `codex-dev-harness` | `python scripts\run_eval.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the same environment error |
| `codex-dev-harness` | bundled Python `scripts\quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| `codex-dev-harness` | bundled Python `scripts\run_eval.py` | PASS | 14 named local eval cases passed |
| `codex-dev-harness` | `powershell -ExecutionPolicy Bypass -File scripts\run_local_verify.ps1` | PASS | pytest 72 passed, quality gate passed, and three example render dry-runs passed |
| `codex-dev-harness` | `git diff --check` | PASS | no whitespace errors reported |
| Scenario-Simulator | `scripts\build.ps1` | PASS | placeholder P0.5 check exited 0; no solution found, expected |
| Scenario-Simulator | `scripts\test.ps1` | PASS | placeholder P0.5 check exited 0; no solution found, expected |
| Scenario-Simulator | `scripts\smoke.ps1` | PASS | placeholder P0.5 check exited 0; no solution found, expected |
| Scenario-Simulator | `scripts\quality_gate.ps1` | PASS | ran build, test, and smoke placeholders; no solution found, expected |

No release artifacts were regenerated. No target render/write was executed.
No Scenario-Simulator production files were modified.

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
- no C# solution/project/source/XAML/build assets
- no PLC/device code
- no live config or live-write behavior
- no raw private source, secrets, or sensitive values copied into either repo
