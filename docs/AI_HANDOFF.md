# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum current context needed to
continue safely.

## Current Phase

Ready for separately approved parallel application development.

The machine-readable state is
`READY_FOR_PARALLEL_APPLICATION_DEVELOPMENT`. The harness completed its
pre-large-integration self-pilot, initialized the safe greenfield alias
`local-data-quality-cli`, governed two disjoint application feature lanes, and
closed the first synthetic MVP pilot without requiring a defect patch.

Work-package schema v2 now adds Windows-safe path ownership, contract-basis and
frozen-interface fields, contract reopen behavior, and an explicit distinction
between structural PASS and authenticated approval. The docs gate loads the
authority manifest at runtime and returns a structured failure when that
manifest is missing or malformed.

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

## Next Recommended Step

Complete the current same-source digest refresh and cumulative V2/V3 gate.
Then select one bounded post-MVP feature for `local-data-quality-cli`, freeze
the shared interface, and open only disjoint work packages. If a lane needs to
change the frozen contract, stop with `CONTRACT_CHANGE_REQUIRED` instead of
modifying the interface concurrently.
