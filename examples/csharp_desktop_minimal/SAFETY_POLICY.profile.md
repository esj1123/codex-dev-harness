# SAFETY_POLICY.profile.md - csharp_desktop_minimal

## Safety Defaults

- Do not include user-specific absolute paths, credentials, private documents, or machine-specific data.
- Treat desktop file writes, settings, caches, and local databases as side effects.
- Use safe synthetic data for future smoke procedures.

## P3 Boundary

This example contains no desktop runtime code and no local user data.
