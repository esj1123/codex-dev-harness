# STATUS.md

## Current Phase

Post v0.1.0-rc1 base template strengthening.

## Current State

The repository contains documentation, base templates, profile templates, render tooling, quality gates, tests, and minimal example skeletons.

## What Exists

- Core repo contract documents.
- Safety and verification policy documents.
- Release readiness documents:
  - `docs/ARCHITECTURE.md`
  - `docs/VALIDATION_SCOPE.md`
  - `docs/TEMPLATE_EXTENSION_POLICY.md`
  - `docs/DOMAIN_ADAPTATION_GUIDE.md`
  - `docs/adr/ADR-0001-local-first.md`
  - `docs/adr/ADR-0002-base-template-over-domain-profile.md`
  - `docs/adr/ADR-0003-approval-gated-side-effect.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/KNOWN_LIMITATIONS.md`
  - `docs/CI_POLICY.md`
  - `docs/LOCAL_USAGE.md`
  - `docs/LOCAL_RELEASE_PACKAGE.md`
  - `docs/P6_RELEASE_CLOSEOUT.md`
  - `docs/RELEASE_NOTES_v0.1.0-rc1.md`
  - `docs/RELEASE_RECORD_v0.1.0-rc1.md`
  - `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md`
  - `docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md`
  - `docs/OPTIONAL_GITHUB_ACTIONS.md`
- Base markdown templates, including source index, project boundary, data scope, phase plan, and approvals templates.
- Profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`.
- `scripts/render_template.py`.
- `scripts/quality_gate.py`.
- Gate modules under `scripts/gates/`.
- Example skeletons:
  - `examples/python_cli_minimal`
  - `examples/csharp_desktop_minimal`
  - `examples/plc_tool_minimal`
- Tests under `tests/`.
- Local verification wrapper: `scripts/run_local_verify.ps1`.
- Optional GitHub Actions template: `templates/ci/github-actions-local-verify.yml.template`.

## What Does Not Exist Yet

- Real application code.
- Real PLC/device code.
- Live target write behavior.
- Real secret/config files.
- CI workflow.
- Release automation.
- Formal `v0.1.0` tag.
- Dedicated `scenario_simulator` profile.
- `examples/scenario_simulator_minimal`.

## Known Constraints

- YAML parsing is intentionally scalar-only.
- Examples are skeletons only.
- Runtime checks in examples may be marked NOT RUN when code or scripts do not exist.
- Render targets inside this repository are limited to `examples/<name>`.

## Latest Verification

Verified commit: `10bccadd15be9401847620eba61d3c8c4117962d`

Tag name: `v0.1.0-rc1`

Tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`

Tag object: `9ca08efbd43cd2c5defba7875efbd7ca702c6166`

| check | status | evidence |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and 3 render dry-runs passed |
| `python -m pytest` | PASS | 16 passed through the local Python runtime used by the verification wrapper |
| `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, secret scan passed through the local Python runtime |
| python_cli render dry-run | PASS | `examples/python_cli_minimal` dry-run succeeded |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal` dry-run succeeded |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal` dry-run succeeded |
| CI workflow | NOT RUN | Not included in this repository baseline |
| release tag | CREATED | `v0.1.0-rc1` points to `10bccadd15be9401847620eba61d3c8c4117962d` |
| release notes | PRESENT | `docs/RELEASE_NOTES_v0.1.0-rc1.md` exists |
| release record | PRESENT | `docs/RELEASE_RECORD_v0.1.0-rc1.md` exists |
| optional GitHub Actions guide | PRESENT | guide and template exist, but no workflow is installed |

## Clean Clone Validation

| item | status | evidence |
|---|---|---|
| clean clone | PASS | Separate temporary clone created |
| checkout ref | PASS | `v0.1.0-rc1` checked out in detached HEAD |
| tag target | PASS | `v0.1.0-rc1` resolves to `10bccadd15be9401847620eba61d3c8c4117962d` |
| dependency install command | ENVIRONMENT BLOCKED | Bare `python.exe` launcher is unavailable in this Codex desktop shell |
| local Python runtime dependency check | PASS | `pytest` already satisfied for wrapper runtime |
| local verification wrapper | PASS | pytest, quality gate, and 3 render dry-runs passed |
| `.github/workflows` | ABSENT | No workflow installed |
| application/device/live-write scope | PASS | No real application code, PLC/device code, or live target write support added |

## Local Target Experiment

| item | status | evidence |
|---|---|---|
| basis tag | PASS | `v0.1.0-rc1` |
| profile | PASS | `python_cli` |
| target folder | PASS | Separate temporary local target folder |
| pre-render verification | PASS | `scripts/run_local_verify.ps1` passed from tag checkout |
| dry-run render | PASS | 11 Markdown outputs planned |
| actual render | PASS | 11 Markdown docs generated after local target write permission was granted |
| generated runtime code | ABSENT | No application runtime code generated |
| private/secrets/live-write scope | PASS | No private input, secrets, or live target write support generated |

## Base Template Strengthening

| item | status | evidence |
|---|---|---|
| architecture model | PRESENT | `docs/ARCHITECTURE.md` defines control, template, profile, render, verification, side-effect, release, optional CI, and downstream application planes |
| validation scope | PRESENT | `docs/VALIDATION_SCOPE.md` separates regression examples from downstream candidates |
| extension policy | PRESENT | `docs/TEMPLATE_EXTENSION_POLICY.md` states that new profiles are approval-gated and should not be created for every project type |
| domain adaptation | PRESENT | `docs/DOMAIN_ADAPTATION_GUIDE.md` explains downstream use without raw source bulk copy or sensitive values |
| base governance templates | PRESENT | `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS` templates exist |
| scenario simulator treatment | DOWNSTREAM CANDIDATE | No dedicated profile or example was created |

## Next Recommended Step

Decide whether to draft a GitHub Release page, whether to run additional downstream application experiments using the strengthened base template, and when a formal `v0.1.0` tag would be appropriate. Actual project application remains deferred.
