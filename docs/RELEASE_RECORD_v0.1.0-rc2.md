# Release Record v0.1.0-rc2

## Tag

- Tag name: `v0.1.0-rc2`
- Tag object: `569b992b390a672cd8a321963a963ff0cbe47976`
- Tag target commit: `67ead73628c8ff7b15e91d2ba608efbdbb8de81e`
- Tag type: annotated
- Tag pushed to remote: YES

## Previous Release Candidate

- Previous tag: `v0.1.0-rc1`
- Previous tag object: `9ca08efbd43cd2c5defba7875efbd7ca702c6166`
- Previous tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`
- Previous tag moved or recreated: NO

## Pre-Tag Verification Result

| check | result | evidence |
|---|---|---|
| target commit | PASS | `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and render dry-runs passed |
| pytest | PASS | 17 passed |
| quality_gate | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| render dry-run 3 variants | PASS | `python_cli_minimal`, `csharp_desktop_minimal`, and `plc_tool_minimal` passed |
| example_render_drift_gate | PASS | expected rendered example files present: 48 |
| secret_scan_gate | PASS | no obvious secret/private patterns found |

## Release Scope

- Local-first governed template baseline.
- Extended base templates included.
- Regression examples synchronized.
- Example render drift gate included.
- Generic/base local target experiment documented.

## Out Of Scope

- GitHub Actions workflow: NOT INSTALLED.
- GitHub Release page: NOT CREATED.
- Formal `v0.1.0`: NOT CREATED.
- Scenario simulator profile/example: NOT CREATED.
- Real application code: NOT CREATED.
- C# source/solution/project: NOT CREATED.
- PLC/device code: NOT CREATED.
- Live target write support: NOT CREATED.

## Conclusion

`v0.1.0-rc2` was created as an annotated tag at `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` after local pre-tag verification passed.

