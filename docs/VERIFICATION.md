# VERIFICATION.md

## Purpose

Define verification expectations for this template repository.

## P0 Verification Checklist

- Requested files exist.
- README and AGENTS read order match.
- P0 docs-only scope is stated.
- No render script exists.
- No quality gate implementation exists.
- No example implementation exists.
- No real application code exists.
- No secrets or private data are included.

## Verification Mesh

P0 uses policy-level verification only.

Future verification layers may include:
- Unit tests.
- Smoke tests.
- Runtime trace.
- Acceptance trace.
- Policy validation.
- Audit evidence.

## NOT RUN Principle

If a check was not executed, mark it as NOT RUN with a reason. Do not imply success for checks that were not run.
