# Clean Clone Validation v0.1.0-rc1

## Validation Purpose

Validate that the already-created annotated tag `v0.1.0-rc1` can be checked out in a separate clean clone and verified with the local-first verification wrapper.

## Tag

- Tag name: `v0.1.0-rc1`
- Tag object: `9ca08efbd43cd2c5defba7875efbd7ca702c6166`
- Tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`

## Clean Clone

- Clean clone run: YES
- Clone folder: separate temporary clone outside the working copy
- Checkout ref: `v0.1.0-rc1`
- Checkout mode: detached HEAD
- Checked out commit: `10bccadd15be9401847620eba61d3c8c4117962d`

## Commands Run

| command | result | evidence |
|---|---|---|
| `git clone https://github.com/esj1123/codex-dev-harness.git _tmp_codex_dev_harness_clean_clone_rc1` | PASS | Repository cloned into a separate temporary folder |
| `git checkout v0.1.0-rc1` | PASS | Detached HEAD at `10bccadd15be9401847620eba61d3c8c4117962d` |
| `git rev-list -n 1 v0.1.0-rc1` | PASS | Returned `10bccadd15be9401847620eba61d3c8c4117962d` |
| `python -m pip install -r requirements-dev.txt` | ENVIRONMENT BLOCKED | Bare `python.exe` launcher failed in this Codex desktop shell with a Windows logon session error |
| local Python runtime pip install | PASS | `pytest` was already satisfied in the local Python runtime used by `scripts/run_local_verify.ps1` |
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | Local verification completed |

## Result Table

| check | result | evidence |
|---|---|---|
| pytest | PASS | 16 passed |
| quality_gate | PASS | docs, hygiene, schema, examples, and secret scan passed |
| python_cli render dry-run | PASS | `examples/python_cli_minimal` dry-run passed |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal` dry-run passed |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal` dry-run passed |
| `.github/workflows` absence | PASS | No `.github/workflows` directory was present |
| application code absence | PASS | No real application source tree was present; only template scripts and tests exist |
| PLC/device code absence | PASS | PLC/device content remains documentation-only and skeleton-only |
| live target write support absence | PASS | No live target write support was added |

## Scope Confirmation

- No GitHub Actions workflow installed.
- No GitHub Release page created.
- No formal `v0.1.0` tag created.
- No application code added.
- No PLC/device code added.
- No live target write support added.
- The existing `v0.1.0-rc1` tag was not moved, deleted, or recreated.

## Conclusion

`v0.1.0-rc1` is locally verifiable from a clean clone through the repository local verification wrapper.

The only caveat is environment-specific: the bare `python` launcher is unavailable in this Codex desktop shell, so dependency confirmation was performed with the local Python runtime that the wrapper resolves and uses.
