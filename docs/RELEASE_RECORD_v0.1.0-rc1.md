# Release Record v0.1.0-rc1

## Tag

- Tag name: `v0.1.0-rc1`
- Tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`
- Tag object: `9ca08efbd43cd2c5defba7875efbd7ca702c6166`

## Local Verification Result

| check | result | evidence |
|---|---|---|
| `scripts/run_local_verify.ps1` | PASS | Local verification wrapper completed successfully |
| pytest | PASS | 16 passed |
| quality_gate | PASS | docs, hygiene, schema, examples, and secret scan passed |
| render dry-run 3 profiles | PASS | `python_cli_minimal`, `csharp_desktop_minimal`, and `plc_tool_minimal` dry-runs passed |

## Release State

- GitHub Actions workflow: NOT INSTALLED
- GitHub Release page: NOT CREATED
- Formal `v0.1.0`: NOT CREATED

## Scope

This tag records the local-first baseline for codex-dev-harness.

Included scope:
- local-first baseline
- governed documentation and templates
- local verification wrapper
- quality gate and render dry-run validation

Excluded scope:
- real application code
- PLC/device code
- live target write support
- live config, secrets, private input, or equipment details
- GitHub Actions workflow installation
- GitHub Release page creation

## Notes

This record documents an already-created tag. It does not move, recreate, or modify the tag.
