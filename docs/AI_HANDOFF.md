# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum context needed to continue safely.

## Project Purpose

Reusable local-first template for governed AI/Codex development workflows.

## Current Phase

Parallel work-package control before greenfield implementation.

The repository has completed the governed template, Render Tier, standalone
local RAG, JSON evidence, Hermes preflight, release-evidence preflight, and
synthetic downstream-contract validation checkpoints described by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

The current synchronized remote baseline is
`7e605cff9a588723f9893c56894493f204d26213`. Its manual GitHub Local Verify
run checked out that exact commit and passed 589 tests, the 15-case standalone
eval, all 9 quality gates, and the three 16-file profile dry-runs with
`contents: read` and no artifact upload. Workflow run and job identifiers stay
in the task closeout instead of this tracked handoff.

Phase 10 release evidence remains valid historical source-basis evidence and
regeneration remains on `HOLD`. Phase 11 is complete through the Phase 11D.2
temporary synthetic filled-contract usage probe. No real downstream
repository, path, branch, source, command, render, write, or private data has
been selected or accessed.

The greenfield `local-data-quality-cli` target contract is selected without
repository creation or implementation. Before initialization, the harness is
adding machine-readable work-package conflict checks, integration-only
ownership, and V0-V3 verification tiers.

The current goal is `READY_FOR_PARALLEL_GREENFIELD_IMPLEMENTATION`: complete
the work-package control checkpoint, refresh the unchanged exact 34-source
digest once if required, and confirm one cumulative remote checkpoint before
creating or implementing the greenfield target.

## Source of Truth

Read in this order:
1. AGENTS.md
2. PRODUCT.md
3. MVP.md
4. STATUS.md
5. docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
6. ACCEPTANCE_TRACE.md
7. docs/SAFETY_POLICY.md
8. docs/VERIFICATION.md
9. docs/PROFILE_MATRIX.md
10. docs/AI_HANDOFF.md

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

Use `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` as the current sequencing
authority. Complete this checkpoint in order:

1. commit the work-package checker, focused tests, policy, and current-authority
   alignment as one integration change;
2. check the exact 34-source digest and refresh it once only when the expected
   stable sources are stale;
3. run V2 verification on the cumulative digest-containing tip;
4. push that tip once and confirm one V3 Local Verify run;
5. plan the separately approved greenfield initialization and a maximum of
   three disjoint feature lanes.

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
