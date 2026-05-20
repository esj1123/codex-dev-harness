# LOCAL_USAGE.md

## Purpose

codex-dev-harness is local-first. The primary workflow is to clone the repository, verify it locally, dry-run template rendering, then apply the generated documents to a new target project only after review.

GitHub Actions are not used in the current baseline.

## Clone And Prepare

1. Clone the repository.
2. Open a shell at the repository root.
3. Install development requirements:

`python -m pip install -r requirements-dev.txt`

4. Run tests:

`python -m pytest`

5. Run the quality gate:

`python scripts/quality_gate.py`

## Recommended Local Verification

Use the wrapper from the repository root:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

The wrapper runs:
- `python -m pytest`
- `python scripts/quality_gate.py`
- Python CLI example render dry-run.
- C# desktop example render dry-run.
- PLC/device tool example render dry-run.

The wrapper does not perform real render writes and does not use `--force`.

## Manual Render Dry-Run Checks

Run:

- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

## Applying To A New Target Project

1. Create or choose a separate target project folder outside this template repository.
2. Create a target-specific `template.config.yml` based on `template.config.example.yml`.
3. Run render with `--dry-run` first.
4. Review the expected output paths.
5. Run render without `--dry-run` only after confirming the target folder is correct.
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

Always start with `--dry-run`. Dry-run output lets you inspect generated paths before any file is written.

## Force Warning

`--force` allows overwriting existing files. Use it only after reviewing expected changes. Do not use `--force` in the local verification wrapper.

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
