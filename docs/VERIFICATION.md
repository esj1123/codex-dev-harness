# VERIFICATION.md

## Purpose

Define verification expectations for this template repository.

## Current Verification Checklist

- Requested files exist.
- README and AGENTS read order match.
- Historical P0 docs-only scope is described as completed baseline.
- Render script exists and supports dry-run rendering.
- Quality gate implementation exists.
- Required root documents exist.
- Base templates exist.
- Profile templates exist.
- Example skeletons exist.
- Example skeletons include profile safety policy files.
- PLC/device example explicitly prohibits live device write and equipment detail exposure.
- No real application code exists.
- No real PLC/device code exists.
- No secrets or private data are included.

## Local Verification Flow

Recommended local command:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

The wrapper runs tests, quality gate, and all three example render dry-runs. It does not write rendered files and does not use `--force`.

## Manual Verification Flow

Run:

`python -m pip install -r requirements-dev.txt`

`python -m pytest`

`python scripts/quality_gate.py`

The quality gate includes:
- Documentation presence.
- Repository hygiene.
- Template config/schema validation.
- Secret/private-pattern scan.
- Example skeleton validation.
- Example config validation.

## Render Dry-Run Checks

Run:

- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

## Historical P0 Verification

P0 used policy-level verification only. At that time, render scripts, quality gates, and examples were intentionally absent. That is historical context, not the current state.

## Verification Mesh

Current and future verification layers may include:
- Unit tests.
- Smoke tests.
- Runtime trace.
- Acceptance trace.
- Policy validation.
- Example validation.
- Audit evidence.

## Release Readiness

Use `docs/RELEASE_CHECKLIST.md` before tagging a reusable baseline. Known gaps and intentionally unsupported behavior are tracked in `docs/KNOWN_LIMITATIONS.md`.

Local package boundaries are documented in `docs/LOCAL_RELEASE_PACKAGE.md`.

CI policy is documented in `docs/CI_POLICY.md`. The current baseline is local verification first and does not include a GitHub Actions workflow.

## NOT RUN Principle

If a check was not executed, mark it as NOT RUN with a reason. Do not imply success for checks that were not run.
