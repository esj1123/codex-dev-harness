# SAFETY_POLICY.profile.md - python_cli_minimal

## Safety Defaults

- Use synthetic fixtures only.
- Do not include private raw input, secrets, local credential files, or real service tokens.
- Treat file writes as side effects unless they are explicit template example files.
- External API mutation is out of scope.

## P3 Boundary

This example contains no runtime code and no live target behavior.
