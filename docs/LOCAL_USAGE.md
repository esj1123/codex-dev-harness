# LOCAL_USAGE.md

## Purpose

codex-dev-harness keeps local inspection and write intent local-first. The
normal verification loop is Local Quick, an approved exact-SHA push, Hosted
Integration Verify, and a comparable closeout. Template rendering remains a
local preview followed by explicit `--apply` only after review.

The repository includes a manual read-only `.github/workflows/local-verify.yml`
Hosted Integration Verify workflow. It uses `workflow_dispatch` with an exact commit SHA; it is not automatic and is not a required check.
Read-only means `contents: read` and no tracked-file, ref, tag, release, or
remote mutation; the hosted runner still performs normal checkout, environment,
dependency, and test filesystem writes. A PASS that contains every required
integration command satisfies the V2 command scope without a prior local Full
run.

The owner-selected `manual_github_release_evidence_export` contract is
implemented by the separate `.github/workflows/release-evidence-export.yml` workflow and remains
explicit and approval-gated. Hosted Integration Verify performs no artifact
upload. Only the export workflow may upload the six approved files with
one-day retention. Read `STATUS.md` for its current implementation and run
state.

## Clone And Prepare

1. Clone the repository.
2. Open a shell at the repository root.
3. For focused development, install the direct development requirements:

`python -m pip install -r requirements-dev.txt`

4. For an exact Local Verify or release-wrapper environment, install the lock
   instead and run the dependency check:

`python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock`

`python -m pip check`

5. Run focused tests as needed:

`python -m pytest`

6. Run the core quality gate:

`python scripts/quality_gate.py`

## Recommended Local Verification

Use the wrapper from the repository root:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

If the normal OS temp root is unsuitable, first create a dedicated directory
outside the repository, then pass it explicitly:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -PytestBaseTempRoot D:\Codex\_tmp\CODEX-HARNESS`

The directory must already exist, be absolute, remain outside the repository,
and not be a reparse point. The wrapper creates a unique pytest child path and
does not remove it automatically. Omitting the option preserves normal OS-temp
behavior.

The wrapper runs:

1. exact development-environment validation and `pip check`
2. full `python -m pytest tests`
3. standalone `python scripts/run_eval.py`
4. core `python scripts/quality_gate.py`
5. Python CLI, C# desktop, and PLC/device profile render dry-runs

The wrapper does not perform real render writes and does not use `--force`.
It disables pytest's cache provider. Tests may still create runner-side
temporary files, so read-only verification is not a zero-filesystem-write
claim.

## Manual Render Dry-Run Checks

Run:

- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

## Applying To A New Target Project

1. Create or choose a separate target project folder outside this template repository.
2. Create a target-specific `template.config.yml` based on `template.config.example.yml`.
3. Run render with no mode flag or with the compatible `--dry-run` preview.
4. Review the expected output paths.
5. Run render with explicit `--apply` only after confirming the target folder is correct.
6. Review generated docs before committing them to the target project.

The renderer config v1 accepts exactly `project.name`, `project.status`,
`profile.name`, and optional `render.tier`. The required CLI `--target` is the
only render-target authority. Safety and verification policy belongs in the
rendered project documents; config keys do not enable, disable, or authorize
those behaviors.

## Render Target Guard

The renderer refuses to render into the template repository itself.

Inside this repository, only `examples/<name>` is allowed as a render target for validation. The following are rejected:
- repository root
- `examples`
- nested example paths such as `examples/demo/nested`
- other repository folders such as `src` or `docs`

For real usage, prefer a separate target project folder outside this repository.

## Dry-Run First

Always start with the default preview (or the compatible `--dry-run` alias).
Preview output lets you inspect generated paths before any file is written.

## Force Warning

`--force` is valid only together with `--apply` and allows overwriting existing
regular single-link files. Use it only after reviewing expected changes. Do not
use `--apply` or `--force` in the local verification wrapper.

## Safety Boundaries

Do not include:
- private raw input
- secrets, keys, tokens, or credentials
- live config
- real equipment IP addresses, ports, tags, addresses, or live parameters
- PLC/device connection code
- live target write behavior
- actual application code in examples

PLC/device and live-target work must remain simulator/mock first and documentation-only in this baseline.
