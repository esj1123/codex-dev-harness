# AGENTS.md - csharp_desktop_minimal

## Profile

csharp_desktop

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

This example is a skeleton only. It does not contain a solution file, project file, PowerShell script, desktop app code, or user data.

## Work Policy

- Keep implementation gated by phase.
- Treat desktop file writes, settings, caches, and local databases as side effects.
- Mark build, test, and smoke checks as NOT RUN until scripts exist.
