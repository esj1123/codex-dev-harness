# GitHub Release Draft v0.1.0-rc2

## Title

v0.1.0-rc2 - Local-first codex-dev-harness release candidate

## Target

- Target tag: `v0.1.0-rc2`
- Tag object: `569b992b390a672cd8a321963a963ff0cbe47976`
- Tag target: `67ead73628c8ff7b15e91d2ba608efbdbb8de81e`
- GitHub Release page: NOT CREATED

## Summary

`v0.1.0-rc2` is a local-first governed template release candidate for codex-dev-harness.

This candidate includes extended base templates, synchronized regression examples, the `example_render_drift_gate`, a completed generic/base local target experiment, and completed clean clone validation.

## Included

- Base templates.
- Existing profile templates:
  - `python_cli`
  - `csharp_desktop`
  - `plc_or_device_tool`
- Regression examples:
  - `examples/python_cli_minimal`
  - `examples/csharp_desktop_minimal`
  - `examples/plc_tool_minimal`
- Render script.
- Quality gate.
- Local verification wrapper.
- Release notes.
- Release records.
- Clean clone validation records.

## Not Included

- Formal `v0.1.0`.
- GitHub Actions workflow.
- GitHub Release publication.
- Scenario simulator profile/example.
- Real application code.
- C# source, solution, or project files.
- PLC/device code.
- Live target write support.
- IFF/N3G source content or sensitive values.

## Verification

| check | result | evidence |
|---|---|---|
| `scripts/run_local_verify.ps1` | PASS | Local wrapper passed |
| pytest | PASS | 17 passed |
| quality_gate | PASS | All gates passed |
| render dry-run 3 variants | PASS | Python CLI, C# desktop, and PLC/device examples passed |
| example_render_drift_gate | PASS | Expected rendered example files present |
| clean clone validation | PASS | `v0.1.0-rc2` verified from a separate clean clone |

## Known Limitations

Known limitations are tracked in `docs/KNOWN_LIMITATIONS.md`.

Important current limits:
- Examples are skeletons only.
- Render drift checking is file-presence only.
- GitHub Actions are optional and not installed.
- Real runtime implementation remains downstream work.

## Recommended Next

- Decide whether to run a downstream application experiment.
- Review formal `v0.1.0` criteria.
- Decide whether to publish a GitHub Release page from this draft without changing tags.

