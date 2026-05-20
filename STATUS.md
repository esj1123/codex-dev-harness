# STATUS.md

## Current Phase

P6 Release Candidate Closeout.

## Current State

The repository contains documentation, base templates, profile templates, render tooling, quality gates, tests, and minimal example skeletons.

## What Exists

- Core repo contract documents.
- Safety and verification policy documents.
- Release readiness documents:
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/KNOWN_LIMITATIONS.md`
  - `docs/CI_POLICY.md`
  - `docs/LOCAL_USAGE.md`
  - `docs/LOCAL_RELEASE_PACKAGE.md`
  - `docs/P6_RELEASE_CLOSEOUT.md`
  - `docs/RELEASE_NOTES_v0.1.0-rc1.md`
  - `docs/OPTIONAL_GITHUB_ACTIONS.md`
- Base markdown templates.
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
- Release tag.

## Known Constraints

- YAML parsing is intentionally scalar-only.
- Examples are skeletons only.
- Runtime checks in examples may be marked NOT RUN when code or scripts do not exist.
- Render targets inside this repository are limited to `examples/<name>`.

## Latest Verification

Verified commit: `aff39d65e716ad2830647fcf52026c00a911d482`

| check | status | evidence |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and 3 render dry-runs passed |
| `python -m pytest` | PASS | 16 passed through the local Python runtime used by the verification wrapper |
| `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, secret scan passed through the local Python runtime |
| python_cli render dry-run | PASS | `examples/python_cli_minimal` dry-run succeeded |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal` dry-run succeeded |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal` dry-run succeeded |
| CI workflow | NOT RUN | Not included in this repository baseline |
| release tag | NOT CREATED | P6 release tag decision remains pending |
| release notes | PRESENT | `docs/RELEASE_NOTES_v0.1.0-rc1.md` exists |
| optional GitHub Actions guide | PRESENT | guide and template exist, but no workflow is installed |

## Next Recommended Step

Reverify the latest commit, then make the `v0.1.0-rc1` tag decision. GitHub Actions remains optional and is represented only by documentation plus a template file.
