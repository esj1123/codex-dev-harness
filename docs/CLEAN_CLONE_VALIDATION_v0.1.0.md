# Clean Clone Validation v0.1.0

## Purpose

Validate that the formal annotated tag `v0.1.0` can be checked out and verified from a clean local clone.

## Tag

- Tag name: `v0.1.0`
- Tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`
- Tag target commit: `43bbf001e1d2770466b41d5b8366f289b972a00b`
- Checkout ref: `v0.1.0`
- Clean clone: YES

## Commands Run

| command | result | notes |
|---|---|---|
| `git clone https://github.com/esj1123/codex-dev-harness.git` | PASS | Separate temporary clone was created |
| `git checkout v0.1.0` | PASS | Checkout required elevated filesystem permission in this sandbox; tag target matched expected commit |
| `python -m pip install -r requirements-dev.txt` | ENVIRONMENT BLOCKED | Bare `python.exe` failed in this Codex desktop shell with a logon-session error |
| local Python runtime `-m pip install -r requirements-dev.txt` | PASS | `pytest` and dependencies were already satisfied in the wrapper runtime |
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and 3 render dry-runs passed |

## Result Table

| check | result | evidence |
|---|---|---|
| tag object | PASS | `a5aed964f381fecdeff54d6c94a068ae21d1dcf9` |
| tag target commit | PASS | `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| pytest | PASS | 17 passed |
| quality_gate | PASS | Documentation, hygiene, schema, examples, render drift, and secret scan passed |
| render dry-run 3 variants | PASS | `python_cli_minimal`, `csharp_desktop_minimal`, and `plc_tool_minimal` dry-runs passed |
| `example_render_drift_gate` | PASS | Expected rendered example files present: 48 |
| `secret_scan_gate` | PASS | No obvious secret/private patterns found |
| `.github/workflows` absence | PASS | No workflow directory exists |

## Scope Confirmation

- No GitHub Release page was created.
- No GitHub Actions workflow was installed.
- No new profile was created.
- No `profiles/scenario_simulator` was created.
- No `examples/scenario_simulator_minimal` was created.
- No real application code was added.
- No C# source, solution, or project files were added.
- No PLC/device code was added.
- No live target write support was added.
- No IFF/N3G raw source or sensitive values were recorded.

## Conclusion

`v0.1.0` is locally verifiable from a clean clone through the local verification wrapper. Bare `python.exe` dependency installation is environment-blocked in this Codex desktop shell, so the dependency check was also validated through the wrapper's local Python runtime.
