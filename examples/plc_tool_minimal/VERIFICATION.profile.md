# VERIFICATION.profile.md - plc_tool_minimal

## Default Checks

- Template render: PASS when renderer can resolve base and plc_or_device_tool profile templates.
- Quality gate: PASS from repository root.
- Simulator/mock first: PASS in safety policy.
- Live device write prohibited: PASS in safety policy.
- Equipment detail exclusion: PASS in safety policy.

## NOT RUN

- Live polling is NOT RUN because no live target exists.
- Device write verification is NOT RUN because write is prohibited.
