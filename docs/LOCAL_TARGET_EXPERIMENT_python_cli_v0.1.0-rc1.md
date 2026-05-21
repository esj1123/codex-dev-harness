# Local Target Experiment python_cli v0.1.0-rc1

## Purpose

Record a small local target project experiment using the `python_cli` profile from the already-created `v0.1.0-rc1` tag.

## Baseline

- Basis tag: `v0.1.0-rc1`
- Tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`
- Profile: `python_cli`
- Source checkout: clean clone checked out at `v0.1.0-rc1`
- Target folder: separate temporary local target folder

## Pre-Render Verification

| check | result | evidence |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and example render dry-runs passed |
| pytest | PASS | 16 passed |
| quality_gate | PASS | docs, hygiene, schema, examples, and secret scan passed |

## Target Config

The target used a local `template.config.yml` with:
- `project.name: local_python_cli_trial`
- `project.status: seed`
- `profile.name: python_cli`
- `safety.private_input_policy: synthetic_fixtures_only`
- `safety.live_target_write: forbidden`

No private input, secret, live config, or equipment detail was used.

## Dry-Run Result

Dry-run command:

`python scripts/render_template.py --config <target>/template.config.yml --target <target> --dry-run`

Result: PASS.

Dry-run planned 11 Markdown outputs:
- `ACCEPTANCE_TRACE.md`
- `AGENTS.md`
- `MVP.md`
- `PRODUCT.md`
- `README.md`
- `STATUS.md`
- `AGENTS.override.md`
- `README.profile.md`
- `SAFETY_POLICY.profile.md`
- `STATUS.profile.md`
- `VERIFICATION.profile.md`

## Actual Render Result

Actual render command:

`python scripts/render_template.py --config <target>/template.config.yml --target <target>`

Result: PASS after running with filesystem permission suitable for the separate local target folder.

The first non-elevated render attempt failed before writing files because the target folder write was denied by the local execution sandbox. After confirming the target still only contained `template.config.yml`, the same render was rerun with permission to write to the local target folder and completed successfully.

## Generated Files Summary

Generated docs:
- `ACCEPTANCE_TRACE.md`
- `AGENTS.md`
- `MVP.md`
- `PRODUCT.md`
- `README.md`
- `STATUS.md`
- `AGENTS.override.md`
- `README.profile.md`
- `SAFETY_POLICY.profile.md`
- `STATUS.profile.md`
- `VERIFICATION.profile.md`

Input file retained:
- `template.config.yml`

No runtime source files, project files, binaries, workflows, secrets, or live config were generated.

## Safety Checks

| check | result | evidence |
|---|---|---|
| no private input | PASS | Synthetic/local config only |
| no secrets | PASS | No obvious secret/token/password/private-key pattern found |
| no live target write | PASS | Generated docs only; no live write mechanism |
| no application runtime code beyond generated docs | PASS | No `.py`, `.cs`, `.sln`, `.csproj`, `.exe`, `.dll`, or `.ps1` generated |
| no GitHub Actions workflow | PASS | No `.github` folder generated |
| no PLC/device code | PASS | `python_cli` profile generated documentation only |

## Conclusion

The `python_cli` profile is usable for a small separate local target project as a docs-only starting point.

The experiment confirms that the template can render base and profile documentation into a target folder without creating application runtime code, workflow files, PLC/device code, secrets, or live target write behavior.

Follow-up work should decide whether to test another profile or prepare a GitHub Release page draft. Formal `v0.1.0` remains deferred.
