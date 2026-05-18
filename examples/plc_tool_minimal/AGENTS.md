# AGENTS.md - plc_tool_minimal

## Profile

plc_or_device_tool

## Read Order

1. AGENTS.md
2. AGENTS.override.md
3. PRODUCT.md
4. MVP.md
5. STATUS.md
6. ACCEPTANCE_TRACE.md
7. SAFETY_POLICY.profile.md
8. VERIFICATION.profile.md

## Boundary

This example is a skeleton only. It does not contain device connection code, PLC logic, tag maps, control scripts, or real equipment configuration.

## Core Safety Rules

- Simulator/mock first.
- Live device write is prohibited.
- Read-only polling must be designed before any write concept.
- Equipment IP, port, tag, address, and live parameter details must not be committed.
