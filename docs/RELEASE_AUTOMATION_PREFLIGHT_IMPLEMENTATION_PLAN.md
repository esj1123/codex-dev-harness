# Release Automation Preflight Implementation Plan

## Purpose

Define and implement the Phase 10C `local_release_evidence_preflight_dry_run`
candidate selected by `docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md`.

Phase 10C adds one local-only, standard-library-only, read-only preflight. It
inspects bounded repository and release-evidence metadata, reports whether the
local repository is ready for an explicitly approved evidence refresh, and
performs no release or repository mutation.

## Allowed Files

Phase 10C implementation is limited to:

- `docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md`
- `scripts/release_evidence_preflight.py`
- `tests/test_release_evidence_preflight.py`

Phase 10C does not edit `STATUS.md`, `ACCEPTANCE_TRACE.md`, the capability
roadmap, schemas, gates, workflows, generators, artifacts, audits, evals,
templates, profiles, examples, dependencies, or downstream repositories.

## Command Contract

The only approved command is:

- `python scripts/release_evidence_preflight.py --repo-root . --dry-run [--json]`

`--dry-run` is required. Omitting it returns `NOT RUN` and performs no
inspection. There is no write mode, output-file option, generator option,
workflow option, publication option, or downstream option.

Default output is one bounded text summary. `--json` emits one deterministic
JSON object to stdout with a final newline. Output is not persisted.

## Read-Only Input Contract

The preflight may read only the Phase 10B release policy documents, the five
configured local release evidence files, `artifacts/eval-report.json` for full
checksum verification, and bounded Git summaries.

The eval report is a narrow Phase 10C read-only clarification. It is not
generated, parsed into output, made routine, made release-blocking, or wired
into a gate or workflow. It is read only because the current checksum bundle
contains an entry for it.

Every fixed file input must remain repo-relative, resolve inside the selected
repository root, be UTF-8, and be no larger than 1 MiB. The preflight must not
read raw source bundles, prompts, transcripts, command logs, local temporary
folders, private input, live configuration, credentials, account values,
network endpoints, device values, release credentials, or downstream content.

Git inspection is limited to local branch, HEAD, configured upstream tracking
ref, tracked/untracked counts, local tag target, artifact path history, and
commit ancestry. Git commands use argument lists, `shell=False`, bounded stdout,
and a timeout. The preflight does not fetch or call any remote service.

## Evidence Checks

The preflight checks:

1. the fixed policy and evidence files exist and are bounded UTF-8;
2. the checksum file has the exact five expected entries;
3. existing canonical checksum verification passes without writing;
4. manifest and provenance source-basis commits match;
5. SPDX and CycloneDX root component versions match that source basis;
6. manifest inventory includes `LICENSE` and `SECURITY.md`;
7. SPDX and CycloneDX root license metadata is MIT;
8. the five release evidence files share one artifact-containing commit;
9. source basis, artifact-containing commit, and local HEAD have valid ancestry;
10. the worktree and local upstream summary satisfy the fail-closed boundary;
11. the Git status snapshot is unchanged after inspection.

The source-basis commit is intentionally older than the artifact-containing
commit. That relationship is not failure. If the artifact-containing commit is
a valid ancestor of a newer clean synchronized HEAD, the result is `PASS WITH
NOTES` with `EVIDENCE_REFRESH_RECOMMENDED`.

## Output Contract

JSON output is capped at 8 KiB and contains exactly these top-level fields:

- `schema_version`
- `candidate_id`
- `dry_run`
- `status`
- `readiness`
- `reason_codes`
- `repository_state`
- `evidence_state`
- `external_state`
- `performed_actions`

`repository_state` distinguishes local HEAD from the commit observed through
the local upstream tracking ref. It must label that pushed-commit observation as
`local_tracking_ref`; it is not live remote confirmation.

`evidence_state` distinguishes source basis from artifact-containing commit and
reports the fixed evidence paths, checksum count/status, and license status.

`external_state` reports local tag observation separately from release,
artifact-upload, and downstream states. The latter states remain `NOT RUN`
because Phase 10C authorizes no network, upload, release, or downstream access.

`performed_actions` is always `[]`. Output must not include absolute paths, raw
Git output, filenames from dirty/untracked status, private values, live values,
or secret-like material.

## Status And Exit Codes

The status precedence is:

1. `NOT RUN` when explicit dry-run intent is absent;
2. `ENVIRONMENT BLOCKED` when Git or repository state cannot be inspected;
3. `FAIL` for malformed/unsafe evidence, checksum or metadata inconsistency,
   invalid source ancestry, artifact commit drift, or cleanup failure;
4. `BLOCKED` for dirty/untracked state, missing evidence, missing/mismatched
   upstream, or artifact-to-HEAD ancestry failure;
5. `PASS WITH NOTES` when local checks pass and a newer clean HEAD makes an
   evidence refresh appropriate;
6. `PASS` when local checks pass and the artifact-containing commit is HEAD.

Exit code `0` means `PASS` or `PASS WITH NOTES`; exit code `1` means `BLOCKED`,
`FAIL`, or `ENVIRONMENT BLOCKED`; exit code `2` means `NOT RUN` or CLI usage
error.

## Cleanup And Side-Effect Boundary

The preflight records a bounded Git status snapshot before inspection and
compares it with a second snapshot afterward. Any change is
`CLEANUP_VERIFICATION_FAILED` and `FAIL`.

Phase 10C does not run release generators, run `scripts/run_release_verify.ps1`,
regenerate evidence, create temporary repository output, stage, commit, push,
fetch, tag, sign, upload, publish, dispatch workflows, call package registries,
call MCP tools, expand Hermes runtime, or access downstream repositories.

## Verification

Phase 10C verification includes:

- `python -m pytest tests/test_release_evidence_preflight.py`
- `python -m pytest tests/test_release_automation_candidate_contract.py`
- `python -m pytest tests/test_release_automation_provenance_boundary.py`
- `python -m pytest tests/test_generate_checksums.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Tests use synthetic temporary Git repositories and local tracking refs only.
They do not perform a real or synthetic `git push`, make network calls, or run
release generators.

## Next Step

After this three-file implementation is committed, pushed under separate
approval, and clean Local Verify passes, run one read-only Phase 10C.1 usage
probe on the synchronized repository tip. The expected first real-repository
result is `PASS WITH NOTES / EVIDENCE_REFRESH_RECOMMENDED` because the Phase 10C
source commit follows the existing artifact-containing commit.

The usage probe does not automatically authorize evidence regeneration,
workflow integration, release automation, tag or release actions, upload, or
downstream work.
