# Hermes Git Push Preflight Output Contract

## Purpose

Record the Phase 9M output contract for the standalone dry-run Hermes
git-push preflight caller.

Phase 9M is documentation and focused synthetic-test only. It does not change
`scripts/hermes_git_push_preflight.py`, change `scripts/hermes_sidecar.py`,
run `git push`, stage files, commit, tag, dispatch workflows, upload
artifacts, execute MCP tools, create audit automation, generate real receipts,
logs, or traces, persist results, wire quality-gate or CI integration,
regenerate artifacts or digests, call external services, add AgentOps or
memory behavior, publish releases, or edit downstream repositories.

## Basis

This contract depends on:

- `scripts/hermes_git_push_preflight.py`
- `tests/test_hermes_git_push_preflight.py`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_CALLER_SELECTION_REVIEW.md`
- `docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md`
- `docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `scripts/hermes_sidecar.py`

If these sources conflict, the narrower and safer rule applies until a later
owner-approved task updates the contract explicitly.

## Required Top-level Fields

Every normal JSON result from `scripts/hermes_git_push_preflight.py` must
include these top-level fields:

| field | contract |
|---|---|
| `schema_version` | Must be `hermes_git_push_preflight.v0`. |
| `mode` | Must be `dry_run`. |
| `decision` | Must be `STOP` in the current implementation. |
| `side_effect_requested` | Must be `git_push`. |
| `guarded_command` | Must be `git push` as a label only, not an executed command. |
| `would_run_git_push` | Must be `false`. |
| `performed_actions` | Must be an empty list. |
| `safe_task_summary` | Must be sanitized text or a safe placeholder. |
| `approval_ref_present` | Boolean copied from the accepted Hermes boundary result. |
| `checked_fields` | Must list the Hermes fields inspected by the caller. |
| `evidence_refs` | Bounded accepted evidence references inside the approved scope. |
| `hermes_result` | Sanitized summary of the underlying no-op Hermes result. |
| `safety_notes` | Safe strings describing dry-run, non-execution, and non-persistence. |
| `reason_code` | Stop reason selected by the caller. |
| `stop_reasons` | Must include the selected stop reason. |
| `next_step` | Safe human-readable stop guidance. |

The output is a preflight decision record only. It is not an execution receipt
and must not be treated as authorization to push.

## Caller Decision Values

The only current caller decision is:

| decision | meaning |
|---|---|
| `STOP` | The caller must stop before `git push`; no executor or guarded push is authorized. |

Phase 9M does not define `ALLOW_EXECUTION`, `PROCEED`, or `RUN`. Any future
execution decision requires a separate contract update, a separate
implementation approval, and a separate approval for the guarded side effect.

## Reason Codes

The current caller may emit these `reason_code` values:

| reason_code | meaning |
|---|---|
| `approval_blocked` | The underlying Hermes result rejected a side-effect request without approval. |
| `executor_not_approved` | Hermes accepted the request boundary as `NOT_RUN`, but no executor is approved. |
| `unsafe_input` | Task summary, approval reference, or evidence input was unsafe. |
| `source_basis_blocked` | Evidence did not exist in the safe repository basis. |
| `unexpected_result_shape` | Required Hermes result fields were missing. |
| `unexpected_schema_version` | The Hermes result schema did not match `hermes_sidecar_noop.v0`. |
| `unexpected_mode` | The Hermes result mode was not `no_op`. |
| `unexpected_status` | The Hermes result status was outside the currently reviewed status set. |
| `scope_conflict` | The result did not describe the `git_push` side-effect class. |
| `contract_violation` | The Hermes result reported non-empty `performed_actions`. |
| `unexpected_evidence_shape` | Accepted-looking evidence was malformed. |
| `evidence_scope_blocked` | Evidence was outside the approved caller scope. |
| `environment_blocked` | The local environment could not support safe preflight interpretation. |
| `unexpected_advisory_result` | Advisory output appeared where a git-push side effect was being preflighted. |

Reason codes must remain fail-closed. They must not trigger fallback behavior
that runs Git commands, widens filesystem access, writes logs, starts servers,
calls tools, calls external services, or generates artifacts.

## Nested Hermes Result Summary

The nested `hermes_result` object is a sanitized summary only. It may include:

- `schema_version`
- `mode`
- `status`
- `reason_code`
- `side_effect_requested`
- `approval_ref_present`

It must not contain raw prompts, private data, raw command logs, unredacted
tool-call bodies, secrets, account values, IPs, ports, live config, device
values, local absolute paths, private raw corpus, `08_Study` raw notes, RSID
raw evidence, downstream raw evidence, or generated downstream source.

## Evidence References

Each accepted `evidence_refs` item must include:

| field | contract |
|---|---|
| `path` | Existing safe repo-relative path from the active approved caller scope. |
| `exists` | Must be `true`. |

Evidence references outside the approved caller scope must produce `STOP` with
`evidence_scope_blocked`. Malformed evidence references must produce `STOP`
with `unexpected_evidence_shape`.

## Non-persistence And Redaction

The current caller keeps the Hermes result in memory and emits only stdout JSON
for the immediate command invocation. It must not write receipt files, trace
files, audit logs, raw command logs, generated reports, digest artifacts,
release artifacts, downstream evidence, or temporary output files.

The output must not persist or echo:

- raw prompts or prompt transcripts;
- private data;
- raw command logs;
- model output transcripts;
- unredacted tool-call request or response bodies;
- secrets, credentials, tokens, account values, or API keys;
- IPs, ports, live endpoints, live config, device values, broker values, or
  equipment values;
- local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, downstream raw
  evidence, or generated downstream source.

Unsafe input must be represented by safe placeholders or safe stop guidance.

## Non-goals

Phase 9M does not:

- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- add a machine-readable JSON Schema artifact;
- connect Hermes to `scripts/quality_gate.py`, CI, MCP, audit automation,
  release automation, AgentOps, memory, external services, or downstream
  repositories;
- run `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation;
- generate or regenerate artifacts, digests, receipts, traces, logs, release
  files, or downstream evidence;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, private raw corpus, `08_Study`
  raw notes, RSID raw evidence, downstream raw evidence, or generated
  downstream source.

## Verification

Phase 9M is accepted as `PASS WITH NOTES` when this contract and focused
synthetic tests pass local verification.

The next safe Hermes step after Phase 9M is to commit and push this output
contract, then run clean Local Verify. Any later change that allows execution,
persistence, quality-gate or CI integration, MCP execution, audit automation,
release automation, external service calls, AgentOps or memory behavior, or
downstream integration must be separately approved.
