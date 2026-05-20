# LOCAL_RELEASE_PACKAGE.md

## Purpose

Define what belongs in a local-first release package for codex-dev-harness.

## Include

A local usage package should include:
- root docs
- `docs/`
- `templates/`
- `profiles/`
- `scripts/`
- `examples/`
- `tests/`
- `requirements-dev.txt`
- `template.config.example.yml`

## Exclude

A local usage package should exclude:
- `.git/`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- private input
- generated target output
- live config
- secrets, keys, tokens, or credentials

## Boundary

The local package does not include:
- live target write behavior
- PLC/device code
- actual application code
- equipment IP, port, tag, address, or live parameter details
- GitHub Actions workflow files
- release tags

The package is a reusable documentation, template, verification, and dry-run render baseline.
