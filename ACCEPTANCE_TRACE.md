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

| trace_id | category | requirement | evidence | evidence_path | status | notes |
|---|---|---|---|---|---|---|
| AT-001 | product_contract | P0 docs-only baseline is defined | README and MVP describe P0 scope | README.md, MVP.md | PASS | Initial baseline |
| AT-002 | scope_contract | No render script, quality gate code, examples, or real program code are created | Repository contains markdown docs/templates only | Repository file list | PASS | P0 constraint |
| AT-003 | safety_contract | Side-effect and private-data rules are documented | Safety policy exists | docs/SAFETY_POLICY.md | PASS | Policy-level only |
| AT-004 | repo_hygiene | Requested P0 files exist | File existence check | Repository file list | PASS | Initial baseline |

## Status Values

- PASS: evidence supports the requirement.
- FAIL: evidence contradicts the requirement.
- PARTIAL: evidence is incomplete.
- NOT RUN: verification was not executed.
