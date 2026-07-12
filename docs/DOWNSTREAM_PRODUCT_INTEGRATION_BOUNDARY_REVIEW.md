# Downstream Product Integration Boundary Review

## Purpose

Record the Phase 11A boundary review for future downstream product integration.

Phase 11A is documentation and focused contract-test only. It defines the
authority, data, evidence, repository-access, and side-effect boundaries that
must exist before any downstream repository is inspected, cloned, edited,
tested, committed, pushed, or otherwise changed.

No downstream repository, worktree, branch, path, remote, product, customer,
account, endpoint, device, or live target is selected by this task.

## Allowed Files

Phase 11A is limited to:

- `docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md`
- `tests/test_downstream_product_integration_boundary.py`

`STATUS.md`, `ACCEPTANCE_TRACE.md`,
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, `.github/workflows`, scripts,
schemas, artifacts, audits, evals, templates, profiles, examples, dependencies,
and existing downstream records are intentionally excluded.

No downstream repository or path is an allowed file surface in Phase 11A.

## Basis

This review depends on:

- `AGENTS.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `docs/SAFETY_POLICY.md`
- `docs/AI_HANDOFF.md`
- `docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md`
- `docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md`
- `docs/DOWNSTREAM_READINESS_PROMPT_USE_VALIDATION.md`
- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/RELEASE_EVIDENCE_REFRESH_DECISION.md`

The stable Phase 10 checkpoint is commit
`6aabb2a681528b1a2c6e02f2ecadb56b025bf66e`. Its clean Local Verify is run
`29159465667`, job `86561923928`, with 470 tests, nine quality gates, all three
profile render dry-runs, read-only contents permission, and no uploaded
artifacts.

The Phase 10D.1 read-only checkpoint review retained release evidence refresh
at `HOLD` because no current tag, GitHub Release, upload, publication, or
downstream target exists. Phase 11A does not change that decision.

## Boundary Decision

Decision: `downstream_product_integration_boundary_documented_without_downstream_access`.

Phase 11A does not authorize downstream access or integration. It records the
minimum contract that a later task must satisfy before any downstream action is
considered.

The presence of templates, profiles, render tooling, adoption records, Local
RAG, MCP boundary documents, Hermes boundary documents, release evidence, or a
clean harness checkpoint does not grant authority over another repository.

## Authority Model

A future downstream task must apply the most restrictive applicable rule from:

1. the explicit owner approval for that task;
2. the downstream repository's local instructions, including its `AGENTS.md`;
3. the downstream repository's branch, worktree, review, and release rules;
4. this harness boundary and its safety policies.

Harness guidance cannot override or broaden downstream repository authority.
Missing, conflicting, stale, or unreadable instructions make the task
`BLOCKED` until the owner resolves the conflict.

Approval for one repository, branch, worktree, file set, command, or side
effect does not transfer to another. Read access does not imply write access,
local write does not imply commit, commit does not imply push, and push does not
imply pull request, merge, release, deployment, or live action.

## Required Downstream Task Contract

Before future downstream access, the task must name:

- an owner-approved repository identifier that is safe to report;
- the access class: local read-only, remote read-only, local write, or remote
  write;
- the approved clone or worktree boundary without persisting a local absolute
  path in harness records;
- the expected branch, base commit, HEAD, upstream, and clean or dirty state;
- exact allowed files and explicit no-touch paths;
- exact commands and whether each command reads, writes, executes code, uses
  network access, or mutates remote state;
- the allowed data classes and forbidden private or live data;
- required target-repository approvals and the approval reference;
- verification commands and truthful `NOT RUN` items;
- rollback, cleanup, retention, and overwrite rules;
- commit, push, pull request, merge, release, deployment, and downstream live
  action permissions as separate decisions;
- closeout fields, safe evidence references, and stop conditions.

If any required item is absent, ambiguous, or inconsistent with the downstream
repository's rules, downstream work is `BLOCKED` and no access occurs.

## Data And Evidence Boundary

Harness-facing downstream evidence must be selected-field, bounded, and safe.
It may contain only owner-approved generalized identifiers, repo-relative file
references, commit identifiers, bounded status and reason codes, verification
outcomes, and a short safe summary.

It must not copy or persist:

- private repository names or remote URLs unless explicitly approved;
- local absolute paths or user/account identifiers;
- raw source files, full diffs, patches, archives, or generated applications;
- prompts, approval text, transcripts, raw stdout or stderr, shell history,
  command logs, or tool-call bodies;
- secrets, tokens, credentials, cookies, keys, connection strings, or private
  configuration;
- customer, employee, account, broker, financial, or other private data;
- IP addresses, ports, endpoints, live configuration, device values, PLC
  values, equipment parameters, production values, or downstream raw evidence;
- raw audit, receipt, trace, RAG, RSID, or study evidence.

Findings must report category, bounded status, and safe remediation context
without echoing a sensitive matched value. A scan result is not proof that
private data or secrets are absent.

No downstream evidence is written to `artifacts/`, `audits/receipts/`,
`audits/traces/`, or any audit log by Phase 11A.

## Repository And Side-Effect Boundary

Phase 11A performs no downstream operation. A later task must separately
authorize each applicable class:

- locating or opening a local downstream repository;
- cloning, fetching, pulling, checking out, or creating a worktree;
- reading a private repository or calling a remote repository API;
- installing dependencies, building, testing, executing hooks, or running
  generated code;
- rendering, generating, editing, deleting, moving, or overwriting files;
- staging, committing, amending, rebasing, resetting, or merging;
- pushing, force-pushing, opening or updating a pull request, or modifying an
  issue;
- dispatching workflows, uploading artifacts, signing, tagging, releasing,
  publishing, deploying, or changing repository settings;
- calling MCP, Hermes, AgentOps, memory, external services, devices, brokers,
  accounts, production systems, or live targets.

Force push, destructive Git operations, live control, release publication, and
downstream deployment remain forbidden unless an exact owner approval names the
operation and target.

## Boundary Checks

Phase 11A checks that:

1. no downstream repository or product is selected;
2. no downstream path, remote, branch, or private identifier is recorded;
3. downstream repository rules remain authoritative;
4. future task contracts fail closed when scope or approval is incomplete;
5. downstream data is not copied into harness records;
6. read, write, execute, commit, push, review, release, deploy, and live-action
   permissions remain distinct;
7. release evidence refresh remains `HOLD`;
8. no workflow, artifact, receipt, trace, audit log, runtime, or downstream
   file is created or changed.

## Failure Modes

Future downstream work must use explicit statuses:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `FAIL`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`

Missing approval, wrong repository, stale branch, unexpected dirty state,
allowed-file drift, instruction conflict, unsafe data, unauthorized network
access, unexpected generated output, cleanup failure, and any unapproved remote
or live side effect are not silent success.

## Verification

Phase 11A verification must include at least:

- `python -m pytest tests/test_downstream_product_integration_boundary.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `python scripts/generate_checksums.py --verify`
- `python scripts/generate_corpus_digest.py --check --json`
- `git diff --check`
- `git ls-files --others --exclude-standard`

`python scripts/run_eval.py` is `NOT RUN` because Phase 11A does not change eval
behavior and must not mutate eval evidence. Release verification and all
downstream commands are also `NOT RUN`.

Clean GitHub Actions Local Verify evidence belongs in task closeout only after
the Phase 11A commit is separately approved for push. Run and job identifiers
must not create a recursive documentation commit.

## Non-goals

Phase 11A does not:

- select, locate, clone, fetch, inspect, or modify a downstream repository;
- render templates into a downstream target;
- add a downstream profile or example;
- create application code, generated source, build files, or dependencies;
- execute downstream tests, builds, hooks, packages, or applications;
- read or persist private downstream data;
- create a receipt, trace, audit log, artifact, report, or release archive;
- regenerate the corpus digest, release evidence, or eval report;
- change scripts, schemas, gates, workflows, templates, profiles, or examples;
- execute MCP or Hermes, add AgentOps or memory behavior, or call an external
  service;
- stage, commit, push, open a pull request, tag, release, publish, deploy, or
  perform a live action in a downstream repository.

## Next Step

After Phase 11A is committed and clean Local Verify passes, either pause until
the owner names a downstream candidate or use a separately approved Phase 11B
task to create a synthetic downstream task-contract fixture and focused review
tests.

Phase 11B must use placeholders such as `<DOWNSTREAM_REPO_ID>`,
`<APPROVED_WORKTREE>`, `<WORKING_BRANCH>`, and `<ALLOWED_FILE_LIST>`. It must not
locate, read, clone, fetch, render into, or modify a real downstream repository.

Actual downstream access remains a later owner-approved task under the target
repository's rules.
