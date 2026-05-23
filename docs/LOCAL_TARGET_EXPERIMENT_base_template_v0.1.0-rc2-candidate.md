# LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md

## Purpose

Record a local target experiment for the extended base template after source index, project boundary, data scope, phase plan, and approvals were added to the base template.

This is a generic/base template experiment. It does not create a scenario simulator profile or any downstream application profile.

## Basis

- Repository: `esj1123/codex-dev-harness`
- Main commit tested: `c92f98097905846915719d13ee140f699e441d2f`
- Existing tag retained: `v0.1.0-rc1`
- Existing tag target retained: `10bccadd15be9401847620eba61d3c8c4117962d`
- New tag created: none
- Profile: none
- Target folder: separate local temporary target folder

## Pre-Render Verification

| command | result | notes |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest 17 passed, quality gate passed, render dry-run 3 variants passed |
| `python scripts/quality_gate.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed in this Codex desktop shell |
| local Python runtime `scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |

## Target Config

The target used a seed project config with no profile selected.

The config kept live target write prohibited and used placeholder-only local data policy. No private input, secret, or live configuration was added.

## Dry-Run Result

Dry-run succeeded and planned 11 base Markdown outputs:

- `ACCEPTANCE_TRACE.md`
- `AGENTS.md`
- `APPROVALS.md`
- `DATA_SCOPE.md`
- `MVP.md`
- `PHASE_PLAN.md`
- `PRODUCT.md`
- `PROJECT_BOUNDARY.md`
- `README.md`
- `SOURCE_INDEX.md`
- `STATUS.md`

## Actual Render Result

Actual render was executed after dry-run review.

Generated Markdown files:

- `ACCEPTANCE_TRACE.md`
- `AGENTS.md`
- `APPROVALS.md`
- `DATA_SCOPE.md`
- `MVP.md`
- `PHASE_PLAN.md`
- `PRODUCT.md`
- `PROJECT_BOUNDARY.md`
- `README.md`
- `SOURCE_INDEX.md`
- `STATUS.md`

The target folder also contained the manually prepared `template.config.yml`.

An initial unprivileged render attempt was blocked by local file permission. The approved render command then succeeded.

## Required Extended Base Docs

| file | status |
|---|---|
| `SOURCE_INDEX.md` | GENERATED |
| `PROJECT_BOUNDARY.md` | GENERATED |
| `DATA_SCOPE.md` | GENERATED |
| `PHASE_PLAN.md` | GENERATED |
| `APPROVALS.md` | GENERATED |

## Scope Confirmation

| check | result | notes |
|---|---|---|
| real application code | ABSENT | No runtime source generated |
| C# source/solution/project | ABSENT | No C# runtime artifacts generated |
| PLC/device code | ABSENT | No device runtime artifacts generated |
| live target write support | ABSENT | No live write implementation generated |
| secret/private/live config | ABSENT | No private values or live config generated |
| scenario simulator profile | ABSENT | No profile or example created |
| GitHub Actions workflow | ABSENT | No workflow created |
| release tag | NOT CREATED | No `v0.1.0-rc2` or formal `v0.1.0` tag created |

## Conclusion

The extended base template is usable for a generic local target without selecting a profile. The base template produced the expected governance documents, including source index, project boundary, data scope, phase plan, and approvals, without generating runtime or live-write artifacts.

