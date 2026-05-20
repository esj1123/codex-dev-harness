# CI_POLICY.md

## Purpose

Define the current CI policy for codex-dev-harness without creating a GitHub Actions workflow.

## Current Policy

Local verification first.

The repository is not currently configured with CI. Release readiness is verified locally with documented commands and recorded closeout evidence.

## Future Optional CI

GitHub Actions may be added in a future phase, but it is optional. If CI is introduced, it should only run repository validation checks:

- `python -m pytest`
- `python scripts/quality_gate.py`
- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

## CI Boundaries

CI must not introduce:

- Real application code.
- Real PLC/device code.
- Live target writes.
- Device start, stop, reset, or mode-change actions.
- Secret or live config generation.
- New profiles without a separate design and validation step.

## Release Relationship

CI is not required before a documentation-level release tag. A release tag should still record local verification evidence and known limitations.
