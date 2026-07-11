# KNOWN_LIMITATIONS.md

## Purpose

Record known limitations for the current codex-dev-harness baseline after the formal `v0.1.0` release.

## Current Limitations

- YAML parsing supports only the scalar subset used by the current template config files.
- Secret scanning is a lightweight heuristic and can produce false positives or false negatives.
- Example projects are skeletons only and intentionally contain no real application code.
- Example validation checks required files, config values, and required safety phrases; it does not execute real project builds.
- Curated example render drift checking is file-presence-only and does not compare rendered content.
- Golden render fixture checking covers one synthetic rendered target for content-level drift.
- Python CLI examples do not implement a CLI command.
- C# desktop examples do not include solution files, project files, source files, or build/test/smoke scripts.
- PLC/device examples do not include polling, connection, tag maps, control actions, or live device write support.
- The eval harness is minimal and standalone; it is not wired into `quality_gate.py`, CI, or release blocking.
- The installed Local Verify GitHub Actions workflow is manual
  `workflow_dispatch` and read-only; automatic push/PR triggers, required-check
  policy, and artifact upload remain absent.
- Release manifest and full-bundle checksum generation plus read-only canonical
  checksum verification exist as local-only evidence; broader release archive,
  publication, signing, and upload behavior is not implemented.
- The release verification wrapper exists as a local-only command; it does not
  create release archives, publish releases, sign artifacts, move tags, upload
  artifacts, or install CI workflows.
- Generated manifest, checksum, eval report, SBOM, and provenance files are
  local evidence only; no release archive is generated.
- SBOM and provenance generators and artifacts exist as minimal local evidence;
  external metadata lookup, certification, signing, publication, and CI
  attestation are not implemented.
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

- Expand or integrate the eval harness only after explicit approval and
  concrete downstream failure modes.
- Expand release verification into broader release bundle/archive generation
  only after explicit approval.
- Expand SBOM/provenance beyond the minimal local generators only after
  explicit approval and a concrete distribution, audit, or compliance need.
- Broaden the manual read-only Local Verify workflow only after separate owner
  approval names the exact triggers, permissions, required-check policy,
  commands, and exclusions.
- Split `docs_gate` into baseline, release-record, and optional-document groups if the required-doc list becomes too release-specific.
- Add stricter config schema validation if template config grows beyond scalar values.
- Add optional design-stage render integration only if manual-use friction appears.
- Add optional design-stage validation or gate support only after explicit approval.
- Add an optional design-stage example only after an integration decision.

## Non-Goals

- Do not broaden GitHub Actions workflows as part of this limitation refresh.
- Do not expand or integrate the eval harness as part of this limitation refresh.
- Do not generate release bundles, release archives, or refreshed release
  evidence artifacts as part of this limitation refresh.
- Do not add a new profile or downstream application implementation as part of this limitation refresh.
- Do not implement optional design-stage render, gate, or example integration as part of this limitation refresh.
