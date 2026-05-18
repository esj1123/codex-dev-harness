# MVP.md

## MVP Goal

Maintain a reusable AI/Codex development repo template that combines documentation contracts, profile templates, dry-run rendering, quality gates, and minimal example validation.

## Current Must Have

- Clear repository purpose.
- AI/Codex operating instructions.
- Product and MVP contract.
- Roadmap and status document.
- Acceptance trace document.
- Code review note.
- Harness specification.
- Profile matrix.
- Safety policy.
- AI handoff document.
- Verification document.
- Base templates for core markdown files.
- Profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`.
- Render script for config-driven dry-run rendering.
- Quality gate covering docs, repo hygiene, template schema, secret scan, and examples.
- Minimal example skeletons for Python CLI, C# desktop, and PLC/device tool profiles.

## Historical P0 Out of Scope

At P0, render script, quality gate implementation, smoke test implementation, example projects, real program code, and publishing automation were out of scope. Render script, quality gate, profile templates, and example skeletons have since been added.

## Still Out of Scope

- Real program implementation.
- Real PLC/device code.
- Live target writes.
- Secret or live config generation.
- Publishing automation.

## Current Acceptance Criteria

- All root contract files exist.
- README and AGENTS read order match exactly.
- Historical P0 scope is described as completed baseline, not current absence.
- Safety policy covers side effects and private data.
- Verification document defines current executable checks.
- Templates are markdown placeholders, not generated application code.
- Example skeletons include profile safety policies and explicit NOT RUN status for missing runtime checks.
