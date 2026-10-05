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

Current work: `HARNESS MAINTENANCE SIMPLIFICATION`.

The selected scope separates progress updates from policy changes, makes
completion reports proportional to the work, and corrects scanner aggregate
claims. Implementation and scoped results are recorded in
`local/checkpoints/maintenance-simplification-20261005/REPORT.md`.
Read the recorded result before claiming verification or completion.

The engineering authoring, diagram and review skills are the preceding local
candidate. Their installation/loading and synthetic checks remain bound to
`local/checkpoints/engineering-workflows-20261005/closeout.json`; actual target
utility remains NOT_MEASURED.

## NEXT

Read the selected task report for completed checks and any remaining
corrections. The next work choice is pending after this local two-commit handoff.
Pilot preparation, actual document/CAD use, additional skills, pushes,
launchpad pin changes and workspace cleanup are outside this selected work.

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
