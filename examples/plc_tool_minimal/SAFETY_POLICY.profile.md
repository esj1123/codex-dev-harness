# SAFETY_POLICY.profile.md - plc_tool_minimal

## Core Safety Defaults

- Simulator/mock first.
- Live device write is prohibited.
- Read-only polling must be designed before any write concept.
- Explicit approval is required for any future live action.

## Prohibited Repository Content

Do not commit:
- Equipment IP addresses.
- Ports.
- Tag names or detailed tag maps.
- Device addresses.
- Live control parameters.
- Credentials, keys, or tokens.
- Real config files for device access.

## Prohibited Default Actions

- Write.
- Start.
- Stop.
- Reset.
- Mode change.
- Any control action against a live device.

## P3 Boundary

This example contains no device runtime code and no live equipment detail.
