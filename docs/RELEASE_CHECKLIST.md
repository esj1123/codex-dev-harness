# RELEASE_CHECKLIST.md

## Purpose

Define the release readiness checks for a reusable codex-dev-harness baseline.

## Required Checks

- Root documentation is phase-aligned.
- `requirements-dev.txt` exists and includes test dependencies.
- `python -m pytest` passes in a prepared development environment.
- `python scripts/quality_gate.py` passes all eight core gates.
- `python scripts/generate_checksums.py --verify` passes for the tracked release
  evidence bundle. This confirms bundle integrity only; valid ancestor evidence
  remains `VALID ANCESTOR / REFRESH REQUIRED` until it is separately regenerated
  from the exact clean release source basis.
- `python scripts/release_evidence_preflight.py --repo-root . --dry-run --json`
  reports schema version `2`. Treat deprecated `readiness` only as an alias of
  `refresh_readiness`; release claims require `release_readiness=READY` and no
  disallowed overall blocker.
- Dry-run render succeeds for:
  - `examples/python_cli_minimal`
  - `examples/csharp_desktop_minimal`
  - `examples/plc_tool_minimal`
- Example config validation passes.
- Example skeletons contain no real application code.
- PLC/device example contains no real device code and no live target details.
- Secret/private-pattern scan passes.
- A GitHub manual-export bundle must declare hosted provenance truthfully,
  return through the exact run ID and artifact name, pass local isolated
  validation, and be committed locally before it may be described as current.

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
