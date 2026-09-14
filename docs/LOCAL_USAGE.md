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

Choose an explicit lane from the repository root according to the purpose.
For routine local feedback:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -Lane Routine`

For the official integration pytest scope:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -Lane Core`

For extended regression:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -Lane Full`

The no-argument command still runs `Full`. `Routine` keeps the existing exact
quick-feedback exclusions and targets five minutes or less. Routine PASS is
local feedback, not V2/V3, release, or promotion evidence. `Core` excludes
centrally marked Agent Quality, Hermes/MCP, and Local RAG optional tests and
is the default Hosted Integration scope. Full remains the extended regression
superset. Follow `docs/VERIFICATION.md` and the cumulative impact plan for
required integration commands and extras; selecting a lane grants no approval.

If the normal OS temp root is unsuitable, use an existing dedicated directory
outside the repository and pass it explicitly with the intended lane:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -Lane Routine -PytestBaseTempRoot D:\Codex\_tmp\CODEX-HARNESS`

The directory must already exist, be absolute, remain outside the repository,
and not be a reparse point. The wrapper creates a unique pytest child path and
does not remove it automatically. Omitting the option preserves normal OS-temp
behavior.

The wrapper runs:

1. exact development-environment validation and `pip check`
2. pytest for the selected `Routine`, `Core`, or `Full` lane
3. standalone `python scripts/run_eval.py`
4. core `python scripts/quality_gate.py`
5. Python CLI, C# desktop, and PLC/device profile render dry-runs

The wrapper does not perform real render writes and does not use `--force`.
It disables pytest's cache provider. Tests may still create runner-side
temporary files, so read-only verification is not a zero-filesystem-write
claim.

### Structured execution result

Add `-Json` to a verification run when a caller needs to consume its result:

`powershell -NoProfile -File scripts/run_local_verify.ps1 -Lane Core -Json`

This runs the same checks as the selected lane. Standard output contains one
JSON result; detailed child output and diagnostics go to standard error.
Capture the streams separately to retain the detailed evidence without parsing
it as JSON. The wrapper does not create a report file or a persistent log.
The default text mode and `-EnvironmentOnly -Json` diagnostic remain available.

The result identifies the lane, overall status and exit code, and all seven
ordered verification steps. Each step records its command ID, `PASS`, `FAIL`,
or `NOT RUN`, and its observed child exit code. A child failure stops later
steps and preserves that child's nonzero code as the wrapper exit code.
Native standard-error output alone does not indicate failure. A launch failure
or missing child exit observation fails with wrapper exit code `1` and a null
child exit code. Setup failures leave all steps `NOT RUN`.
The aggregate verdict is computed from the fixed required step IDs and order;
missing, duplicate, unstarted or unsuccessful records cannot produce `PASS`.
This lets callers consume the verdict directly and inspect detailed logs only
for failures, contradictions or missing evidence.

Executed steps include `safe_argv` and `invocation_sha256`; unstarted steps have
null invocation fields. The safe argument list replaces the selected executable
with `{PYTHON}` or `{PY_LAUNCHER}`, retains the launcher's `-3.12`, and replaces
the generated pytest directory with `{PYTEST_BASETEMP}`. The hash uses the
actual invocation tokens at the call boundary, joined with NUL separators,
encoded as UTF-8 without a trailing separator. It correlates that invocation;
it is not a capture of native process arguments, resolved executable identity,
or proof of literal equality with a work-package command.

`wrapper_sha256` identifies only the wrapper file bytes observed during setup
(`source_binding_scope: "wrapper_only"`). The caller must still bind the
repository candidate, runtime and work package to this execution. The result
does not authenticate approval, replace independent review, or establish a
verification tier by itself. Parameter-binding errors and abrupt process
termination may produce no JSON result; missing or incomplete output must not
be treated as success.

### Standalone checker JSON results

For a direct quality-gate or eval decision without a report-file write, use:

```powershell
python scripts/quality_gate.py --json
python scripts/run_eval.py --json
```

These options run the same selected checks. Standard output is one compact JSON
object; the existing human-readable diagnostics go to standard error. Retain
the process exit code and capture the streams separately. The default text mode
remains available, and the outer `run_local_verify.ps1 -Json` step contract is
unchanged.

Both results contain `schema_version`, `checker_id`, `status`, `exit_code`,
`counts` (`total`, `passed`, `failed`), `results`, `omitted_result_count`,
`reason_codes`, and `report_written: false`. Each result row contains a safe
`check_id`, its status, and a message count. Quality-gate IDs identify the fixed
core gates. Eval IDs such as `case_0001` identify the one-based selected execution
order within that invocation; they are not stable cross-invocation case names.
Retain the chosen case selection when correlating eval rows with diagnostics.

The JSON excludes arbitrary case names, raw messages, local absolute paths and
timestamps. At most 100 result rows are included, with an explicit omitted
count. Failed rows are selected first; execution order is retained within the
failed and passed groups, and IDs retain their original check positions. Counts
and the aggregate verdict always cover every result, including omitted rows. A failure, no results, an inconsistent summary or a caught checker
exception cannot produce PASS. Detailed diagnostics remain available on stderr
when a failure or omitted row needs inspection. Invalid command-line arguments
may fail without a result object; missing JSON is never success.

`run_eval.py --json` accepts the existing `--case` selection but cannot be
combined with `--report`, `--summary-report` or `--cases-report`. Such a combination
is rejected before evaluation or report writing. The existing explicit report
modes are unchanged when `--json` is absent. `report_written: false` means that
this mode creates no eval report; existing checker-internal temporary validation
activity is preserved. It does not claim zero filesystem activity.

These are local checker decisions. The invocation, candidate, required
verification scope and independent review still belong in the task closeout.

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
