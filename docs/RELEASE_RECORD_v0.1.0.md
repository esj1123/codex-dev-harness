# Release Record v0.1.0

## Purpose

Record the post-tag state for the formal `v0.1.0` local-first codex-dev-harness baseline.

## Tag

- Tag name: `v0.1.0`
- Tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`
- Tag target commit: `43bbf001e1d2770466b41d5b8366f289b972a00b`
- Tag type: annotated

## Pre-Tag Verification Result

| check | result | evidence |
|---|---|---|
| `run_local_verify.ps1` | PASS | Local verification wrapper completed |
| pytest | PASS | 17 passed |
| quality_gate | PASS | Documentation, hygiene, schema, examples, render drift, and secret scan passed |
| render dry-run 3 variants | PASS | `python_cli_minimal`, `csharp_desktop_minimal`, and `plc_tool_minimal` dry-runs passed |
| `example_render_drift_gate` | PASS | Expected rendered example files present |
| `secret_scan_gate` | PASS | No obvious secret/private patterns found |
| rc2 clean clone validation | PASS | `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md` |
| downstream base-template experiment | PASS | `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md` |

## Release State

| item | state |
|---|---|
| GitHub Actions workflow | NOT INSTALLED |
| GitHub Release page | NOT CREATED |
| Formal `v0.1.0` tag | CREATED |

## Scope

- Local-first governed template.
- Extended base templates.
- Regression examples synchronized.
- Render drift gate included.
- Generic/base downstream experiment documented.
- Scenario simulator tested as downstream candidate, not profile.

## Scope Exclusions

- No real application code.
- No C# source, solution, or project files.
- No PLC/device code.
- No live target write support.
- No `scenario_simulator` profile.
- No `examples/scenario_simulator_minimal`.
- No IFF/N3G raw source or sensitive values.

## Conclusion

`v0.1.0` is the formal local-first baseline tag for codex-dev-harness. GitHub Release publication remains a separate decision.
