# Local Target Experiment Plan: csharp_desktop

## Purpose

Plan a future local target experiment for the `csharp_desktop` profile without
executing a target render in the planning task.

This document was created as documentation-only planning. It did not create a
downstream target folder, C# source, solution files, project files, XAML, build
assets, CI workflow, release artifact, or live-write behavior.

## Execution Record

An approved controlled execution record now exists:

- `docs/LOCAL_TARGET_EXPERIMENT_csharp_desktop_post_v0.1.0.md`

That execution used a separate outside-repo temporary target, performed dry-run
review before actual render, generated Markdown documentation only, and did not
add C# source, solution, project, XAML, build assets, PLC/device code, live
configuration, CI workflow, release publication, tag movement, or live-write
behavior.

## Target Profile

- Profile: `csharp_desktop`
- Existing regression example config:
  `examples/csharp_desktop_minimal/template.config.yml`
- Intended experiment type: local docs-only render into a separate temporary
  target after explicit owner approval.

## Separate Temporary Target Requirement

The experiment must use a separate temporary target folder that is not a real
application project and is not a repository-internal production path.

Required target properties:

- Empty or disposable before render.
- Created only after explicit approval.
- Not inside `.git/`, `artifacts/`, `docs/`, `scripts/`, `profiles/`,
  `templates/`, or an existing downstream project.
- Not a real C# application repository.
- Contains no private input, raw source, secrets, credentials, live
  configuration, equipment details, IPs, ports, tags, or live parameter values.

Use a neutral placeholder in planning records, such as:

- `<approved-temp-target>/csharp_desktop_doc_target`

Do not record a real sensitive local path in committed evidence.

## Dry-Run First Requirement

Dry-run must be executed before any actual write is requested.

Planned dry-run command:

```powershell
python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target <approved-temp-target>/csharp_desktop_doc_target --dry-run
```

Dry-run review must confirm:

- The target path is the approved temporary target.
- The planned output list contains Markdown documentation only.
- No overwrite of an existing downstream project is planned.
- No generated C# source, solution, project, XAML, build asset, binary,
  workflow, or live configuration is planned.

## Expected Generated Docs Only

Expected rendered files are documentation files only:

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

Forbidden generated outputs include:

- `.sln`
- `.csproj`
- `.cs`
- `.xaml`
- `.props`
- `.targets`
- binaries
- package files
- build scripts
- CI workflows
- live configuration

## Required Safety Checks

Before requesting actual render approval, confirm:

- Local verification passed or any block is recorded honestly.
- Dry-run was reviewed and produced a docs-only output list.
- Target folder is separate, temporary, and approved.
- No `--force` use is planned unless separately approved.
- No real application code is generated.
- No C# source, solution, project, XAML, or build asset is generated.
- No private input, raw source, secret, credential, token, or live configuration
  is used.
- No equipment detail, IP, port, tag, or live parameter value is recorded.
- No CI workflow, release archive, tag movement, signing, publication, or
  artifact upload is performed.
- No `scenario_simulator` profile or example is created.

## Approval Needed Before Actual Render

Actual render is not approved by this plan.

Before any actual render write, the owner approval must explicitly name:

- Profile: `csharp_desktop`
- Approved temporary target path class or exact non-sensitive path.
- Whether the operation is dry-run only or actual render write.
- Whether overwrite or `--force` is forbidden or separately approved.

Without that approval, actual render status must remain `NOT RUN`.

## Evidence Document After Execution

If a future approved experiment is executed, create a separate evidence record,
for example:

- `docs/LOCAL_TARGET_EXPERIMENT_csharp_desktop_<date-or-ref>.md`

The evidence record should include:

- Repository commit or tag used as the source basis.
- Profile and config path.
- Target path classification without sensitive local detail.
- Commands run.
- Dry-run output list.
- Actual render result, if approved and executed.
- Generated files summary.
- Verification result.
- Safety checks.
- Any environment block, skipped step, or unresolved risk.

## NOT RUN / BLOCKED Recording

Use honest status language:

- `NOT RUN`: The step was not executed because approval was not granted or the
  task was planning-only.
- `BLOCKED`: The step could not proceed because required approval, target
  availability, verification, or safety evidence was missing.
- `ENVIRONMENT BLOCKED`: The local environment prevented a command from running,
  such as a Python launcher failure.
- `PASS`: Use only when the named check actually ran and passed.
- `FAIL`: Use when the named check ran and failed.

The original planning task recorded the future experiment as `NOT RUN`.
The approved post-v0.1.0 execution is recorded separately in
`docs/LOCAL_TARGET_EXPERIMENT_csharp_desktop_post_v0.1.0.md`.
