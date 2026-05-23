# Local Downstream Adoption Run v0.1.0

## Purpose

Record the first local downstream adoption run using the formal `v0.1.0` codex-dev-harness baseline. This run applies the base template only to a separate local scenario simulator design baseline target.

## Baseline

- Basis tag: `v0.1.0`
- Tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`
- Tag target commit: `43bbf001e1d2770466b41d5b8366f289b972a00b`
- Source checkout: clean clone or verified clean clone checkout at `v0.1.0`
- Source verification: PASS

## Target

- Target type: scenario simulator design baseline
- Target folder: `<local-downstream-target>/iff_scenario_simulator_design_baseline`
- Project name: `iff_scenario_simulator_design_baseline`
- Project status: `seed`
- Profile: none
- Template mode: base template only

## Source Handling Rules

- Source-index driven.
- No raw source bulk copy.
- No sensitive values.
- No IP, port, tag, or live parameter values.
- No runtime implementation code.
- No C# source, solution, or project files.
- No PLC/device code.
- No live target write support.

## Source Repo Verification

| check | result | evidence |
|---|---|---|
| checkout ref | PASS | `v0.1.0` |
| tag target | PASS | `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest 17 passed, quality gate passed, and 3 regression render dry-runs passed |

## Dry-Run Result

Dry-run was executed before actual render. It planned 11 base Markdown outputs and no profile templates:

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

Result: PASS.

## Actual Render Result

| item | result | notes |
|---|---|---|
| initial non-elevated write attempt | BLOCKED | Sandbox denied target file write before any Markdown output was created |
| approved actual render | PASS | 11 base Markdown docs generated |
| `--force` usage | NOT USED | No overwrite mode was used |
| profile templates | NOT USED | No profile selected |
| downstream repository creation | NOT DONE | Separate local target folder only |

## Generated Files Summary

| file | result |
|---|---|
| `SOURCE_INDEX.md` | GENERATED |
| `PROJECT_BOUNDARY.md` | GENERATED |
| `DATA_SCOPE.md` | GENERATED |
| `PHASE_PLAN.md` | GENERATED |
| `APPROVALS.md` | GENERATED |
| `AGENTS.md` | GENERATED |
| `PRODUCT.md` | GENERATED |
| `MVP.md` | GENERATED |
| `STATUS.md` | GENERATED |
| `ACCEPTANCE_TRACE.md` | GENERATED |
| `README.md` | GENERATED |

The local target folder also contained a hidden/system zero-byte placeholder file created by the local environment before render. It was not produced by `render_template.py` and is not counted as generated adoption output.

## Safety Checks

| check | result | notes |
|---|---|---|
| `.github/workflows` | ABSENT | No workflow created |
| `profiles/scenario_simulator` | ABSENT | No profile created |
| `examples/scenario_simulator_minimal` | ABSENT | No example created |
| application code | ABSENT | No runtime implementation generated |
| C# source/solution/project | ABSENT | No C# artifact generated |
| PLC/device code | ABSENT | No device artifact generated |
| live target write support | ABSENT | No live-write support generated |
| secret/private/live config | ABSENT | Config contains only non-sensitive policy values |
| IFF/N3G raw source or sensitive values | ABSENT | No raw source or sensitive operational values recorded |

## Conclusion

Usable. The `v0.1.0` base template can be applied to a separate local scenario simulator design baseline target without creating a profile, repository example, runtime implementation, C# project, PLC/device artifact, or live-write support.

## Next Action

- Review generated docs in the downstream target manually.
- Fill `SOURCE_INDEX.md` with sanitized source summaries only.
- Keep raw source, sensitive values, IP, port, tag, live parameter, and private input out of the target repository.
- Start actual implementation only after a separate phase approval.
