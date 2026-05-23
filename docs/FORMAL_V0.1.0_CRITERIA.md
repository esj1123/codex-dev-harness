# Formal v0.1.0 Criteria

## Purpose

Define the criteria for deciding whether codex-dev-harness is ready for a formal `v0.1.0` tag.

Formal `v0.1.0` has not been created.

## Entry Conditions

Formal `v0.1.0` should be considered only when all conditions are satisfied:

1. `v0.1.0-rc2` clean clone validation is PASS.
2. GitHub Release Draft is prepared.
3. At least one downstream application experiment is PASS.
4. Base template render experiment is PASS.
5. Regression examples remain synchronized.
6. `example_render_drift_gate` is PASS.
7. GitHub Actions workflow is not required.
8. No real application, PLC/device, or live-write code is added to the template baseline.
9. `ACCEPTANCE_TRACE.md` and `STATUS.md` match the latest state.

## Current Criteria Status

| condition | status | evidence |
|---|---|---|
| `v0.1.0-rc2` clean clone validation | PASS | `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md` |
| GitHub Release Draft prepared | PASS | `docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md` |
| Downstream application experiment | PASS | `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md` |
| Base template render experiment | PASS | `docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md` |
| Regression examples synchronized | PASS | `example_render_drift_gate` and example docs |
| No required GitHub Actions workflow | PASS | No workflow installed |
| No runtime/live-write code in baseline | PASS | Status and release records |
| Acceptance trace and status current | PASS | Updated with downstream experiment result |

## Not Required For Formal v0.1.0

These are not required before formal `v0.1.0`:

- Signed release.
- SBOM.
- Provenance bundle.
- GitHub Actions.
- Actual application implementation.

## Post-v0.1.0 Candidates

Potential work after formal `v0.1.0`:

- Eval harness.
- Release manifest.
- SBOM/provenance.
- Optional GitHub Actions adoption.
- Downstream project adoption pattern.

## Current Decision

Formal `v0.1.0` remains deferred until explicit release approval. The downstream application experiment condition is now satisfied.
