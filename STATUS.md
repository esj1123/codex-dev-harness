# STATUS.md

## Current Phase

P4/P5 validation patch phase.

## Current State

The repository contains documentation, base templates, profile templates, render tooling, quality gates, tests, and minimal example skeletons.

## What Exists

- Core repo contract documents.
- Safety and verification policy documents.
- Release readiness documents:
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/KNOWN_LIMITATIONS.md`
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

## What Does Not Exist Yet

- Real application code.
- Real PLC/device code.
- Live target write behavior.
- Real secret/config files.
- CI workflow.
- Release automation.

## Known Constraints

- YAML parsing is intentionally scalar-only.
- Examples are skeletons only.
- Runtime checks in examples may be marked NOT RUN when code or scripts do not exist.
- Render targets inside this repository are limited to `examples/<name>`.

## Next Recommended Step

Run the P5 release readiness checklist in a prepared development environment, then decide whether to document CI policy in `docs/CI_POLICY.md` before adding any workflow.
