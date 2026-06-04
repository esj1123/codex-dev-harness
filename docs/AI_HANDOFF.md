# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum context needed to continue safely.

## Project Purpose

Reusable local-first template for governed AI/Codex development workflows.

## Current Phase

Stage 5B stock practical probe closeout handoff.

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
- Stage 4 optional CI decision: keep deferred and template-only.
- Stage 5A downstream transition decision.

The current direction is to keep `codex-dev-harness` frozen as the
local-first governed baseline after completing the Stage 5B stock-first flow:

1. target repository selection
2. `stock` practical probes #1-#5
3. probe closeout review

Scenario-Simulator remains an architecture/planning candidate, but it is not
the default practical probe target.

## Source of Truth

Read in this order:
1. AGENTS.md
2. PRODUCT.md
3. MVP.md
4. STATUS.md
5. ACCEPTANCE_TRACE.md
6. docs/SAFETY_POLICY.md
7. docs/VERIFICATION.md
8. docs/PROFILE_MATRIX.md
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

## Pending Risks

- Eval harness integration into `scripts/quality_gate.py`, CI, or release
  blocking remains deferred; the standalone local eval runner, eval gate
  wrapper, cases, tests, and explicit eval report evidence exist.
- Real audit log generation, validators, and automation remain deferred; the
  audit schema and policy exist.
- Release archive creation, publication, signing, tag movement, upload, and CI
  installation remain deferred; the local release verification wrapper,
  manifest/checksum artifacts, minimal SBOM, and provenance evidence exist.
- Optional design-stage pack remains manual-use-only and is not integrated into render, gate, or examples.
- Examples are skeletons only and intentionally contain no real application code.
- GitHub Actions workflow is not installed; CI remains optional.
- `plc_or_device_tool` actual target execution remains deferred and is not the
  next default stage.
- Scenario-Simulator remains a downstream architecture/planning candidate; do
  not add `profiles/scenario_simulator` or
  `examples/scenario_simulator_minimal` by default.
- The `stock` practical probe sequence is closed out. Probe #1-#5 evidence
  supports current task-contract discipline but does not justify another stock
  probe by default or immediate harness automation expansion.
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
- Keep scanner integration with `scripts/quality_gate.py`, CI, generated
  reports, RAG/model tooling, and release gates deferred unless separately
  approved.

## Next Recommended Step

Use `docs/STAGE_5B_STOCK_PRACTICAL_PROBE_CLOSEOUT.md`,
`docs/STAGE_5B_TARGET_REPO_SELECTION_AND_PROBE_PLAN.md`, and
`docs/NEXT_DIRECTION_DECISION.md` as the current handoff. The recommended next
work is a review-only decision on whether Probe #1-#5 justifies a minimal Code
Simplicity Addendum or whether no harness change is needed.

Practical next candidates:

- decide whether to add a minimal Code Simplicity Addendum or no harness change
  after reviewing Probe #1-#5 evidence
- keep Scenario-Simulator as a deferred architecture/planning candidate for a
  separate task selected under that repository's own rules
- keep `AI_HANDOFF`, `STATUS`, and `ACCEPTANCE_TRACE` aligned after any future
  evidence baseline changes
- preserve generated artifact source-basis versus artifact-containing commit
  semantics when documentation-only commits advance HEAD
- defer quality-gate eval integration, routine eval reports, audit log
  automation, release archives, signing, publication, workflows, artifact
  upload, required CI checks, new profiles, new examples, RAG/index/vector
  store or model tooling, optional CI installation, and runtime, application,
  device, or live-write behavior until separately approved
- do not start Probe #6 by default

## Historical / Deferred Candidate

Scenario-Simulator was previously evaluated as a downstream candidate and may
still be useful for architecture or P1 planning. It is deferred from the active
Stage 5B practical probe path because its next useful work is WPF/MVVM and
RSID-adjacent planning with a larger approval boundary. Do not treat
Scenario-Simulator production implementation, profile creation, example
creation, WPF shell work, project-file creation, UI work, simulation behavior,
or RSID behavior as approved by this handoff.
