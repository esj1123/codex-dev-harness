# ACCEPTANCE_TRACE - plc_tool_minimal

| id | category | requirement | evidence | status |
|---|---|---|---|---|
| PLC-001 | scope_contract | Example remains skeleton-only | README.md | PASS |
| PLC-002 | product_contract | Product and MVP docs exist | PRODUCT.md, MVP.md | PASS |
| PLC-003 | safety_contract | Simulator/mock first is explicit | SAFETY_POLICY.profile.md | PASS |
| PLC-004 | side_effect_contract | Live device write is prohibited | SAFETY_POLICY.profile.md | PASS |
| PLC-005 | security_contract | Equipment IP, port, tag, and live parameter details are prohibited | SAFETY_POLICY.profile.md | PASS |
| PLC-006 | quality_gate | Root quality gate passes | scripts/quality_gate.py output | PASS |
