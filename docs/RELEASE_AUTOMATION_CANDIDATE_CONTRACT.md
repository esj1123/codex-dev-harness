# Release Automation Candidate Contract

## Purpose

Record the Phase 10B contract for the first narrow release automation candidate.

Phase 10B is documentation and focused synthetic-test only. It selects a future
local release evidence preflight dry-run candidate and defines the exact
approval boundary before any implementation. It does not implement a script,
run release verification, run generator scripts, regenerate artifacts, create or
move tags, upload artifacts, sign artifacts, publish a release, edit workflows,
call external services, or touch downstream repositories.

## Allowed Files

Phase 10B is limited to:

- `docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md`
- `tests/test_release_automation_candidate_contract.py`

`STATUS.md`, `ACCEPTANCE_TRACE.md`, `.github/workflows`, scripts, schemas,
generated artifacts, audits, evals, templates, profiles, examples,
dependencies, tags, releases, and downstream repositories are intentionally
excluded from this contract task.

## Basis

This contract depends on:

- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `docs/CI_POLICY.md`
- `docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md`
- `docs/RELEASE_BUNDLE_POLICY.md`
- `docs/RELEASE_MANIFEST_POLICY.md`
- `docs/SBOM_PROVENANCE_PLAN.md`
- `scripts/run_release_verify.ps1`
- `scripts/generate_manifest.py`
- `scripts/generate_checksums.py`
- `scripts/generate_sbom.py`
- `scripts/generate_provenance.py`
- `tests/test_release_automation_provenance_boundary.py`
- `tests/test_generate_manifest.py`
- `tests/test_generate_checksums.py`
- `tests/test_generate_sbom.py`
- `tests/test_generate_provenance.py`

The clean Local Verify evidence for the preceding Phase 10A boundary review is
run `28830639298`, job `85503573430`, for commit
`ca8c065fa72c3b7097f300d01ba71ee6d69f37ab`.

## Candidate Decision

Decision: `local_release_evidence_preflight_dry_run_candidate_selected_without_implementation`.

The first future release automation candidate is a local release evidence
preflight dry-run. The candidate is selected because it can validate release
automation readiness without creating release artifacts, moving tags, uploading
artifacts, publishing releases, changing workflows, signing artifacts, or
calling external services.

Phase 10B does not authorize implementation. A later Phase 10C task must name
exact files, commands, output rules, cleanup rules, and verification before any
script or automation behavior is added.

## Selected Candidate

Candidate id: `local_release_evidence_preflight_dry_run`.

Future candidate purpose:

- inspect repository state;
- inspect configured local release evidence paths;
- inspect whether expected local release evidence files are present or absent;
- report whether release evidence generation would be blocked, ready, or not
  run;
- produce a bounded dry-run summary only;
- preserve source-basis, artifact-containing, push, tag, release, upload, and
  downstream states as separate fields.

Future candidate must be local-only, standard-library-only, and dry-run-only by
default. It must not execute release evidence generators or release verification
wrappers.

## Future Implementation Contract

A later implementation task, if separately approved, may propose only these
implementation files:

- `docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md`
- `scripts/release_evidence_preflight.py`
- `tests/test_release_evidence_preflight.py`

The future task must not edit unrelated release generators, release evidence
artifacts, workflows, schemas, `STATUS.md`, `ACCEPTANCE_TRACE.md`, templates,
profiles, examples, dependencies, or downstream repositories unless a separate
owner approval explicitly names those files.

The future command shape must be explicit before implementation. The proposed
dry-run command is:

- `python scripts/release_evidence_preflight.py --repo-root . --dry-run --json`

The proposed command is a contract placeholder only. Phase 10B does not create
that script, run that command, or authorize the command to exist.

## Input Contract

Future implementation input must be limited to repository-owned release policy,
local release evidence metadata, and git state summaries:

- `docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md`
- `docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md`
- `docs/RELEASE_BUNDLE_POLICY.md`
- `docs/RELEASE_MANIFEST_POLICY.md`
- `docs/SBOM_PROVENANCE_PLAN.md`
- `artifacts/release-manifest.json`
- `artifacts/checksums.sha256`
- `artifacts/sbom.spdx.json`
- `artifacts/sbom.cdx.json`
- `artifacts/provenance.intoto.jsonl`
- safe git state summaries for branch, HEAD, upstream, and diff status

Future implementation must not read raw source bundles, prompt transcripts,
shell transcripts, raw command logs, local temporary folders, private inputs,
downstream repositories, live configuration, secrets, credentials, account
values, IPs, ports, endpoints, device values, or release publication tokens.

## Output Contract

Future implementation output must be bounded and non-persistent by default:

- stdout summary only by default;
- optional JSON stdout only when `--json` is provided;
- no tracked output file;
- no artifact under `artifacts/`;
- no audit log;
- no receipt file;
- no trace file;
- no release archive;
- no upload;
- no tag;
- no release publication.

If a later task proposes any output file, it must be a temporary output outside
the repository unless a separate owner approval names an exact repository path,
overwrite rule, retention rule, cleanup rule, and schema validation procedure.

## Status Contract

Future preflight status values must be explicit:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `FAIL`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`

Candidate output must distinguish these states:

- source-basis commit;
- artifact-containing commit;
- local HEAD commit;
- pushed commit;
- tag target;
- release target;
- generated local evidence artifact;
- uploaded artifact;
- downstream release state.

These states must not be collapsed into a single `released` or `ready` flag.

## Failure Modes

Future implementation must fail closed for:

- dirty worktree when clean state is required;
- branch/upstream mismatch;
- missing expected local release evidence;
- unexpected untracked files;
- unexpected generated artifact drift;
- unsafe output path;
- attempted artifact regeneration;
- attempted workflow edit;
- attempted tag creation or movement;
- attempted artifact upload;
- attempted release publication;
- attempted signing;
- attempted external metadata lookup;
- attempted package registry call;
- downstream access;
- raw private or live material exposure;
- cleanup failure.

None of these conditions may be treated as silent success.

## Verification

Phase 10B verification must include at least:

- `python -m pytest tests/test_release_automation_candidate_contract.py`
- `python -m pytest tests/test_release_automation_provenance_boundary.py`
- `python -m pytest tests/test_generate_manifest.py`
- `python -m pytest tests/test_generate_checksums.py`
- `python -m pytest tests/test_generate_sbom.py`
- `python -m pytest tests/test_generate_provenance.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Clean GitHub Actions Local Verify evidence should be recorded separately after
this contract is committed and pushed.

## Non-goals

Phase 10B does not:

- implement `scripts/release_evidence_preflight.py`;
- create `docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md`;
- create `tests/test_release_evidence_preflight.py`;
- run `scripts/run_release_verify.ps1`;
- run release evidence generators;
- regenerate `artifacts/release-manifest.json`;
- regenerate `artifacts/checksums.sha256`;
- regenerate `artifacts/sbom.spdx.json`;
- regenerate `artifacts/sbom.cdx.json`;
- regenerate `artifacts/provenance.intoto.jsonl`;
- create release archives;
- create or move tags;
- create a GitHub Release;
- upload artifacts;
- sign artifacts;
- add or edit workflows;
- add required checks;
- perform external metadata lookup;
- call package registries;
- change release, SBOM, provenance, eval, audit, MCP, Hermes, RAG, or downstream
  runtime behavior;
- publish, deploy, or mutate downstream repositories.

## Next Step

After Phase 10B is committed and clean Local Verify passes, the next safe release
step should be either:

- pause before any release automation implementation; or
- a separately approved Phase 10C implementation plan for the
  `local_release_evidence_preflight_dry_run` candidate that names exact allowed
  files, exact command behavior, output policy, cleanup policy, verification
  commands, and closeout evidence before adding code.

Phase 10B does not authorize implementation or execution by itself.
