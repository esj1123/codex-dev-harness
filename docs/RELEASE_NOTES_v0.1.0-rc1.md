# Release Notes v0.1.0-rc1

## Summary

`v0.1.0-rc1` is the recommended first release candidate for the local-first codex-dev-harness baseline.

This release candidate is intended for users who want to clone the repository, verify it locally, dry-run template rendering, and then adapt the generated documentation to a separate target project.

## Local-First Baseline Scope

Included in scope:
- governed development repo documentation
- base template files
- profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`
- render script with dry-run support
- quality gate runner and gate modules
- example skeletons for template validation
- local verification wrapper
- release readiness and local usage documentation

Excluded from scope:
- release tag creation
- GitHub Actions workflow installation
- real application code
- real PLC/device code
- live target write support
- secrets, private inputs, live config, or equipment details
- automatic application to an external project

## Verification Commands

Run from the repository root:

- `python -m pip install -r requirements-dev.txt`
- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`
- `python -m pytest`
- `python scripts/quality_gate.py`

The local verification wrapper runs tests, the quality gate, and the three example render dry-runs. It does not write rendered files and does not use `--force`.

## Known Limitations

Known limitations are tracked in `docs/KNOWN_LIMITATIONS.md`.

## Recommended Tag

Recommended tag after final local verification: `v0.1.0-rc1`.

The tag has not been created by this document.
