# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum context needed to continue safely.

## Project Purpose

Reusable local-first template for governed AI/Codex development workflows.

## Current Phase

Ready for separately approved greenfield initialization.

The repository has completed the governed template, Render Tier, standalone
local RAG, JSON evidence, Hermes preflight, release-evidence preflight, and
synthetic downstream-contract validation checkpoints described by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

The pre-large-integration self-pilot adds a canonical work-package
`plan_digest`, read-only postflight enforcement, a machine-readable authority
manifest, and an advisory verification-impact planner. Two disjoint feature
lanes used the same base and plan digest, produced one commit each, passed V1,
and passed postflight before integration. The packages and result envelopes
remained ignored local control-plane data.

Phase 10 release evidence remains valid historical source-basis evidence and
regeneration remains on `HOLD`. Phase 11 is complete through the Phase 11D.2
temporary synthetic filled-contract usage probe. No real downstream
repository, path, branch, source, command, render, write, or private data has
been selected or accessed.

The greenfield `local-data-quality-cli` target contract is selected without
repository creation or implementation. The machine-readable current state is
`READY_FOR_GREENFIELD_INITIALIZATION`; it means the harness-side control
surfaces are available, not that target creation, render, feature work, or any
side effect is approved. Exact digest and Local Verify evidence for the final
cumulative commit stays in the artifact and task closeout rather than this
tracked handoff.

## Source of Truth

Read in this order:
1. AGENTS.md
2. docs/AUTHORITY_MANIFEST.json
3. PRODUCT.md
4. MVP.md
5. STATUS.md
6. docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
7. docs/SAFETY_POLICY.md
8. docs/VERIFICATION.md
9. docs/AI_HANDOFF.md

## Changed Files

Current baseline surface includes:

- root contract documents
- base Markdown templates
- profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`
- `scripts/render_template.py`
- `scripts/quality_gate.py`
- gate modules under `scripts/gates/`
- `scripts/run_local_verify.ps1`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `scripts/generate_manifest.py`
- `scripts/generate_checksums.py`
- `scripts/generate_sbom.py`
- `scripts/generate_provenance.py`
- `scripts/run_release_verify.ps1`
- `.github/workflows/local-verify.yml`
- `scripts/local_rag_retriever.py`
- `scripts/hermes_sidecar.py`
- `scripts/hermes_git_push_preflight.py`
- `scripts/release_evidence_preflight.py`
- `scripts/downstream_task_contract_validator.py`
- `scripts/work_package_conflict_check.py`
- `scripts/work_package_postflight.py`
- `scripts/authority_manifest_check.py`
- `scripts/verification_plan.py`
- `docs/AUTHORITY_MANIFEST.json`
- `docs/VERIFICATION_IMPACT_MAP.json`
- `docs/AI_READINESS_SCANNER_v0.md`
- `scripts/ai_readiness_scanner.py`
- regression examples under `examples/`
- pytest tests under `tests/`
  - includes `tests/test_ai_readiness_scanner.py`
- generated local release evidence under `artifacts/`
- Stage 1 governance policy docs:
  - `docs/CHANGE_CONTROL.md`
  - `docs/HUMAN_APPROVALS.md`
  - `docs/EVAL_POLICY.md`
  - `docs/AUDIT_LOG_POLICY.md`
- Capability implementation roadmap:
  - `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`

## Pending Risks

- No downstream target or owner target authorization exists.
- Release evidence regeneration, archives, publication, signing, tag movement,
  upload, and CI release behavior remain on `HOLD`.
- MCP execution, Hermes execution bridges, durable audit automation, AgentOps,
  and memory runtime are not implemented.
- The AI readiness scanner and local RAG retriever remain standalone and cannot
  authorize writes or broaden a task contract.
- The optional design-stage pack remains manual-use-only.
- Examples remain skeletons and do not execute real project builds or device
  behavior.
- `plc_or_device_tool` live target execution remains prohibited without a
  separate target-specific approval.

## Verification Status

Current local wrapper command:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

The wrapper runs:

- `pytest tests`
- `scripts/quality_gate.py`
- dry-run rendering for `python_cli_minimal`
- dry-run rendering for `csharp_desktop_minimal`
- dry-run rendering for `plc_tool_minimal`

The installed manual GitHub Local Verify workflow is:

`.github/workflows/local-verify.yml`

It runs `python -m pytest tests`, then exactly
`python scripts/run_eval.py` without report flags, then
`python scripts/quality_gate.py`, followed by the same three profile dry-runs.
It is `workflow_dispatch` only with `contents: read`, no secrets, no artifact
generation or upload, no automatic trigger, no required-check policy, and no
release-blocking semantics.

The local wrapper intentionally does not run the standalone eval. The local
wrapper and the manual GitHub Local Verify workflow are separate verification
surfaces and their results must be reported by name.

The pytest target is intentionally scoped to `tests` so local staging folders,
snapshot copies, and other untracked working artifacts do not affect collection.
`pytest.ini` applies the same `tests` collection target for direct
`python -m pytest` runs.
The hygiene and secret-scan gates also ignore `local/` because that folder is a
root-level local staging workspace, not the repository source of truth.

The AI readiness scanner is for readiness inspection only:

- Use `scripts/ai_readiness_scanner.py` for local read-only readiness review.
- Do not use scanner output to authorize writes or broaden task scope.
- Do not scan sibling repositories without explicit target-path approval.
- Do not treat domain flags as failures without review; they are conservative
  path-level indicators.
- Do not print private values, raw source excerpts, secrets, live config,
  customer data, broker data, mail bodies, IPs, ports, or equipment values.
- Keep scanner integration with `scripts/quality_gate.py`, generated reports,
  RAG/model tooling, and release gates out of the first CI hygiene task unless
  separately approved.

## Next Recommended Step

Use `docs/AUTHORITY_MANIFEST.json` for authority classes and
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` for sequencing. The next
repository-changing task after the cumulative digest-valid and remotely
verified checkpoint is a separately approved greenfield initialization.

The task closeout, rather than another recursive handoff commit, must confirm
the final same-source digest, V2 result, exact pushed SHA, and V3 Local Verify.
Greenfield initialization must then define the target path, `git init`, render,
initial authoring, verification, cleanup, and commit permissions explicitly.

Actual work-package manifests belong under ignored `local/work-packages/`.
They describe scope but do not authenticate approval. The greenfield path,
directory creation, `git init`, render, application implementation, worktree
creation, push, workflow dispatch, release, deployment, MCP execution, Hermes
execution bridge, and live behavior remain outside this source task.

## Historical / Deferred Candidate

Scenario-Simulator was previously evaluated as a downstream candidate and may
still be useful for architecture or P1 planning. It is deferred from the active
Stage 5B practical probe path because its next useful work is WPF/MVVM and
RSID-adjacent planning with a larger approval boundary. Do not treat
Scenario-Simulator production implementation, profile creation, example
creation, WPF shell work, project-file creation, UI work, simulation behavior,
or RSID behavior as approved by this handoff.
