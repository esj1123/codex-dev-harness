# Release Summary Prompt

Use this prompt to summarize a release candidate, tag, package, or publication decision.

This template is documentation-only. It does not create tags, move tags, publish releases, generate artifacts, or approve release actions.

## Release Target

- Release name or version: [name]
- Tag: [tag, or NOT CREATED]
- Commit: [commit, or TBD]
- Branch: [branch, if relevant]
- Publication status: [DRAFT / NOT CREATED / PUBLISHED / DEFERRED]

## Verification Basis

| check | result | evidence |
|---|---|---|
| tests | PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED | [path or command output summary] |
| quality gate | PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED | [path or command output summary] |
| render dry-run | PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED | [path or command output summary] |
| clean clone validation | PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED | [path or command output summary] |

## Manifest / Checksum

- Manifest: [PRESENT / NOT PRESENT / NOT APPLICABLE]
- Checksums: [PRESENT / NOT PRESENT / NOT APPLICABLE]
- Evidence path: [path or NONE]

Do not create or update manifest or checksum artifacts unless separately approved.

## SBOM / Provenance

- SBOM: [PRESENT / NOT PRESENT / NOT APPLICABLE]
- Provenance: [PRESENT / NOT PRESENT / NOT APPLICABLE]
- Evidence path: [path or NONE]

Do not create or update SBOM or provenance artifacts unless separately approved.

## Eval Result

- Eval harness: [PRESENT / NOT PRESENT / DEFERRED]
- Eval result: [PASS / FAIL / NOT RUN / NOT APPLICABLE]
- Evidence path: [path or NONE]

## Release Exclusions

Confirm exclusions:

- no tag movement unless approved
- no release publication unless approved
- no workflow installation unless approved
- no generated application/device/live-write behavior
- no secrets, private raw input, sensitive source text, or live values

## Summary

1. Release status
2. Verification result
3. Artifact status
4. Exclusions confirmed
5. Owner decisions still required
