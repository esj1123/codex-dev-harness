# STATUS.md

## Current State

`CORE_HARNESS_READY`

This is the current human progress summary and implementation sequence. Policy,
approval and hold boundaries are owned by AGENTS, the authority manifest and
`docs/SAFETY_POLICY.md`; verification is owned by `docs/VERIFICATION.md`.
The state label mirrors the manifest. A progress edit cannot change authority.

Source-bound verification, recovery and adoption history is preserved in
[Historical Local Checkpoints](ACCEPTANCE_TRACE.md#historical-local-checkpoints).
Those records are completed observations, not self-updating local or remote refs.

## NOW

Current work: `ENGINEERING PILOT FOLLOW-UP` (2026-10-06).

Local commits `d53a58d` (verification command alignment) and `381dfcd`
(Office template part preservation guidance) are complete and unpushed.
Local `main` is 11 commits ahead of its recorded upstream tracking ref.

The read-only pilot is complete per the user-relayed report: quantity notation
in the current reference drawing matches the latest applicable source; the
derivation basis of those quantities remains unverified.

Authoring pilot A1 is complete: the RevA template copy's `I_O Quantity` sheet
is populated. Claude's relayed independent check confirms values match the
sources, originals are preserved, and only one worksheet part changed among
28 package parts. General-purpose saving lost header images during A1; the
candidate was repaired by targeted part replacement, and the preservation
guidance is recorded in `381dfcd`.

Earlier maintenance results remain in
`local/checkpoints/maintenance-simplification-20261005/REPORT.md`;
engineering skill installation/loading and synthetic checks remain bound to
`local/checkpoints/engineering-workflows-20261005/closeout.json`.
These pilot observations do not establish comparative utility, which remains
NOT_MEASURED.

## NEXT

The drawing revision pilot (A2) awaits the user's concrete change values.
Push remains a separate user decision.

## Operational Capability Status

| Surface | State | Meaning |
|---|---|---|
| Core template harness | `READY` | Core docs, templates, examples, tests, and local verification are supported. |
| Renderer apply | `READY` | No-flag and `--dry-run` are previews; writes require explicit `--apply`. |
| Release generator code | `HARDENED` | Clean-HEAD Git-blob lineage, hash-locked SBOM inputs, non-circular provenance/checksums, and physical output-path controls are implemented. |
| Tracked release bundle | `CURRENT / LOCAL RELEASE / GITHUB-VERIFIED / TRANSIENT CI EXPORT / NOT PUBLISHED` | The six-file bundle was generated from its exact source basis by approved manual export, independently validated after download, and committed for local Git use. No remote release or publication is claimed. |
| Manual GitHub release-evidence export | `IMPLEMENTED / APPROVAL-GATED / COMPLETED` | Bounded one-day transport completed for the recorded source basis. Workflow run IDs stay in task closeout evidence. |
| External control-plane packages | `HARDENED / EXTERNAL CONTROL-PLANE ROOT VALIDATED` | Optional `--package-root` passed same-root, physical-safety, identity-drift, and downstream read-only acceptance. No new capability, approval, downstream remote action, or schema migration is granted. |
| Read-only environment diagnostic | `IMPLEMENTED / EXACT-SHA LOCALLY VERIFIED / LOCALLY ADOPTED` | Safe JSON diagnostics install nothing, persist no path, execute no verification suite, and perform no target behavior. Hosted evidence is separate. |
| Downstream target closeout | `STOCK / RSID / LAUNCHPAD LOCAL CHECKPOINTS COMPLETE` | Exact target SHA and result scopes are in Historical Local Checkpoints. Remote, Hosted, Office, transfer, and release remain unobserved or not authorized. |
| Agent Quality/provider | `STRUCTURAL V2 PASS / FROZEN / NOT_ADOPTED` | AQ-R5K structure passed; earlier HOLDs remain preserved. Provider, trial, calibration, baseline, promotion, and adoption remain held. |
| Role calibration v7 | `NOT RUN` | Core readiness authorizes no calibration trial or review batch. |
| Hermes/MCP | `HELD` | Runtime activation requires a selected repository use case and separate approval. |
| Local RAG | `ADVISORY / FROZEN` | Optional read-only retrieval is outside core verification. |
