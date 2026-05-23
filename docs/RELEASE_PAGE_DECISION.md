# Release Page Decision

## Purpose

Record the decision options for a GitHub Release page after the formal `v0.1.0` baseline.

This document does not create a GitHub Release page.

## Current State

GitHub Release page current state: NOT CREATED.

Source draft: `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md`.

The repository already has an annotated `v0.1.0` tag, release record, clean clone validation record, and local-first usage documentation. A GitHub Release page is therefore optional, not required for local-first use.

## Options

| option | meaning | tradeoff |
|---|---|---|
| no release page | Keep the repository tag and docs as the release record | Lowest maintenance; enough for local-first usage |
| draft only | Keep `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md` as the canonical draft | Useful for internal review without public publication |
| publish | Create a GitHub Release page from the draft | Useful for external/reference distribution but adds a publication surface |

## Recommendation

Publish only if external/reference distribution is needed.

Local-first use does not require a GitHub Release page. The current tag, release record, clean clone validation, local usage guide, and release draft are sufficient for local cloning and verification.

## Required Checks Before Publish

- Confirm `v0.1.0` tag target remains unchanged.
- Re-run local verification.
- Confirm no GitHub Actions workflow is required.
- Confirm no real application code, PLC/device code, live target write support, secrets, raw source, or live values are included.
- Confirm `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md` is still accurate.

## Current Decision

Decision: DEFER PUBLICATION.

The release page remains not created until there is an explicit downstream or external distribution need.
