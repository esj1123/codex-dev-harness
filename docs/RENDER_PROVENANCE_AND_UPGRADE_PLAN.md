# RENDER_PROVENANCE_AND_UPGRADE_PLAN.md

## Purpose

Define how downstream projects should know which harness render basis they came
from and how they should receive later template updates without overwriting
reviewed project-specific content.

This is a contract plan only. It does not implement render script behavior,
write generated provenance stamps, rewrite examples, edit downstream projects,
create artifacts, or run release automation.

## Operating Model

The template uses a hybrid operating model:

- Stamp durable project guidance into downstream repositories when a project is
  created or intentionally upgraded.
- Keep verification centralized in this harness through render checks,
  readiness scans, secret scans, and future target-root audits.
- Treat downstream edits as reviewed project work, not as automatic harness
  overwrite output.

## Provenance Stamp Fields

A future render provenance stamp should be safe, bounded, and repo-relative. The
stamp should identify render basis without embedding private paths, raw command
logs, account values, prompts, tool payloads, secrets, or live configuration.

Candidate fields:

- `schema_version`
- `harness_commit`
- `harness_version` or release label, when available
- `render_profile`
- `project_name`
- `project_status`
- `config_source`
- `render_command_class`
- `rendered_file_set`
- `generated_vs_user_editable_policy`
- `created_at_utc`, only if non-determinism is explicitly accepted for that
  stamp target

`harness_commit`, `render_profile`, and `config_source` are the minimum useful
fields because they let maintainers reconstruct the intended render basis.

## Generated Versus User-Editable Boundary

Rendered files are starting points for project governance. After a downstream
project reviews or edits them, those files become project-owned content.

A provenance stamp must therefore distinguish:

- generated snapshot basis: the raw template output that can be re-rendered for
  comparison
- user-editable project docs: reviewed downstream files that must not be
  overwritten automatically
- harness-owned verification: checks run from this repository against a target
  root or a temporary render output

Curated regression examples in `examples/*_minimal` remain curated skeletons,
not byte-for-byte generated snapshots.

## Upgrade Workflow

The safe upgrade path is compare-first:

1. Identify the downstream project's recorded `harness_commit`,
   `render_profile`, and `config_source`.
2. Re-render the same config into a temporary directory outside the downstream
   project worktree or into an explicitly disposable scratch path.
3. Compare the temporary render output with the current downstream files.
4. Review differences file by file and classify them as template improvement,
   downstream customization, or conflict.
5. Apply selected changes manually or with an explicit approved patch.
6. Re-run central harness checks against the downstream target root when a
   target-root audit path exists.
7. Do not use blanket `--force` overwrite on reviewed downstream content.

Missing provenance should not trigger automatic overwrite. It should trigger a
manual baseline identification step.

## Non-Goals

This plan does not authorize:

- render script behavior changes
- automatic downstream overwrite
- tracked generated provenance stamps
- workflow or CI changes
- artifact generation
- release, tag, or publication behavior
- downstream repository access
- secret, account, prompt, tool-call, local absolute path, live config, or raw
  evidence persistence

## Implementation Sequence

1. Document this contract and keep examples curated.
2. Keep dry-run provenance preview support limited to safe summary output; it
   must not write tracked provenance stamps or downstream files.
3. Add a temporary re-render diff helper only after preview semantics are clear.
4. Add target-root central audit support only after downstream access and data
   boundary rules are explicitly approved.
