# GitHub Release Draft v0.1.0

## Title

v0.1.0 - Local-first codex-dev-harness baseline

## Target

- Target tag: `v0.1.0`
- Tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`
- Tag target: `43bbf001e1d2770466b41d5b8366f289b972a00b`
- GitHub Release page: NOT CREATED

## Summary

`v0.1.0` is the formal local-first governed template baseline for codex-dev-harness.

This release includes extended base templates, synchronized regression examples, the `example_render_drift_gate`, a completed generic/base downstream experiment, and completed formal clean clone validation.

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
- Release records.
- Clean clone validations.
- Downstream experiment record.

## Not Included

- GitHub Actions workflow.
- Real application code.
- C# source, solution, or project files.
- PLC/device code.
- Live target write support.
- Scenario simulator profile/example.
- IFF/N3G raw source or sensitive values.

## Verification

| check | result | evidence |
|---|---|---|
| `v0.1.0` clean clone validation | PASS | `docs/CLEAN_CLONE_VALIDATION_v0.1.0.md` |
| `scripts/run_local_verify.ps1` | PASS | Local wrapper passed |
| pytest | PASS | 17 passed |
| quality_gate | PASS | All gates passed |
| render dry-run 3 variants | PASS | Python CLI, C# desktop, and PLC/device examples passed |
| example_render_drift_gate | PASS | Expected rendered example files present |
| secret_scan_gate | PASS | No obvious secret/private patterns found |

## Known Limitations

Known limitations are tracked in `docs/KNOWN_LIMITATIONS.md`.

Important current limits:
- Examples are skeletons only.
- Render drift checking is file-presence only.
- GitHub Actions are optional and not installed.
- Real runtime implementation remains downstream work.

## Recommended Next

- Start local downstream adoption from `v0.1.0`.
- Decide whether to publish a GitHub Release page from this draft.
- Consider future eval, release manifest, SBOM, and provenance work.
