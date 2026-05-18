# KNOWN_LIMITATIONS.md

## Purpose

Record known limitations for the current codex-dev-harness baseline.

## Current Limitations

- YAML parsing supports only the scalar subset used by the current template config files.
- Secret scanning is a lightweight heuristic and can produce false positives or false negatives.
- Example validation checks required files, config values, and required safety phrases; it does not execute real project builds.
- Example projects are skeletons only and intentionally contain no application code.
- Python CLI examples do not implement a CLI command.
- C# desktop examples do not include solution files, project files, or build/test/smoke scripts.
- PLC/device examples do not include polling, connection, tag maps, or control actions.
- CI workflow is not included yet.

## Safety Limitations

- The template can document safety policy but cannot enforce safety outside the repository.
- Live target writes remain out of scope.
- Real secrets, private raw inputs, device addresses, equipment ports, tag maps, and live parameters must remain outside the repo.

## Candidate Future Work

- Add `docs/CI_POLICY.md` to define CI expectations before creating an actual workflow.
- Add stricter config schema validation if template config grows beyond scalar values.
- Add release tagging guidance after P5 checks stabilize.
