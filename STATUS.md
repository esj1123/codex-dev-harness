# STATUS.md

## Current Phase

P5.5 Local Usage Readiness.

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

Verified commit: `90d52099259dd56edf429a5d17753fdae0f618b9`

| check | status | evidence |
|---|---|---|
| `python -m pytest` | PASS | 16 passed |
| `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, secret scan passed |
| python_cli render dry-run | PASS | `examples/python_cli_minimal` dry-run succeeded |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal` dry-run succeeded |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal` dry-run succeeded |
| CI workflow | NOT RUN | Not included in this repository baseline |
| release tag | NOT CREATED | P6 release tag decision remains pending |

## Next Recommended Step

P6 release tag decision. Decide whether to tag the local-first baseline, and whether CI should remain policy-only or move to a future optional workflow.
