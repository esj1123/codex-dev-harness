# ARCHITECTURE.md

## Purpose

Describe codex-dev-harness as a general local-first template system for governed agentic development.

The repository is not a downstream application. It provides reusable documents, templates, policies, render tooling, and validation gates that can be adapted to many project types without creating project-specific profiles for every domain.

## Control Plane

The control plane defines the project contract and operating rules:
- `AGENTS.md`
- `PRODUCT.md`
- `MVP.md`
- `ROADMAP.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `code_review.md`

These files tell an agent what the project is, what is in scope, what is out of scope, what evidence is required, and how closeout should be recorded.

## Template Plane

The template plane contains base files that should be useful across project types:
- `templates/base/AGENTS.md.template`
- `templates/base/README.md.template`
- `templates/base/PRODUCT.md.template`
- `templates/base/MVP.md.template`
- `templates/base/STATUS.md.template`
- `templates/base/ACCEPTANCE_TRACE.md.template`
- `templates/base/SOURCE_INDEX.md.template`
- `templates/base/PROJECT_BOUNDARY.md.template`
- `templates/base/DATA_SCOPE.md.template`
- `templates/base/PHASE_PLAN.md.template`
- `templates/base/APPROVALS.md.template`

The base template is the preferred place for broadly reusable controls such as source indexing, project boundary definition, data scope, phase planning, and approval records.

## Optional Profile Plane

Profiles are optional variants for recurring workflow shapes. Current profiles are regression/example variants:
- `python_cli`
- `csharp_desktop`
- `plc_or_device_tool`

Profiles should not be created for every downstream project type. A profile is justified only when the repo needs a durable, repeated, safety-relevant variation with its own validation example.

## Optional Pack Plane

Optional packs are reusable document packs that are not part of the base render path and are not profiles.

The current optional pack is the optional design-stage pack:
- `templates/optional/design_stage/`
- `docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md`
- `docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md`
- `docs/OPTIONAL_DESIGN_STAGE_PACK_INTEGRATION_DECISION.md`

Current optional design-stage pack state:

- Template files exist.
- Usage guide exists.
- Review record is refreshed.
- Manual feedback 001 and 002 are documented.
- All seven optional design-stage templates have PASS manual-use evidence.
- Manual-use-only baseline is closed.
- Render integration is deferred.
- Gate integration is deferred.
- Example integration is deferred.

The optional design-stage pack is not a profile, not a downstream application, and not part of the base render behavior. Future render, gate, or example integration requires a separate explicit owner approval.

## Render Plane

The render plane is local-first and explicit:
- `scripts/render_template.py`
- `template.config.example.yml`
- profile-specific `template.config.yml` files in examples

Rendering supports dry-run first. The renderer refuses to write into the template repository except for controlled `examples/<name>` validation targets. Real downstream use should render into a separate target folder.

## Verification/Gate Plane

The verification plane checks the template system before release or adoption:
- `scripts/quality_gate.py`
- `scripts/gates/docs_gate.py`
- `scripts/gates/repo_hygiene_gate.py`
- `scripts/gates/template_schema_gate.py`
- `scripts/gates/example_gate.py`
- `scripts/gates/secret_scan_gate.py`
- `tests/`

Current verification covers required docs, required base templates, template config schema, example config consistency, simple private-pattern scanning, and regression examples.

## Side-Effect Boundary

The default boundary is read-only first, dry-run first, and approval-gated before mutation. The template must not add:
- real application code
- C# solution or project files
- PLC/device code
- live target write support
- live configuration
- private input
- secret values
- equipment connection details

Downstream projects can use the generated docs to request approval before crossing any side-effect boundary.

## Release/Record Plane

Release evidence is tracked as documents:
- `docs/RELEASE_CHECKLIST.md`
- `docs/RELEASE_NOTES_v0.1.0-rc1.md`
- `docs/RELEASE_NOTES_v0.1.0-rc2.md`
- `docs/RELEASE_RECORD_v0.1.0-rc1.md`
- `docs/RELEASE_RECORD_v0.1.0-rc2.md`
- `docs/RELEASE_RECORD_v0.1.0.md`
- `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md`
- `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md`
- `docs/CLEAN_CLONE_VALIDATION_v0.1.0.md`
- `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md`
- `docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md`
- `docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md`
- `docs/POST_V0.1.0_ROADMAP.md`
- `docs/RELEASE_PAGE_DECISION.md`
- `docs/LOCAL_PACKAGE_CHECKLIST.md`
- `docs/OPTIONAL_EVAL_HARNESS_PLAN.md`
- `docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md`

Release records document what happened. They do not create tags, move tags, publish GitHub Releases, or enable CI.

Current release state:

- Formal `v0.1.0` tag exists and is recorded.
- Formal `v0.1.0` clean clone validation is recorded.
- Formal GitHub Release draft exists, but the GitHub Release page is still NOT CREATED.
- Downstream adoption run and downstream doc review checklist are recorded.
- Post-v0.1.0 roadmap, release page decision, local package checklist, and optional eval harness plan are recorded.
- GitHub Actions workflow is still NOT INSTALLED.
- Eval harness, SBOM, provenance, release manifest/checksum, and optional CI actualization remain future/optional work.

## Optional CI Plane

GitHub Actions are optional. The repository includes a disabled template under `templates/ci/`, but no `.github/workflows` file is installed by default.

CI, if adopted later, should only run tests, quality gates, and render dry-runs. It must not deploy, create runtime code, connect to live targets, or perform release actions without explicit approval.

## Downstream Application Boundary

Complex projects such as a scenario simulator design are downstream application candidates, not built-in profiles by default.

A downstream project should use the base templates to define:
- source index
- project boundary
- data scope
- phase plan
- approvals

Raw source bulk copy, sensitive values, equipment connection details, and live parameters must stay out of this repository.
