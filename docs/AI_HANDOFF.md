# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum context needed to continue safely.

## Project Purpose

Reusable local-first template for governed AI/Codex development workflows.

## Current Phase

Capability implementation roadmap handoff.

The historical P0 docs-only baseline is complete. The repository now includes
documentation, base templates, profile templates, render tooling, quality gates,
tests, minimal example skeletons, standalone local eval tooling, a standalone
local read-only AI readiness scanner, local release evidence generators,
generated local release evidence artifacts, and documentation-only governance
policies.

Stages 1-5A are complete:

- Stage 1 documentation drift cleanup.
- Stage 2 local post-v0.1.0 evidence baseline.
- Stage 3 eval integration decision: keep standalone.
- Stage 4 optional CI decision: historical template-only risk evidence.
- Stage 5A downstream transition decision.

The current implementation direction is defined by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`. The owner intent is to eventually
implement CI, RAG, audit / trace / receipt schema, eval/report integration,
MCP tool boundary, Hermes sidecar, release automation / provenance, and
downstream product integration.

The first implementation target after the roadmap is read-only CI +
verification hygiene. Historical optional/deferred decisions and the Stage 5B
stock practical probe records remain risk evidence and sequencing evidence,
not permanent blockers.

Scenario-Simulator remains an architecture/planning candidate, but it is not
the default implementation target.

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

- Eval/report integration is a roadmap target after audit / trace / receipt
  schema. The standalone local eval runner, eval gate wrapper, cases, tests,
  and explicit eval report evidence exist.
- Audit / trace / receipt schema is the second roadmap implementation target.
  Real audit log generation, validators, and automation still require separate
  phase approval.
- Release automation / provenance is a later roadmap target. Release archive
  creation, publication, signing, tag movement, upload, and CI release behavior
  still require separate approval; the local release verification wrapper,
  manifest/checksum artifacts, minimal SBOM, and provenance evidence exist.
- Optional design-stage pack remains manual-use-only and is not integrated into render, gate, or examples.
- Examples are skeletons only and intentionally contain no real application code.
- GitHub Actions workflow is not installed. Read-only CI + verification hygiene
  is the first implementation target and remains approval-gated.
- `plc_or_device_tool` actual target execution remains deferred and is not the
  next default stage.
- Scenario-Simulator remains a downstream architecture/planning candidate; do
  not add `profiles/scenario_simulator` or
  `examples/scenario_simulator_minimal` by default.
- The `stock` practical probe sequence is closed out. Probe #1-#5 evidence
  supports current task-contract discipline and informs verification hygiene;
  it is not a permanent blocker to the roadmap targets.
- AI readiness scanner integration into `scripts/quality_gate.py`, generated
  report artifacts, and sibling repository scans remain deferred unless
  separately approved.

## Verification Status

Current local verification command:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

The wrapper runs:

- `pytest tests`
- `scripts/quality_gate.py`
- dry-run rendering for `python_cli_minimal`
- dry-run rendering for `csharp_desktop_minimal`
- dry-run rendering for `plc_tool_minimal`

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

Use `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` as the current implementation
handoff. The recommended next work is Phase 3: read-only CI + verification
hygiene.

Practical next candidates:

- create the smallest approved read-only CI or CI-adjacent verification hygiene
  path that mirrors existing local verification
- keep Scenario-Simulator as a deferred architecture/planning candidate for a
  separate task selected under that repository's own rules
- keep `AI_HANDOFF`, `STATUS`, and `ACCEPTANCE_TRACE` aligned after any future
  evidence baseline changes
- preserve generated artifact source-basis versus artifact-containing commit
  semantics when documentation-only commits advance HEAD
- keep audit automation, eval quality-gate integration, routine eval reports,
  release archives, signing, publication, artifact upload, required CI checks,
  new profiles, new examples, RAG/index/vector store or model tooling,
  MCP/Hermes implementation, downstream product integration, and runtime,
  application, device, or live-write behavior out of the CI hygiene task unless
  separately approved
- do not start Probe #6 by default

## Historical / Deferred Candidate

Scenario-Simulator was previously evaluated as a downstream candidate and may
still be useful for architecture or P1 planning. It is deferred from the active
Stage 5B practical probe path because its next useful work is WPF/MVVM and
RSID-adjacent planning with a larger approval boundary. Do not treat
Scenario-Simulator production implementation, profile creation, example
creation, WPF shell work, project-file creation, UI work, simulation behavior,
or RSID behavior as approved by this handoff.
