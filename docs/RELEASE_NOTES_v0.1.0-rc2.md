# Release Notes v0.1.0-rc2

## Summary

`v0.1.0-rc2` is the recommended second release candidate for the local-first codex-dev-harness baseline.

This candidate builds on `v0.1.0-rc1` by strengthening the generic base template and proving that the extended base template can be rendered into a separate local target without selecting a profile.

## Changes Since rc1

- Extended base templates:
  - `SOURCE_INDEX.md`
  - `PROJECT_BOUNDARY.md`
  - `DATA_SCOPE.md`
  - `PHASE_PLAN.md`
  - `APPROVALS.md`
- Regression example synchronization:
  - `examples/python_cli_minimal`
  - `examples/csharp_desktop_minimal`
  - `examples/plc_tool_minimal`
- `example_render_drift_gate` added to check that regression examples contain expected rendered files.
- Generic/base template local target experiment documented in `docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md`.

## Included Scope

- Local-first documentation baseline.
- Base template governance documents.
- Existing profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`.
- Regression examples for existing profiles.
- Render dry-run and local actual-render evidence for a generic base target.
- Quality gates, tests, and release candidate documentation.

## Excluded Scope

- `v0.1.0-rc2` tag creation.
- Formal `v0.1.0` tag creation.
- GitHub Release page creation.
- GitHub Actions workflow installation.
- New scenario simulator profile or example.
- Real application code.
- C# source, solution, or project files.
- PLC/device code.
- Live target write support.
- Secrets, private input, live configuration, or equipment connection details.

## Verification Commands

Run from the repository root:

- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`
- local Python runtime `scripts/quality_gate.py`

The local verification wrapper runs tests, the quality gate, and the three regression example render dry-runs. It does not write rendered files and does not use `--force`.

## Known Limitations

Known limitations are tracked in `docs/KNOWN_LIMITATIONS.md`.

Current limitations remain:
- YAML parsing is intentionally scalar-only.
- Regression examples are skeletons only.
- Render drift checking is file-presence only and does not compare rendered content.
- GitHub Actions remain optional and are not installed.
- Real runtime implementation remains downstream work.

## Recommended Tag

Recommended tag after final local verification: `v0.1.0-rc2`.

The `v0.1.0-rc2` tag has not been created by this document.

