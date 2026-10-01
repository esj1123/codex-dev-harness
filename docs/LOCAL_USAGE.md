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

For an actual task decision, set the three parameters below to the bound
repository, approved Python runtime and an existing, approved fresh evidence
directory outside the repository, then run this standard-library example. It
executes only the two commands printed above. The four fixed evidence names must
not exist; the collision check happens before either checker runs, the directory
is not created automatically, and each stream is opened exclusively. Record the
actual argument arrays plus candidate, source and runtime bindings in the task
closeout.

```python
from pathlib import Path
import json, re, subprocess

REPO = Path(r"D:\path\to\bound\CODEX HARNESS")
PYTHON = Path(r"D:\path\to\approved\python.exe")
EVIDENCE_DIR = Path(r"D:\approved\fresh\external-evidence")
CHECKS = (
    ("quality_gate", ("scripts/quality_gate.py", "--json"), "quality-gate"),
    ("local_eval", ("scripts/run_eval.py", "--json"), "standalone-eval"),
)
# PASS contract from scripts/quality_gate.py:GATE_INVENTORY.
QUALITY_GATE_IDS = (
    "docs_gate", "repo_hygiene_gate", "template_schema_gate", "example_gate",
    "example_render_drift_gate", "rendered_golden_content_gate",
    "secret_scan_gate", "json_evidence_gate",
)

if not REPO.is_dir() or not PYTHON.is_file() or not EVIDENCE_DIR.is_dir():
    raise SystemExit("Set REPO, PYTHON, and an existing EVIDENCE_DIR first.")
paths = [
    EVIDENCE_DIR / f"{stem}.{stream}"
    for _, _, stem in CHECKS for stream in ("stdout.json", "stderr.txt")
]
collisions = [path.name for path in paths if path.exists()]
if collisions:
    print(json.dumps({"decision": "FAIL", "reason_codes": ["EVIDENCE_COLLISION"],
                      "evidence": collisions}, sort_keys=True, separators=(",", ":")))
    raise SystemExit(1)

is_uint = lambda value: type(value) is int and value >= 0
safe_id = re.compile(r"(?:[a-z][a-z0-9_]*|case_[0-9]{4})").fullmatch
safe_reason = re.compile(r"[A-Z][A-Z0-9_]*").fullmatch
decisions = []
for expected_id, command_tail, stem in CHECKS:
    stdout_path = EVIDENCE_DIR / f"{stem}.stdout.json"
    stderr_path = EVIDENCE_DIR / f"{stem}.stderr.txt"
    process = None
    with stdout_path.open("xb") as stdout_file, stderr_path.open("xb") as stderr_file:
        try:
            process = subprocess.run([str(PYTHON), *command_tail], cwd=REPO,
                                     stdout=stdout_file, stderr=stderr_file, check=False)
        except OSError as exc:
            stderr_file.write(f"Process launch error: {exc}\n".encode("utf-8"))

    invalid = [] if process is not None else ["PROCESS_LAUNCH_FAILED"]
    try:
        result = json.loads(stdout_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        result = None
        invalid.append("RESULT_JSON_INVALID")

    counts = result.get("counts") if isinstance(result, dict) else None
    rows = result.get("results") if isinstance(result, dict) else None
    reasons = result.get("reason_codes") if isinstance(result, dict) else None
    omitted = result.get("omitted_result_count") if isinstance(result, dict) else None
    reported_exit = result.get("exit_code") if isinstance(result, dict) else None
    process_exit = process.returncode if process is not None else None
    counts_ok = isinstance(counts, dict) and all(
        is_uint(counts.get(key)) for key in ("total", "passed", "failed"))
    rows_ok = isinstance(rows, list) and all(
        isinstance(row, dict) and isinstance(row.get("check_id"), str)
        and safe_id(row["check_id"]) and row.get("status") in ("PASS", "FAIL")
        and is_uint(row.get("message_count")) for row in rows)
    reasons_ok = isinstance(reasons, list) and all(
        isinstance(reason, str) and safe_reason(reason) for reason in reasons)
    contract_ok = (
        isinstance(result, dict) and result.get("schema_version") == "1"
        and result.get("checker_id") == expected_id
        and result.get("status") in ("PASS", "FAIL") and is_uint(reported_exit)
        and result.get("report_written") is False and counts_ok and rows_ok
        and reasons_ok and is_uint(omitted)
    )
    if not contract_ok:
        invalid.append("RESULT_CONTRACT_INVALID")
    else:
        projected = min(counts["total"], 100)
        projected_failed = min(counts["failed"], projected)
        statuses = ["FAIL"] * projected_failed + ["PASS"] * (projected - projected_failed)
        coherent = (
            counts["total"] == counts["passed"] + counts["failed"]
            and len(rows) == projected and omitted == counts["total"] - projected
            and [row["status"] for row in rows] == statuses
            and len({row["check_id"] for row in rows}) == len(rows)
            and process_exit == reported_exit
            and reported_exit == (0 if result["status"] == "PASS" else 1)
            and (result["status"] == "FAIL" and bool(reasons)
                 or result["status"] == "PASS" and counts["total"] > 0
                 and counts["failed"] == 0 and reasons == [])
        )
        if not coherent:
            invalid.append("RESULT_CONTRADICTION")
        if result["status"] == "PASS":
            expected_pass_ids = list(QUALITY_GATE_IDS) if expected_id == "quality_gate" else [
                f"case_{position:04d}" for position in range(1, projected + 1)]
            if ([row["check_id"] for row in rows] != expected_pass_ids
                    or expected_id == "quality_gate" and counts["total"] != len(QUALITY_GATE_IDS)):
                invalid.append("RESULT_CHECK_IDS_INVALID")

    failed_rows = [] if not rows_ok else [
        {"check_id": row["check_id"], "message_count": row["message_count"]}
        for row in rows if row["status"] == "FAIL"
    ]
    decision = "PASS" if not invalid and result["status"] == "PASS" else "FAIL"
    decisions.append({
        "checker_id": expected_id, "decision": decision,
        "process_exit": process_exit,
        "reported_exit": reported_exit if is_uint(reported_exit) else None,
        "counts": {key: counts[key] for key in ("total", "passed", "failed")}
                  if counts_ok else None,
        "reason_codes": [*invalid, *reasons] if reasons_ok else invalid,
        "failed_rows": failed_rows,
        "omitted_result_count": omitted if is_uint(omitted) else None,
        "evidence": {"stdout": stdout_path.name, "stderr": stderr_path.name},
    })
    if decision == "FAIL":
        break

overall = "PASS" if len(decisions) == len(CHECKS) and all(
    row["decision"] == "PASS" for row in decisions) else "FAIL"
print(json.dumps({"decision": overall, "results": decisions},
                 sort_keys=True, separators=(",", ":")))
raise SystemExit(0 if overall == "PASS" else 1)
```

The printed object selects verdicts, native and reported exits, aggregate counts,
checker/consumer reason codes, failed rows, omission counts and safe evidence
names. Its process exit is nonzero whenever the final decision is `FAIL`. It does
not repeat PASS rows or standard error. On the first process, JSON, contract,
identity/count or checker failure, the object reports `FAIL` and later checkers
are not run; the original stdout and stderr files remain available for diagnosis.
Missing, malformed, contradictory or unknown results therefore cannot become
PASS. This is a task-local caller example, not a public schema or reusable
runner.

These are local checker decisions. The invocation, candidate, required
verification scope and independent review still belong in the task closeout.

## Bounded Closeout State And Usage

The selected local `scripts/task_evidence_summary.py` reader projects exact
current-state inputs. Original Codex numeric usage metadata is an optional
evaluation input, not a requirement for inspection or task completion. Target
adapters own state meaning and approval. No discovery, recursive repository or
conversation search, timestamp-based latest-file selection, target command,
watcher, background service, input repair or evidence writer is provided.
The default is read-only stdout; approved callers may retain its safe output
in their existing task-owned evidence record.

At actual task start, declare one fixed spec and its physical input/runtime
roots in task coordination metadata. The existing postflight closeout/handoff
invocation then performs both inspections in process:

```text
python scripts/work_package_postflight.py --repo-root <REPO_ROOT> --package <PACKAGE_JSON> --task-id <TASK_ID> --verification-status PASS --verification-interpreter-id <INTERPRETER_ID> --completed-command-id <COMMAND_ID> --task-evidence-spec <SPEC_JSON> --task-evidence-input-root <TARGET_ROOT> --task-evidence-runtime-root <RUNTIME_ROOT> --json
```

For ordinary state/evidence inspection, declare `"runtime": []` and omit
`--task-evidence-runtime-root`. No runtime source is read. Select usage only
when an improvement evaluation needs it; do not add accounting work to every
task or make unavailable usage block an otherwise valid state-only inspection.

Repeat the completed command IDs as required. Spec location is relative to the
same package root; the normal `--package-root` option supports an external
local control-plane root. Omit the runtime-root flag when no runtime source is
declared. Existing invocations without these new flags retain their output
and decisions. The optional `task_evidence` result is separate from structural
postflight and from work-package schema v3. A bad projection blocks an otherwise
passing postflight; a valid projection of pending work does not declare target
completion or authenticate approval. For a bounded initial probe, the same
reader can run standalone with `--spec`, `--spec-root`, `--input-root`, optional
`--runtime-root`, and `--json`. Closeout callers use the postflight hook.
Omit `--json` for a bounded decision summary. With the hook selected, postflight
also includes that evidence summary; its no-hook text remains unchanged. Keep
detailed JSON in the existing approved evidence record and expand it for a
specific mismatch, uncertainty or changed input instead of returning all
unchanged evidence and per-turn details to the model on each handoff.

The local spec is JSON with exactly the following keys. It is a selected input
declaration, not a command language or a new work-package namespace:

| Key | Input contract |
| --- | --- |
| `schema_version` | Literal `"1"`. |
| `state` | `path`, exact raw-byte `sha256`, and `pointer` selecting current JSON. |
| `identities` | Up to 8 `{id,pointer,expected}` records; expected is a 40/64hex SHA. |
| `candidate` | Exact `path` and `sha256`; null SHA means unbound, never complete. |
| `evidence` | Fixed `root` and `pointer` to at most 64 `{path,sha256}` rows in current state. |
| `links` | Up to 64 `{receipt,pointer,target}` scalar SHA links within named evidence. |
| `gates` | Up to 32 `{id,pointer,states,proofs}` records; completed gates require named proofs. |
| `history` | Up to 16 `{id,path,pointer,states,gate}` historical claims from state or named evidence. |
| `runtime` | Up to 8 `{id,path,session_id,turns,cutoff}` original sources; one source per session/counter. |

Pointers are lists of at most 8 bounded JSON object keys. Every `states` map
has `completed`, `pending` and `unknown` lists of disjoint literal uppercase
status codes, booleans or null. Unmatched input becomes UNKNOWN; source prose
is never printed. IDs are safe local aliases. Named paths are Windows-safe
root-relative paths; UNC, traversal, symlink/reparse ancestry, hard links and
non-regular files fail. SHA comparison accepts uppercase hex but preserves
raw-byte hashes. UTF-8 JSON with an optional native producer BOM is decoded
without rewriting input. The spec limit is 64 KiB, receipt/current JSON 4 MiB,
individual hash input 64 MiB, runtime source 512 MiB, metadata line 2 MiB,
unique usage events 100,000 and output 16 KiB. Excess output becomes a small
failure envelope and a nonzero exit, including through postflight.

Output selects consistency, exact identities, COMPLETED/PENDING/UNKNOWN gates,
superseded claims, candidate binding and a mechanical next-action code. A
missing or unbound candidate cannot complete. A mismatch or malformed input
does not become PASS; exception strings, source body, raw tool output, paths
and private payload are not reflected. `authorization_status` remains
`NOT_AUTHENTICATED`; mappings, exact linkage and completion counters do not
grant qualification, adoption, runtime execution, technical authority or release.
Next actions distinguish inconsistent evidence, missing or unbound candidates,
pending gates and unknown gates. An unknown gate remains incomplete; it is not
silently converted into a pending task or PASS. Gate selection belongs to the
target's acceptance contract. Keep historical uncertainty in its source record,
and explicitly decide whether it blocks the current outcome before selecting
that task's required gates. Never remove a required gate merely to obtain PASS.

Reuse an existing verification only after matching its candidate and input
identities, command/runtime basis, acceptance scope and original result. Expand
to affected checks for drift, missing coverage, contradictions or new findings.
The current task's required integration and independent checks still apply;
this reader validates linkage and does not authenticate or rerun those checks.
Target adapters own domain-specific environment checks such as Office readiness.

Runtime accounting uses the previous snapshot of the same cumulative counter,
including an unselected predecessor. Only a verified initial zero boundary
(first cumulative snapshot equals last usage) includes the complete first
response. Duplicate event keys and unchanged snapshots contribute zero; reset,
missing/corrupt metadata and missing selected turns remain explicit coverage
gaps. Snapshot keys use session identity, timestamp and the cumulative tuple.
Repeated turn contexts do not create calls, and actual model/effort stays with
each observed group. Cached input and reasoning output are subsets; total is
input plus output. Inconsistent advisory last-usage or interval subset values
are flagged without discarding valid cumulative counter increments. A captured
runtime prefix is hashed twice to reject drift while permitting later append;
it is never copied or followed indefinitely. Large known message/body records
are skipped; oversized unrecognized records leave coverage PARTIAL.

Usage totals cover only the explicit distinct sessions and selected turns up
to each cutoff. Missing session identity prevents a combined total. API/model
calls and app turn durations are UNKNOWN; usage event timestamps do not measure
active labor. Record provider/reviewer/coordination/repair/handoff gaps, failed
attempts and preparation/review overhead in the existing measurement ledger.
Bytes and compact output are not token savings. Savings remains NOT_MEASURED
without a comparable accepted outcome and original usage/billing coverage.

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
