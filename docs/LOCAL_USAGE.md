# LOCAL_USAGE.md

## Purpose

codex-dev-harness is local-first. The primary workflow is to clone the
repository, verify it locally, preview template rendering, then apply the
generated documents to a new target project only after review with explicit
`--apply`.

The repository includes a manual read-only `.github/workflows/local-verify.yml`
workflow. It runs only through `workflow_dispatch` with an exact commit SHA; it
is not automatic and is not a required check.

## Clone And Prepare

1. Clone the repository.
2. Open a shell at the repository root.
3. For focused development, install the direct development requirements:

`python -m pip install -r requirements-dev.txt`

4. For an exact Local Verify or release-wrapper environment, install the lock
   instead and run the dependency check:

`python -m pip install -r requirements-dev.lock`

`python -m pip check`

5. Run focused tests as needed:

`python -m pytest`

6. Run the core quality gate:

`python scripts/quality_gate.py`

## Recommended Local Verification

Use the wrapper from the repository root:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

The wrapper runs:

1. exact development-environment validation and `pip check`
2. full `python -m pytest tests`
3. standalone `python scripts/run_eval.py`
4. core `python scripts/quality_gate.py`
5. Python CLI, C# desktop, and PLC/device profile render dry-runs

The wrapper does not perform real render writes and does not use `--force`.

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
