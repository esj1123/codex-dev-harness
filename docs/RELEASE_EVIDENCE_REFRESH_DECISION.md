# Release Evidence Refresh Decision

## Purpose

Record the Phase 10D hold/proceed decision after the Phase 10C local release
evidence preflight implementation and the Phase 10C.1 synchronized-tip usage
probe.

Phase 10D is documentation and focused contract-test only. It does not change
`scripts/release_evidence_preflight.py`, run release evidence generators,
regenerate artifacts, edit workflows or schemas, update `STATUS.md` or the
capability roadmap, refresh the approved corpus digest, create or move a tag,
upload an artifact, publish a release, or access a downstream repository.

The only Phase 10D files are:

- `docs/RELEASE_EVIDENCE_REFRESH_DECISION.md`
- `tests/test_release_evidence_refresh_decision.py`

## Basis

This decision depends on:

- `docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md`
- `docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md`
- `docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md`
- `docs/RELEASE_EVIDENCE_PREFLIGHT_USAGE_PROBE.md`
- `docs/RELEASE_BUNDLE_POLICY.md`
- `docs/RELEASE_MANIFEST_POLICY.md`
- `docs/SBOM_PROVENANCE_PLAN.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `scripts/release_evidence_preflight.py`
- `scripts/run_release_verify.ps1`

The Phase 10C.1 implementation basis is commit
`7fa51a0cd44b8d35674b38513d9e1b39be87ad1a`. Its clean Local Verify is run
`29156067497`, job `86553240545`, with 464 tests, nine quality gates, all three
profile render dry-runs, read-only contents permission, and no uploaded
artifacts.

The synchronized preflight result is `PASS WITH NOTES` with readiness `READY`
and the single reason code `EVIDENCE_REFRESH_RECOMMENDED`.

## Decision

Decision: `release_evidence_refresh_hold_until_stable_phase_10_checkpoint`.

Status: `HOLD`.

Reason codes:

- `HANDOFF_SYNCHRONIZATION_PENDING`
- `STABLE_SOURCE_BASIS_PENDING`
- `NO_RELEASE_PUBLICATION_TARGET`

The release evidence refresh remains on hold. The current evidence is
internally valid historical source-basis evidence, checksum verification passes,
and the preflight note is informational rather than a blocker.

An immediate refresh would precede the known `STATUS.md` and capability-roadmap
handoff synchronization and the resulting same-source corpus digest freshness
repair. That sequence would create another source-basis change immediately
after regeneration. No release, tag, upload, publication, or downstream target
currently requires current-tip evidence.

## Current Evidence State

| field | reviewed value |
|---|---|
| reviewed Phase 10C.1 tip | `7fa51a0cd44b8d35674b38513d9e1b39be87ad1a` |
| source-basis commit | `28b416f9d46dc421c6e87dbc1562110a40224824` |
| artifact-containing commit | `588db911099d19de4d37b11b17f9a269b1157d77` |
| checksum status | `PASS`, five entries |
| license metadata status | `PASS` |
| approved corpus status | `34/34 valid`, stale `0` |
| release target | `NOT RUN` |
| uploaded artifact | `NOT RUN` |
| downstream release | `NOT RUN` |

These values describe separate source-basis, artifact-containing, local tip,
and external states. They must not be collapsed into a single released state.

## Proceed Conditions

A future refresh may change from `HOLD` to `PROCEED` only when one separately
owner-approved task names and verifies all of the following:

- the exact stable source-basis commit;
- the exact approval reference and generation command;
- completed `STATUS.md` and capability-roadmap handoff synchronization;
- a subsequent exact same-34-source corpus digest freshness commit with
  `34/34 valid`, stale `0`, and unchanged source membership and allow-list;
- a clean branch with local HEAD equal to the local upstream tracking commit;
- successful Local Verify for the stable source checkpoint;
- a preflight result with no `FAIL`, `BLOCKED`, or environment error;
- the exact five allowed release evidence output paths;
- an outside-repository backup and pre/post SHA-256 record for protected
  evidence;
- an overwrite and rollback rule for each generated artifact;
- proof that `artifacts/eval-report.json` remains byte-for-byte unchanged;
- focused tests, the full suite, all standing quality gates, checksum
  verification, corpus digest verification, and repository hygiene checks;
- separate approval for any push or workflow dispatch after local commit.

If any condition is absent or differs from its approved value, the refresh must
remain `HOLD` and no generator may run.

## Future Refresh Artifact Boundary

Only a later `PROCEED` task may regenerate these exact five tracked files:

- `artifacts/release-manifest.json`
- `artifacts/checksums.sha256`
- `artifacts/sbom.spdx.json`
- `artifacts/sbom.cdx.json`
- `artifacts/provenance.intoto.jsonl`

`artifacts/eval-report.json` is a protected read-only checksum input and must
remain unchanged. `artifacts/corpus-digest.json` must already be valid for the
approved stable source basis and is not a release-evidence output. No other
artifact, audit, receipt, trace, schema, workflow, template, profile, example,
or downstream file may change in a refresh task.

## Allowed Hold Work

While status is `HOLD`, allowed work is limited to:

- documentation-only decision review;
- focused contract tests;
- read-only preflight, checksum, corpus, and Git-state inspection;
- local test and quality-gate execution;
- closeout reporting without tracked run identifiers for the decision commit.

Allowed hold work does not include generator execution, temporary candidate
evidence, tracked evidence output, artifact overwrite, release automation, or
publication-adjacent behavior.

## Non-goals

Phase 10D does not:

- change release evidence generators, the preflight script, or the release
  verification wrapper;
- regenerate the release manifest, checksums, SPDX SBOM, CycloneDX SBOM, or
  provenance;
- regenerate `artifacts/eval-report.json` or the approved corpus digest;
- edit `STATUS.md`, `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, or
  `ACCEPTANCE_TRACE.md`;
- change schemas, quality gates, CI, or workflows;
- create archives, signatures, attestations, tags, releases, or uploads;
- call external metadata services or package registries;
- execute MCP tools, expand Hermes runtime, add AgentOps or memory behavior, or
  access downstream repositories.

## Verification

Phase 10D is accepted as `PASS WITH NOTES / HOLD` when the decision document and
focused contract tests pass local verification.

Required verification:

- `python -m pytest tests/test_release_evidence_refresh_decision.py`
- `python -m pytest tests/test_release_evidence_preflight.py`
- `python -m pytest tests/test_release_automation_candidate_contract.py`
- `python -m pytest tests/test_release_automation_provenance_boundary.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `python scripts/generate_checksums.py --verify`
- `python scripts/generate_corpus_digest.py --check --json`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Clean GitHub Actions Local Verify evidence belongs in task closeout after this
decision is committed and pushed. Its run and job identifiers must not create a
recursive documentation commit.

## Next Step

After Phase 10D is committed and clean Local Verify passes, use a separately
approved current-handoff synchronization task for `STATUS.md` and
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, followed by an exact
same-34-source corpus digest freshness commit.

That digest-valid checkpoint may then be reviewed against the `Proceed
Conditions`. Release evidence regeneration still requires a separate exact-file,
exact-command, owner-approved task and is not authorized by Phase 10D.
