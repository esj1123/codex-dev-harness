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

## Status Values

- PASS: evidence supports the requirement.
- FAIL: evidence contradicts the requirement.
- PARTIAL: evidence is incomplete.
- NOT RUN: verification was not executed.
