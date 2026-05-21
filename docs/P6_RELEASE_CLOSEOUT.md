# P6 Release Closeout

## Purpose

This document records the P6 release candidate closeout state for the local-first Agentic Development Repo Template baseline.

## Candidate

- Historical pre-tag candidate commit: `aff39d65e716ad2830647fcf52026c00a911d482`
- Final tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`
- Tag name: `v0.1.0-rc1`
- Tag object: `9ca08efbd43cd2c5defba7875efbd7ca702c6166`
- Release tag: CREATED
- GitHub Release page: NOT CREATED
- CI workflow: NOT INSTALLED

## Local Verification

| check | result | evidence |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and 3 render dry-runs passed |
| `python -m pytest` | PASS | 16 passed through the local Python runtime used by the verification wrapper |
| `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, secret scan passed through the local Python runtime |
| python_cli render dry-run | PASS | `examples/python_cli_minimal/template.config.yml` rendered in dry-run mode |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal/template.config.yml` rendered in dry-run mode |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal/template.config.yml` rendered in dry-run mode |

## Release References

- Known limitations: `docs/KNOWN_LIMITATIONS.md`
- Release checklist: `docs/RELEASE_CHECKLIST.md`
- Release notes: `docs/RELEASE_NOTES_v0.1.0-rc1.md`
- Release record: `docs/RELEASE_RECORD_v0.1.0-rc1.md`
- Clean clone validation record: `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md`
- Optional GitHub Actions guide: `docs/OPTIONAL_GITHUB_ACTIONS.md`
- Local usage guide: `docs/LOCAL_USAGE.md`
- Local package boundary: `docs/LOCAL_RELEASE_PACKAGE.md`

## Remaining Decisions

- Clean clone validation from the `v0.1.0-rc1` tag: COMPLETED.
- Decide whether to draft a GitHub Release page without changing the tag.
- Decide whether to run a small local target project application experiment.
- Decide when a formal `v0.1.0` tag would be appropriate.

## Scope Confirmation

- Release tag `v0.1.0-rc1` was created.
- No GitHub Release page was created.
- No GitHub Actions workflow was installed.
- Clean clone validation was documented.
- No new profile was added.
- No real application code was added.
- No PLC/device code was added.
- No live target write support was added.
- Render target guards were not relaxed.
