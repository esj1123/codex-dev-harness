# Clean Clone Validation v0.1.0-rc2

## Purpose

Validate that the annotated tag `v0.1.0-rc2` can be checked out and verified from a separate clean local clone.

## Tag

- Tag name: `v0.1.0-rc2`
- Tag object: `569b992b390a672cd8a321963a963ff0cbe47976`
- Tag target commit: `67ead73628c8ff7b15e91d2ba608efbdbb8de81e`
- Checkout ref: `v0.1.0-rc2`
- Clean clone: YES

## Commands Run

| command | result | notes |
|---|---|---|
| `git clone` | PASS | Separate temporary local clone created |
| `git checkout v0.1.0-rc2` | PASS | Detached HEAD at `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| `python -m pip install -r requirements-dev.txt` | ENVIRONMENT BLOCKED | Bare `python.exe` failed in this Codex desktop shell |
| local Python runtime `-m pip install -r requirements-dev.txt` | PASS | `pytest` already satisfied |
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and render dry-runs passed |

## Result Table

| check | result | evidence |
|---|---|---|
| tag target | PASS | `v0.1.0-rc2` resolves to `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| pytest | PASS | 17 passed |
| quality_gate | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| render dry-run 3 variants | PASS | `python_cli_minimal`, `csharp_desktop_minimal`, and `plc_tool_minimal` passed |
| example_render_drift_gate | PASS | expected rendered example files present: 48 |
| secret_scan_gate | PASS | no obvious secret/private patterns found |
| `.github/workflows` absence | PASS | No workflow directory exists |

## Scope Confirmation

- No GitHub Actions workflow installed.
- No GitHub Release page created.
- No formal `v0.1.0` tag created.
- No scenario simulator profile created.
- No scenario simulator example created.
- No real application code added.
- No C# source, solution, or project files added.
- No PLC/device code added.
- No live target write support added.

## Conclusion

`v0.1.0-rc2` is locally verifiable from a clean clone.

The only blocked command was bare `python -m pip install -r requirements-dev.txt`, caused by the local Codex desktop shell's `python.exe` launch environment. The wrapper's local Python runtime dependency check and full verification passed.

