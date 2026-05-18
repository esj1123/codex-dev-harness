# ROADMAP.md

## Phase Status

| phase | status | summary |
|---|---|---|
| P0: Docs Only | completed | Historical baseline for root docs, policies, and base template placeholders |
| P1: Profile Templates | completed | Added `python_cli`, `csharp_desktop`, and `plc_or_device_tool` profile templates |
| P2: Render and Base Quality Gate | completed | Added config-driven renderer and base quality gates |
| P3: Example Skeletons | completed | Added minimal docs-only examples for three profiles |
| P4: Example Gate Validation | in progress | Add example-specific gate coverage and render target guard hardening |
| P5: Release Readiness | not started | Define CI/dependency guidance and release checklist |
| P6: Release | not started | Tag a reusable baseline and document known limitations |

## P0: Docs Only

Goal: establish the documentation baseline and template contract.

Done:
- Core markdown files exist.
- docs/ policy files exist.
- templates/base placeholders exist.
- P0 scope and non-goals were explicit.

## P1: Profile Templates

Goal: add profile-specific template variants.

Done:
- `python_cli` profile exists.
- `csharp_desktop` profile exists.
- `plc_or_device_tool` profile exists.

## P2: Render and Base Quality Gate

Goal: render selected templates from a config file and run base repository checks.

Done:
- `scripts/render_template.py` exists.
- `scripts/quality_gate.py` exists.
- Docs, repo hygiene, template schema, and secret scan gates exist.

## P3: Examples

Goal: validate the template against minimal example projects.

Done:
- `examples/python_cli_minimal` exists.
- `examples/csharp_desktop_minimal` exists.
- `examples/plc_tool_minimal` exists.
- Examples are skeleton-only and do not contain application code.

## P4: Example Gate Validation

Goal: include example skeletons in the quality gate.

Done when:
- `scripts/gates/example_gate.py` validates required example files.
- Profile-specific safety phrases are checked.
- Renderer allows only `examples/<name>` as repo-internal target.

## P5: Release Readiness

Goal: prepare the repository for reusable baseline release.

Candidate work:
- Dependency setup instructions for pytest.
- CI workflow decision.
- Release checklist.
- Known limitations document.

## P6: Release

Goal: tag a reusable baseline and document known limitations.
