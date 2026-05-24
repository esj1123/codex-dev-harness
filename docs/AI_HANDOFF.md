# AI_HANDOFF.md

## Purpose

Provide the next AI/Codex worker with the minimum context needed to continue safely.

## Project Purpose

Reusable local-first template for governed AI/Codex development workflows.

## Current Phase

Post v0.1.0 Stage 1 docs-only governance gap closure.

The historical P0 docs-only baseline is complete. The repository now includes
documentation, base templates, profile templates, render tooling, quality gates,
tests, minimal example skeletons, and documentation-only governance policies.

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
- regression examples under `examples/`
- pytest tests under `tests/`
- Stage 1 governance policy docs:
  - `docs/CHANGE_CONTROL.md`
  - `docs/HUMAN_APPROVALS.md`
  - `docs/EVAL_POLICY.md`
  - `docs/AUDIT_LOG_POLICY.md`

## Pending Risks

- Eval harness implementation remains deferred.
- Audit log schema and audit log implementation remain deferred.
- Release verification wrapper, release manifest, checksum artifacts, SBOM, and provenance remain deferred.
- Optional design-stage pack remains manual-use-only and is not integrated into render, gate, or examples.
- Examples are skeletons only and intentionally contain no real application code.
- GitHub Actions workflow is not installed; CI remains optional.

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

## Next Recommended Step

Keep the Stage 1 governance baseline documentation-only unless a separate owner
approval explicitly opens an implementation surface.

Practical next candidates:

- keep `AI_HANDOFF`, `STATUS`, and `ACCEPTANCE_TRACE` aligned after governance changes
- decide whether prompt task contract templates should become a separate approved task
- defer eval harness, audit schema, release manifest/checksum, SBOM/provenance, workflows, new profiles, examples, and live-write behavior until separately approved
