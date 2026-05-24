# KNOWN_LIMITATIONS.md

## Purpose

Record known limitations for the current codex-dev-harness baseline after the formal `v0.1.0` release.

## Current Limitations

- YAML parsing supports only the scalar subset used by the current template config files.
- Secret scanning is a lightweight heuristic and can produce false positives or false negatives.
- Example projects are skeletons only and intentionally contain no real application code.
- Example validation checks required files, config values, and required safety phrases; it does not execute real project builds.
- Render drift checking is file-presence-only and does not compare rendered content.
- Python CLI examples do not implement a CLI command.
- C# desktop examples do not include solution files, project files, source files, or build/test/smoke scripts.
- PLC/device examples do not include polling, connection, tag maps, control actions, or live device write support.
- The eval harness is minimal and standalone; it is not wired into `quality_gate.py`, CI, or release blocking.
- GitHub Actions workflow is not installed.
- Release bundle and manifest policies exist, but no generator or artifact exists.
- Release manifests and checksum files are not generated.
- SBOM and provenance artifacts are not implemented.
- Optional design-stage pack is manual-use-only.
- Optional design-stage pack has no render integration.
- Optional design-stage pack has no gate integration.
- Optional design-stage pack has no example integration.

## Safety Limitations

- The template can document safety policy but cannot enforce safety outside the repository.
- Live target writes remain out of scope.
- Real secrets, private raw inputs, device addresses, equipment ports, tag maps, and live parameters must remain outside the repo.
- Downstream generated target output is outside this repository baseline and must be reviewed separately.

## Candidate Future Work

- Implement an eval harness only after explicit approval and concrete downstream failure modes.
- Implement release manifest/checksum generation only after explicit approval.
- Implement release bundle generation only after explicit approval.
- Add SBOM/provenance only if a distribution or compliance need appears.
- Actualize optional CI only if local-first verification is no longer enough.
- Split `docs_gate` into baseline, release-record, and optional-document groups if the required-doc list becomes too release-specific.
- Add stricter config schema validation if template config grows beyond scalar values.
- Add optional design-stage render integration only if manual-use friction appears.
- Add optional design-stage validation or gate support only after explicit approval.
- Add an optional design-stage example only after an integration decision.

## Non-Goals

- Do not add a GitHub Actions workflow as part of this limitation refresh.
- Do not expand or integrate the eval harness as part of this limitation refresh.
- Do not generate release bundles, manifests, checksums, or release archives as part of this limitation refresh.
- Do not create SBOM/provenance artifacts as part of this limitation refresh.
- Do not add a new profile or downstream application implementation as part of this limitation refresh.
- Do not implement optional design-stage render, gate, or example integration as part of this limitation refresh.
