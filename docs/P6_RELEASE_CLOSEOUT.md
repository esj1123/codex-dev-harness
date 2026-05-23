# P6 Release Closeout

## Purpose

This document records the P6 release candidate closeout state for the local-first Agentic Development Repo Template baseline.

## Candidate

- Historical pre-tag candidate commit: `aff39d65e716ad2830647fcf52026c00a911d482`
- Final tag target commit: `10bccadd15be9401847620eba61d3c8c4117962d`
- Tag name: `v0.1.0-rc1`
- Tag object: `9ca08efbd43cd2c5defba7875efbd7ca702c6166`
- Release tag: CREATED
- GitHub Release page: NOT CREATED
- CI workflow: NOT INSTALLED

## Local Verification

| check | result | evidence |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest, quality gate, and 3 render dry-runs passed |
| `python -m pytest` | PASS | 16 passed through the local Python runtime used by the verification wrapper |
| `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, secret scan passed through the local Python runtime |
| python_cli render dry-run | PASS | `examples/python_cli_minimal/template.config.yml` rendered in dry-run mode |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal/template.config.yml` rendered in dry-run mode |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal/template.config.yml` rendered in dry-run mode |

## Release References

- Known limitations: `docs/KNOWN_LIMITATIONS.md`
- Release checklist: `docs/RELEASE_CHECKLIST.md`
- Release notes: `docs/RELEASE_NOTES_v0.1.0-rc1.md`
- RC2 release notes: `docs/RELEASE_NOTES_v0.1.0-rc2.md`
- Release record: `docs/RELEASE_RECORD_v0.1.0-rc1.md`
- RC2 release record: `docs/RELEASE_RECORD_v0.1.0-rc2.md`
- Formal v0.1.0 release record: `docs/RELEASE_RECORD_v0.1.0.md`
- RC2 candidate closeout: `docs/RC2_CANDIDATE_CLOSEOUT.md`
- Clean clone validation record: `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md`
- RC2 clean clone validation record: `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md`
- GitHub Release Draft: `docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md`
- Formal v0.1.0 criteria: `docs/FORMAL_V0.1.0_CRITERIA.md`
- Downstream experiment: `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md`
- Local target experiment record: `docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md`
- Base template local target experiment record: `docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md`
- Optional GitHub Actions guide: `docs/OPTIONAL_GITHUB_ACTIONS.md`
- Local usage guide: `docs/LOCAL_USAGE.md`
- Local package boundary: `docs/LOCAL_RELEASE_PACKAGE.md`
- Architecture: `docs/ARCHITECTURE.md`
- Validation scope: `docs/VALIDATION_SCOPE.md`
- Template extension policy: `docs/TEMPLATE_EXTENSION_POLICY.md`
- Domain adaptation guide: `docs/DOMAIN_ADAPTATION_GUIDE.md`
- Local-first ADR: `docs/adr/ADR-0001-local-first.md`
- Base-template-over-domain-profile ADR: `docs/adr/ADR-0002-base-template-over-domain-profile.md`
- Approval-gated side-effect ADR: `docs/adr/ADR-0003-approval-gated-side-effect.md`

## Base Template Strengthening

- Source index, project boundary, data scope, phase plan, and approvals are base template surfaces.
- Existing profiles remain regression/example variants.
- Scenario simulator is recorded as a downstream application candidate, not a built-in profile.
- New profile creation remains approval-gated and should require repeated reuse evidence.
- Regression examples are synchronized with the extended base template docs.
- Render drift is checked at file-presence level for regression examples.
- The extended base template was rendered into a separate generic local target with no profile selected.

## RC2 Candidate State

- `v0.1.0-rc1` remains the existing tagged baseline.
- `v0.1.0-rc1` still points to `10bccadd15be9401847620eba61d3c8c4117962d`.
- `v0.1.0-rc2` is the current tagged candidate at `67ead73628c8ff7b15e91d2ba608efbdbb8de81e`.
- `v0.1.0-rc2` tag object: `569b992b390a672cd8a321963a963ff0cbe47976`.
- `v0.1.0-rc2` tag: CREATED.
- `v0.1.0-rc2` clean clone validation: COMPLETED.
- GitHub Release Draft: DOCUMENTED, not published.
- Downstream scenario simulator design candidate experiment: COMPLETED as base-template-only downstream target.
- Formal `v0.1.0` tag: CREATED at `43bbf001e1d2770466b41d5b8366f289b972a00b`.
- Formal `v0.1.0` tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`.
- Formal `v0.1.0` release record: DOCUMENTED.

## Remaining Decisions

- Clean clone validation from the `v0.1.0-rc1` tag: COMPLETED.
- Decide whether to draft a GitHub Release page without changing the tag.
- Local target project experiment with `python_cli`: COMPLETED.
- Generic/base template local target experiment: COMPLETED.
- Clean clone validation for `v0.1.0-rc2`: COMPLETED.
- Decide whether to create a GitHub Release page from `docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md` without changing tags.
- Downstream application experiment: COMPLETED.
- Formal `v0.1.0` tag: CREATED.
- Decide whether to run clean clone validation from the formal `v0.1.0` tag.
- Decide whether to run additional profile experiments.
- Decide whether to run downstream application experiments through the base template extension surfaces.

## Scope Confirmation

- Release tag `v0.1.0-rc1` was created.
- Release tag `v0.1.0-rc2` was created.
- Formal release tag `v0.1.0` was created.
- No GitHub Release page was created.
- No GitHub Actions workflow was installed.
- GitHub Release Draft was documented.
- Formal v0.1.0 criteria were documented.
- Clean clone validation was documented.
- Local target experiment was documented.
- Base template architecture and extension policy were documented.
- No scenario simulator profile was added.
- Scenario simulator design was tested only as a downstream candidate.
- Regression examples include the extended base docs.
- Generic/base template local target experiment was documented.
- No new profile was added.
- No real application code was added.
- No PLC/device code was added.
- No live target write support was added.
- Render target guards were not relaxed.
