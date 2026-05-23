# Local Downstream Adoption Plan

## Purpose

Define how to apply the formal `v0.1.0` codex-dev-harness baseline to a separate local downstream project without creating a downstream repository, running a live target, or generating runtime implementation code as part of this plan.

## Baseline

- Basis tag: `v0.1.0`
- Tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`
- Tag target commit: `43bbf001e1d2770466b41d5b8366f289b972a00b`
- Adoption mode: local-first
- GitHub Release page: NOT CREATED
- GitHub Actions workflow: NOT INSTALLED

## Local-First Adoption Flow

1. Create a clean local clone of `codex-dev-harness`.
2. Check out `v0.1.0`.
3. Run `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`.
4. Prepare a separate target folder outside the template repository.
5. Create a target-specific `template.config.yml`.
6. Run `scripts/render_template.py` in `--dry-run` mode first.
7. Review the target path, planned files, and side-effect boundary.
8. Run actual render only after explicit approval.
9. Review generated docs before any downstream implementation work starts.

## First Adoption Candidate

- Candidate: scenario simulator design baseline.
- Treatment: downstream application candidate, not built-in profile.
- Repository changes in codex-dev-harness for the candidate: NONE.
- Actual downstream render in this plan: NOT RUN.

## Application Method

- No profile.
- Base template only.
- Source-index driven.
- No raw source bulk copy.
- No sensitive values.
- No IP, port, tag, or live parameter values.
- No runtime code.
- No C# source, solution, or project files.
- No PLC/device code.
- No live target write support.

## Expected Generated Docs

The first downstream adoption should produce these base documents in the separate target folder:

- `SOURCE_INDEX.md`
- `PROJECT_BOUNDARY.md`
- `DATA_SCOPE.md`
- `PHASE_PLAN.md`
- `APPROVALS.md`
- `AGENTS.md`
- `PRODUCT.md`
- `MVP.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `README.md`

## Approval Checklist

Before actual render:

- Confirm the checkout is `v0.1.0`.
- Confirm `run_local_verify.ps1` passed.
- Confirm the target folder is separate from the template repository.
- Confirm `template.config.yml` uses `project.status: seed`.
- Confirm no profile is selected for the first scenario simulator design baseline trial.
- Confirm dry-run output lists only expected Markdown docs.
- Confirm no private input, raw source bulk copy, secret, live config, IP, port, tag, or live parameter is present.
- Confirm no runtime implementation, C# project, PLC/device code, or live-write support is planned.
- Confirm an explicit approval decision exists before actual render.

## Failure And Rollback Notes

- If clean clone verification fails, stop and record the failure before preparing any target folder.
- If dry-run output includes unexpected files or paths, do not run actual render.
- If target path review fails, delete only the separate target folder after confirming it is outside the template repository.
- If actual render is approved but generated docs are unsatisfactory, remove or archive the generated target docs only after confirming the target folder boundary.
- Do not use `--force` unless a separate approval explicitly covers overwrite behavior.
- Do not modify tags, GitHub Release pages, GitHub Actions workflows, or profile lists during adoption.

## Next Evidence To Collect

- Clean clone path generalized.
- Checkout ref and tag target confirmation.
- `run_local_verify.ps1` result.
- Target folder generalized path.
- `template.config.yml` summary without sensitive values.
- Dry-run planned file list.
- Approval decision for actual render.
- Actual render result, if approved.
- Generated docs review notes.
- Safety confirmation for no raw source, no sensitive values, no runtime code, and no live-write support.
