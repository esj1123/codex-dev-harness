# RELEASE_CHECKLIST.md

## Purpose

Define the release readiness checks for a reusable codex-dev-harness baseline.

## Required Checks

- Root documentation is phase-aligned.
- `requirements-dev.txt` exists and includes test dependencies.
- `python -m pytest` passes in a prepared development environment.
- `python scripts/quality_gate.py` passes.
- Dry-run render succeeds for:
  - `examples/python_cli_minimal`
  - `examples/csharp_desktop_minimal`
  - `examples/plc_tool_minimal`
- Example config validation passes.
- Example skeletons contain no real application code.
- PLC/device example contains no real device code and no live target details.
- Secret/private-pattern scan passes.

## Release Boundary

Release readiness does not require:
- Real application implementation.
- Real PLC/device implementation.
- CI workflow creation.
- Live target write support.
- Publishing automation.

## Closeout Evidence

Before tagging a release, record:
- Commit SHA.
- Commands run.
- Verification results.
- NOT RUN items and reasons.
- Known limitations.
