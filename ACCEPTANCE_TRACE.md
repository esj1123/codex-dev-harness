# ACCEPTANCE_TRACE.md

## Purpose

Acceptance trace links each requirement to evidence. It is different from runtime trace. Runtime trace records execution flow; acceptance trace records whether a requirement is satisfied.

## Categories

- product_contract.
- scope_contract.
- runtime_contract.
- safety_contract.
- side_effect_contract.
- quality_gate.
- repo_hygiene.
- security_contract.

## Trace Table

| trace_id | phase | category | requirement | evidence | evidence_path | status | notes |
|---|---|---|---|---|---|---|---|
| AT-001 | P0 historical | product_contract | P0 docs-only baseline was defined | README and MVP described P0 scope | README.md, MVP.md | PASS | Historical baseline |
| AT-002 | P0 historical | scope_contract | P0 did not include render script, quality gate code, examples, or real program code | Initial repository contained markdown docs/templates only | Repository file list at P0 | PASS | Historical P0 constraint, not current state |
| AT-003 | current | product_contract | Current repo describes render script, quality gate, profile templates, and examples | Current state sections exist | README.md, STATUS.md | PASS | Current phase alignment |
| AT-004 | current | safety_contract | Side-effect and private-data rules are documented | Safety policy exists | docs/SAFETY_POLICY.md | PASS | Policy-level guard |
| AT-005 | current | quality_gate | Quality gate includes docs, repo hygiene, template schema, secret scan, and examples | Gate modules and quality gate runner exist | scripts/quality_gate.py, scripts/gates/ | PASS | P4 validation target |
| AT-006 | current | side_effect_contract | Render target guard rejects repo-internal targets outside examples/<name> | Guard and tests exist | scripts/render_template.py, tests/test_render_template.py | PASS | Examples only |
| AT-007 | current | security_contract | PLC/device example prohibits live device write and equipment details | Example safety policy exists | examples/plc_tool_minimal/SAFETY_POLICY.profile.md | PASS | Skeleton-only example |
| AT-008 | current | quality_gate | requirements-dev.txt exists and includes pytest | Dependency file exists | requirements-dev.txt | PASS | P5 release readiness |
| AT-009 | current | quality_gate | pytest command is documented | Verification commands documented | README.md, docs/VERIFICATION.md | PASS | P5 release readiness |
| AT-010 | current | product_contract | Release checklist exists | Release readiness checklist exists | docs/RELEASE_CHECKLIST.md | PASS | P5 release readiness |
| AT-011 | current | product_contract | Known limitations are documented | Known limitations document exists | docs/KNOWN_LIMITATIONS.md | PASS | P5 release readiness |
| AT-012 | current | quality_gate | Example config validation is covered by example_gate | example_gate validates template.config.yml values | scripts/gates/example_gate.py, tests/test_quality_gate.py | PASS | P5 release readiness |
| AT-013 | current | governance_audit | CI policy is documented without creating a workflow | CI policy draft exists | docs/CI_POLICY.md | PASS | Policy only, no workflow |
| AT-014 | current | product_contract | Local-first usage is documented | Local usage guide exists | docs/LOCAL_USAGE.md | PASS | P5.5 local usage readiness |
| AT-015 | current | scope_contract | Local release package boundary is documented | Local package guide exists | docs/LOCAL_RELEASE_PACKAGE.md | PASS | P5.5 local usage readiness |
| AT-016 | current | quality_gate | Local verification wrapper exists | PowerShell wrapper exists | scripts/run_local_verify.ps1 | PASS | P5.5 local usage readiness |
| AT-017 | current | governance_audit | CI remains optional and local verification first | CI policy and local usage docs say local-first | docs/CI_POLICY.md, docs/LOCAL_USAGE.md | PASS | No workflow created |
| AT-018 | current | governance_audit | P6 release candidate closeout is documented | Closeout document exists | docs/P6_RELEASE_CLOSEOUT.md | PASS | Release tag not created |
| AT-019 | current | quality_gate | Latest verified commit is recorded | STATUS records release candidate commit | STATUS.md | PASS | `aff39d65e716ad2830647fcf52026c00a911d482` |
| AT-020 | current | quality_gate | Local verification wrapper was run for release candidate | Latest verification records wrapper result | STATUS.md, docs/P6_RELEASE_CLOSEOUT.md | PASS | Local-first validation |
| AT-021 | current | product_contract | Release notes are documented | Release notes exist for the recommended release candidate tag | docs/RELEASE_NOTES_v0.1.0-rc1.md | PASS | Tag not created |

## Status Values

- PASS: evidence supports the requirement.
- FAIL: evidence contradicts the requirement.
- PARTIAL: evidence is incomplete.
- NOT RUN: verification was not executed.
