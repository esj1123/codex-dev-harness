# SAFETY_POLICY.md

## Purpose

Define safety defaults for AI/Codex work using this template.

## Side Effects

Side effects include:
- File write, delete, move, rename, or permission change.
- Email send, reply, or forward.
- Database insert, update, delete, or migration apply.
- External API mutation.
- Live target write.
- PLC or equipment write, start, stop, reset, or mode change.

## Required Order

1. Read-only inspection.
2. Dry-run or expected change summary.
3. Review of expected changes.
4. Explicit confirmation for risky side effects.
5. Apply only within approved scope.
6. Closeout with evidence.

## Private Data Protection

Do not include:
- Secrets, credentials, keys, or tokens.
- Private raw input.
- Sensitive business source text.
- Device addresses, device parameters, or live-control values.

Use synthetic fixtures and summaries instead of private raw input.

## PLC and Equipment Work

Simulator or mock comes first. Live write, start, stop, reset, and mode change are high-risk side effects and are not part of P0.

## Harness Maintenance Boundaries

These boundaries apply to maintaining this Harness repository, not as a new
procedure for every downstream document. STATUS reports observations and next
actions; it cannot grant permission, lift a hold, or redefine these boundaries.
New capability selection follows `CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

Remote, Hosted, release, provider, trial, calibration, baseline promotion,
and Agent Quality redesign or adoption remain separate owner decisions.
No tracked recommendation alone authorizes remote action, release/publication,
runtime repair, branch deletion, worktree removal, target mutation, or adoption.

- Future Remote fetch/push, Harness or target Hosted workflow execution, export,
  tag, release, checksum, SBOM, provenance, signing, publication, deployment,
  durable remote distribution, target execution, and additional local-main
  mutation require exact repo-owned checkpoints and separate fresh authority.
  The completed normal push and exact-SHA Hosted V3 result at
  `bac6a13ef77e20554f67b38398fa65499828fba0` do not authorize a successor
  remote or Hosted action; future Remote and Hosted actions remain
  `HOLD / DEFERRED` by default.
- Agent Quality/provider/API/model execution, demonstrated-prevention trial,
  role calibration v7 or review batches, baseline creation/promotion/adoption,
  release, Git GC, and preservation packing remain held or `NOT RUN / DEFERRED`.
  Baseline adoption requires the numeric-bound and Unicode failures to complete
  human/grader review, owner-held graders to match the hardened invariants,
  and a fresh complete suite to meet every adoption threshold.
- Hermes/MCP activation, Hermes execution bridges, AgentOps, durable audit
  logging, Local RAG expansion, and target mutation remain held or separately
  approval-gated. Local RAG stays optional, read-only, advisory, and frozen.
- A generic command runner, inferred package fields, durable audit writer,
  automatic worktree prune, local-ref update, Junction repair, manifest
  rewrite, dependency installation, and EOL normalization remain `NO-GO`.
- Automatic digest writes, automatic release triggers, and release automation
  outside the selected manual GitHub release-evidence export contract are held.
  Completed manual export does not authorize another export or publication.
- New downstream access, render, write, commit, push, or workflow dispatch
  requires target-specific authority. Physical cleanup and the Stock-then-RSID
  sequence remain separate operational/target-owned checkpoints. RSID GAP-013
  owner/provenance remains unresolved; empty-root and merged-branch hygiene
  remains separate. Launchpad evidence does not authorize Office, transfer, or
  release work. No additional application capability has a selected contract.
- Hosted verification is an operational evidence checkpoint, not a new
  capability. The dirty-worktree checkpoint and P1 automation remain deferred.
- Agent Quality suites, schemas, and validation helpers remain preserved;
  historical envelopes do not establish core readiness, provider isolation,
  or role-profile mapping. Safe envelopes and failure candidates stay ignored
  under `local/agent-quality/`; raw prompts, transcripts, model output, and
  holdout fixtures are not tracked. Moving runtime/calibration archives does
  not adopt a baseline or change the tracked contract.
