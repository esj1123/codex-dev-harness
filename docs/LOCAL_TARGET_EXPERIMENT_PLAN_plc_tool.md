# Local Target Experiment Plan: plc_or_device_tool

## Purpose

Plan a future local target experiment for the `plc_or_device_tool` profile
without executing a target render in this task.

This is documentation-only planning. It does not create a downstream target
folder, PLC/device code, polling logic, connection logic, tag maps, control
actions, live configuration, CI workflow, release artifact, or live-write
behavior.

## Target Profile

- Profile: `plc_or_device_tool`
- Existing regression example config:
  `examples/plc_tool_minimal/template.config.yml`
- Intended experiment type: local docs-only render into a separate temporary
  target after explicit owner approval.

## Separate Temporary Target Requirement

The experiment must use a separate temporary target folder that is not a real
device project and is not a repository-internal production path.

Required target properties:

- Empty or disposable before render.
- Created only after explicit approval.
- Not inside `.git/`, `artifacts/`, `docs/`, `scripts/`, `profiles/`,
  `templates/`, or an existing downstream project.
- Not connected to any real PLC, device, simulator, or live control system.
- Contains no private input, raw source, secrets, credentials, live
  configuration, equipment details, IPs, ports, tags, or live parameter values.

Use a neutral placeholder in planning records, such as:

- `<approved-temp-target>/plc_tool_doc_target`

Do not record a real sensitive local path in committed evidence.

## Dry-Run First Requirement

Dry-run must be executed before any actual write is requested.

Planned dry-run command:

```powershell
python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target <approved-temp-target>/plc_tool_doc_target --dry-run
```

Dry-run review must confirm:

- The target path is the approved temporary target.
- The planned output list contains Markdown documentation only.
- No overwrite of an existing downstream project is planned.
- No generated PLC/device code, polling logic, connection logic, tag map,
  control action, live configuration, workflow, or live-write mechanism is
  planned.

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

- PLC/device source code
- polling scripts
- connection scripts
- tag maps
- control actions
- live configuration
- start, stop, reset, or mode-change behavior
- `.sln`
- `.csproj`
- `.cs`
- `.xaml`
- binaries
- package files
- CI workflows

## Required Safety Checks

Before requesting actual render approval, confirm:

- Local verification passed or any block is recorded honestly.
- Dry-run was reviewed and produced a docs-only output list.
- Target folder is separate, temporary, and approved.
- No `--force` use is planned unless separately approved.
- No PLC/device code is generated.
- No polling, connection, tag map, control action, live configuration, or
  live-write support is generated.
- No start, stop, reset, mode-change, or device mutation behavior is generated.
- No private input, raw source, secret, credential, token, or live configuration
  is used.
- No equipment detail, IP, port, tag, or live parameter value is recorded.
- No CI workflow, release archive, tag movement, signing, publication, or
  artifact upload is performed.
- No `scenario_simulator` profile or example is created.

## Approval Needed Before Actual Render

Actual render is not approved by this plan.

Before any actual render write, the owner approval must explicitly name:

- Profile: `plc_or_device_tool`
- Approved temporary target path class or exact non-sensitive path.
- Whether the operation is dry-run only or actual render write.
- Whether overwrite or `--force` is forbidden or separately approved.

Without that approval, actual render status must remain `NOT RUN`.

## Evidence Document After Execution

If a future approved experiment is executed, create a separate evidence record,
for example:

- `docs/LOCAL_TARGET_EXPERIMENT_plc_tool_<date-or-ref>.md`

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

This plan itself records the future experiment as `NOT RUN`.

