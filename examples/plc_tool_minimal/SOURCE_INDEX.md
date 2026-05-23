# SOURCE_INDEX.md

## Purpose

Track source categories for `plc_tool_minimal`.

This example is a docs-only regression skeleton. It does not include device code or live configuration.

## Source Table

| source_id | source type | owner | allowed use | sensitivity | evidence path | notes |
|---|---|---|---|---|---|---|
| SRC-001 | base template | codex-dev-harness | regression validation | public template material | `templates/base/` | Seed docs only |
| SRC-002 | plc_or_device_tool profile template | codex-dev-harness | regression validation | public template material | `profiles/plc_or_device_tool/` | Profile docs only |
| SRC-003 | simulator/mock concept | example skeleton | documentation only | synthetic | `SAFETY_POLICY.profile.md` | No live target |

## Source Rules

- Do not add device code.
- Do not add live configuration.
- Use simulator/mock first.
- Keep live behavior as prohibited in this skeleton.

