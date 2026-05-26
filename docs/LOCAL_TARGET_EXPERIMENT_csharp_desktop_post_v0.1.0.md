# Local Target Experiment: csharp_desktop Post v0.1.0

## Purpose

Record an approved controlled local target experiment for the
`csharp_desktop` profile after the post-v0.1.0 evidence baseline.

This record covers a dry-run review followed by an actual render into a
separate temporary target. It does not approve or add C# source, solution,
project, XAML, build assets, PLC/device code, live configuration, release
publication, tag movement, CI workflow installation, or downstream source
ingestion.

## Basis

| item | value |
|---|---|
| repository | `esj1123/codex-dev-harness` |
| branch/ref | `main` / `origin/main` |
| basis commit | `76d88b842852635c95adcd8f3534f95e8bdc3ff5` |
| profile | `csharp_desktop` |
| source config | `examples/csharp_desktop_minimal/template.config.yml` |
| copied target config | `<outside-repo-temp>/codex-dev-harness-csharp-desktop-post-v0.1.0-76d88b8/template.config.yml` |
| target folder type | outside-repo temporary target |
| target committed | NO |

The committed evidence records the target path class instead of the full local
machine path. The actual temporary folder used during execution was under the
local user temp directory.

## Pre-Experiment Verification

| command | result | notes |
|---|---|---|
| `python -m pytest` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| `python scripts/quality_gate.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| `python scripts/run_eval.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| bundled Python `python -m pytest` | PASS | 72 passed |
| bundled Python `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| bundled Python `python scripts/run_eval.py` | PASS | 14 named local-only non-LLM eval cases passed |

## Dry-Run Render

Command:

```powershell
python scripts/render_template.py --config <outside-repo-temp>/codex-dev-harness-csharp-desktop-post-v0.1.0-76d88b8/template.config.yml --target <outside-repo-temp>/codex-dev-harness-csharp-desktop-post-v0.1.0-76d88b8 --dry-run
```

Result: PASS.

The dry-run planned 16 Markdown documentation outputs and no prohibited C#,
build, binary, workflow, live configuration, or device artifacts.

## Actual Render

Command:

```powershell
python scripts/render_template.py --config <outside-repo-temp>/codex-dev-harness-csharp-desktop-post-v0.1.0-76d88b8/template.config.yml --target <outside-repo-temp>/codex-dev-harness-csharp-desktop-post-v0.1.0-76d88b8
```

Result: PASS.

The actual render generated Markdown documentation files only. The temporary
target also contained the copied `template.config.yml` support file used to run
the experiment.

## Generated File List

Rendered Markdown docs:

- `ACCEPTANCE_TRACE.md`
- `AGENTS.md`
- `AGENTS.override.md`
- `APPROVALS.md`
- `DATA_SCOPE.md`
- `MVP.md`
- `PHASE_PLAN.md`
- `PRODUCT.md`
- `PROJECT_BOUNDARY.md`
- `README.md`
- `README.profile.md`
- `SAFETY_POLICY.profile.md`
- `SOURCE_INDEX.md`
- `STATUS.md`
- `STATUS.profile.md`
- `VERIFICATION.profile.md`

Temporary support file:

- `template.config.yml`

## Prohibited Artifact Scan

| check | result | notes |
|---|---|---|
| `.sln` absent | PASS | No matching files found |
| `.csproj` absent | PASS | No matching files found |
| `.cs` absent | PASS | No matching files found |
| `.xaml` absent | PASS | No matching files found |
| `.props` / `.targets` absent | PASS | No matching files found |
| binaries absent | PASS | No `.exe` or `.dll` files found |
| live config absent | PASS | No live configuration file names found |
| secret assignment patterns absent | PASS | No obvious `password`, `secret`, `token`, `api_key`, or `private_key` assignment patterns found |
| IP-like values absent | PASS | No IPv4-like values found |

## Post-Experiment Verification

| command | result | notes |
|---|---|---|
| bundled Python `python -m pytest` | PASS | 72 passed |
| bundled Python `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| bundled Python `python scripts/run_eval.py` | PASS | 14 named local-only non-LLM eval cases passed |
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and three example render dry-runs passed |
| `git diff --check` | PASS | LF-to-CRLF warnings only |

## Safety Checks

- The target was outside the repository.
- The target was temporary and not committed.
- Dry-run review preceded actual render.
- No `--force` flag was used.
- No downstream private source was copied into the target.
- No secrets, credentials, tokens, private input, equipment details, IPs, ports,
  tags, or live parameter values were added.
- No C# source, solution, project, XAML, build asset, binary, or runtime code
  was generated.
- No PLC/device code, polling, connection, tag map, control action, live
  configuration, or live-write behavior was added.
- No `scenario_simulator` profile or example was created.
- No CI workflow was installed.
- No release archive, GitHub Release, tag creation, tag movement, signing, or
  artifact upload was performed.

## Conclusion

Outcome: PASS.

The approved `csharp_desktop` profile local target experiment generated only
the expected Markdown documentation in a separate temporary target after
dry-run review. It does not change the repository into a C# desktop
application project and does not expand live/device behavior.

## Next Recommendation

Keep the `plc_or_device_tool` local target experiment deferred unless a
separate owner approval explicitly names the temporary target, dry-run review,
actual render permission, safety checks, and evidence record scope.
