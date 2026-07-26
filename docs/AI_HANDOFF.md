# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum current context needed to
continue safely.

## Current Phase

Agent-quality controls implemented; adoption baseline held.

The machine-readable state is
`AGENT_QUALITY_BASELINE_NOT_ESTABLISHED`. The harness completed its
pre-large-integration self-pilot, initialized the safe greenfield alias
`local-data-quality-cli`, governed disjoint application lanes, and installed a
standalone manual Agent Quality Stability layer.

Work-package schema v2 now adds Windows-safe path ownership, contract-basis and
frozen-interface fields, contract reopen behavior, and an explicit distinction
between structural PASS and authenticated approval. The docs gate loads the
authority manifest at runtime and returns a structured failure when that
manifest is missing or malformed.

The first fixed-configuration agentic suite completed 19 trials. Critical
5-trial tasks passed, but one numeric parser trial failed an owner-held valid
Decimal holdout. The aggregate is `HOLD`; no tracked agent-quality baseline
artifact exists. Safe envelopes and the pre-regression failure candidate remain
ignored local control-plane evidence.

This state does not authorize another target, another feature, a remote, push,
workflow dispatch, release action, or live/private data use.

## Source Of Truth

Read in this order:

1. `AGENTS.md`
2. `docs/AUTHORITY_MANIFEST.json`
3. `PRODUCT.md`
4. `MVP.md`
5. `STATUS.md`
6. `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
7. `docs/SAFETY_POLICY.md`
8. `docs/VERIFICATION.md`
9. `docs/AI_HANDOFF.md`

`ACCEPTANCE_TRACE.md` and older phase records are historical evidence, not
default operating context.

## Active Control Surface

- `scripts/work_package_conflict_check.py`
- `scripts/work_package_postflight.py`
- `docs/PARALLEL_WORK_PACKAGE_SYNTHETIC_FIXTURE.json`
- `docs/CHANGE_CONTROL.md`
- `docs/AUTHORITY_MANIFEST.json`
- `scripts/authority_manifest_check.py`
- `docs/VERIFICATION_IMPACT_MAP.json`
- `scripts/verification_plan.py`
- `scripts/gates/docs_gate.py`
- `docs/CI_POLICY.md`
- `docs/AGENT_QUALITY_STABILITY_POLICY.md`
- `scripts/agent_quality.py`
- `evals/agentic/suites/agentic-regression-v1.json`

Actual package JSON and optional checkpoint envelopes remain ignored local
control-plane data under `local/`. They must not contain secrets, private
payloads, absolute paths, raw command logs, or approval text.

## Work-Package V2 Rules

- All packages in a batch share one base and one canonical frozen contract
  surface.
- Feature packages declare non-empty `contract_frozen_paths` and include them
  in `read_set`.
- Case variants and parent/child ownership overlap are conflicts.
- A frozen-interface change returns `CONTRACT_CHANGE_REQUIRED`; stop the batch
  and create a new contract basis.
- Preflight and postflight return
  `authorization_status=NOT_AUTHENTICATED`. PASS does not grant execution or
  side-effect permission.
- Feature and contract lanes produce one coherent commit and do not change
  integration-only authority.

## Verification

V2 core:

- full pytest;
- `python scripts/run_eval.py` without report flags;
- `python scripts/quality_gate.py`.

Impact-required extras:

- checksum verification;
- exact corpus digest check;
- relevant profile render dry-runs.

V3 remains one separately approved push and one manual read-only Local Verify
for the final cumulative SHA. Tracked authority does not record run IDs.

## Current Boundaries

- The first local application pilot has no remote and no push authorization.
- Release evidence regeneration remains `HOLD`.
- Workflow expansion, tag/release/upload, MCP execution, Hermes execution
  bridges, AgentOps, memory runtime, and durable audit automation remain
  unapproved.
- No real, private, customer, or live data may be used.
- No new feature lane begins until its owner-selected contract and side-effect
  permissions are explicit.
- Agent-quality PASS is standalone evidence, not CI, release, approval, or
  execution authority.
- A failed trial cannot be replaced selectively after a fingerprint-affecting
  change; a comparable baseline requires a complete suite.

## Next Recommended Step

Review and sanitize the observed numeric parser failure, reproduce it with the
owner-held grader, and obtain human review before any regression promotion.
Keep baseline creation on hold. A changed prompt, tool policy, grader, model,
or task contract requires a complete new 19-trial run under one fingerprint.
