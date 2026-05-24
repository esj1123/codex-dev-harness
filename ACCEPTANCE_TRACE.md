# ACCEPTANCE_TRACE.md

## Purpose

Acceptance trace links each requirement to evidence. It is different from runtime trace. Runtime trace records execution flow; acceptance trace records whether a requirement is satisfied.

## Categories

- product_contract.
- scope_contract.
- runtime_contract.
- safety_contract.
- side_effect_contract.
- quality_gate.
- repo_hygiene.
- security_contract.

## Trace Table

| trace_id | phase | category | requirement | evidence | evidence_path | status | notes |
|---|---|---|---|---|---|---|---|
| AT-001 | P0 historical | product_contract | P0 docs-only baseline was defined | README and MVP described P0 scope | README.md, MVP.md | PASS | Historical baseline |
| AT-002 | P0 historical | scope_contract | P0 did not include render script, quality gate code, examples, or real program code | Initial repository contained markdown docs/templates only | Repository file list at P0 | PASS | Historical P0 constraint, not current state |
| AT-003 | current | product_contract | Current repo describes render script, quality gate, profile templates, and examples | Current state sections exist | README.md, STATUS.md | PASS | Current phase alignment |
| AT-004 | current | safety_contract | Side-effect and private-data rules are documented | Safety policy exists | docs/SAFETY_POLICY.md | PASS | Policy-level guard |
| AT-005 | current | quality_gate | Quality gate includes docs, repo hygiene, template schema, secret scan, and examples | Gate modules and quality gate runner exist | scripts/quality_gate.py, scripts/gates/ | PASS | P4 validation target |
| AT-006 | current | side_effect_contract | Render target guard rejects repo-internal targets outside examples/<name> | Guard and tests exist | scripts/render_template.py, tests/test_render_template.py | PASS | Examples only |
| AT-007 | current | security_contract | PLC/device example prohibits live device write and equipment details | Example safety policy exists | examples/plc_tool_minimal/SAFETY_POLICY.profile.md | PASS | Skeleton-only example |
| AT-008 | current | quality_gate | requirements-dev.txt exists and includes pytest | Dependency file exists | requirements-dev.txt | PASS | P5 release readiness |
| AT-009 | current | quality_gate | pytest command is documented | Verification commands documented | README.md, docs/VERIFICATION.md | PASS | P5 release readiness |
| AT-010 | current | product_contract | Release checklist exists | Release readiness checklist exists | docs/RELEASE_CHECKLIST.md | PASS | P5 release readiness |
| AT-011 | current | product_contract | Known limitations are documented | Known limitations document exists | docs/KNOWN_LIMITATIONS.md | PASS | P5 release readiness |
| AT-012 | current | quality_gate | Example config validation is covered by example_gate | example_gate validates template.config.yml values | scripts/gates/example_gate.py, tests/test_quality_gate.py | PASS | P5 release readiness |
| AT-013 | current | governance_audit | CI policy is documented without creating a workflow | CI policy draft exists | docs/CI_POLICY.md | PASS | Policy only, no workflow |
| AT-014 | current | product_contract | Local-first usage is documented | Local usage guide exists | docs/LOCAL_USAGE.md | PASS | P5.5 local usage readiness |
| AT-015 | current | scope_contract | Local release package boundary is documented | Local package guide exists | docs/LOCAL_RELEASE_PACKAGE.md | PASS | P5.5 local usage readiness |
| AT-016 | current | quality_gate | Local verification wrapper exists | PowerShell wrapper exists | scripts/run_local_verify.ps1 | PASS | P5.5 local usage readiness |
| AT-017 | current | governance_audit | CI remains optional and local verification first | CI policy and local usage docs say local-first | docs/CI_POLICY.md, docs/LOCAL_USAGE.md | PASS | No workflow created |
| AT-018 | current | governance_audit | P6 release candidate closeout is documented | Closeout document exists | docs/P6_RELEASE_CLOSEOUT.md | PASS | Updated after tag creation |
| AT-019 | current | quality_gate | Latest verified commit is recorded | STATUS records release candidate commit | STATUS.md | PASS | `10bccadd15be9401847620eba61d3c8c4117962d` |
| AT-020 | current | quality_gate | Local verification wrapper was run for release candidate | Latest verification records wrapper result | STATUS.md, docs/P6_RELEASE_CLOSEOUT.md | PASS | Local-first validation |
| AT-021 | current | product_contract | Release notes are documented | Release notes exist for the recommended release candidate tag | docs/RELEASE_NOTES_v0.1.0-rc1.md | PASS | Retained after tag creation |
| AT-022 | current | governance_audit | v0.1.0-rc1 tag was created | Release record captures created tag state | docs/RELEASE_RECORD_v0.1.0-rc1.md | PASS | GitHub Release page not created |
| AT-023 | current | governance_audit | Tag target commit is recorded | Release record and STATUS capture target commit | docs/RELEASE_RECORD_v0.1.0-rc1.md, STATUS.md | PASS | `10bccadd15be9401847620eba61d3c8c4117962d` |
| AT-024 | current | product_contract | Release record exists | Post-release record exists | docs/RELEASE_RECORD_v0.1.0-rc1.md | PASS | Tag not modified |
| AT-025 | current | quality_gate | v0.1.0-rc1 clean clone validation is documented | Clean clone validation record exists | docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md | PASS | Bare python launcher blocked, wrapper runtime passed |
| AT-026 | current | governance_audit | Clean clone checkout target is recorded | Checkout target and tag target are recorded | docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md | PASS | `10bccadd15be9401847620eba61d3c8c4117962d` |
| AT-027 | current | quality_gate | Local verification passed from clean clone | Wrapper verification passed from tag checkout | docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md | PASS | pytest 16 passed, quality gate passed, render dry-runs passed |
| AT-028 | current | product_contract | Local target experiment is documented | Local target experiment record exists | docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md | PASS | Separate temporary target |
| AT-029 | current | quality_gate | python_cli profile was tested against a separate local target | Dry-run and actual render results are recorded | docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md | PASS | 11 Markdown docs generated |
| AT-030 | current | side_effect_contract | Actual render result is recorded | Actual render result and safety checks are documented | docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md | PASS | No runtime code or live-write support generated |
| AT-031 | current | product_contract | Base template architecture is documented | Architecture document exists | docs/ARCHITECTURE.md | PASS | Local-first planes and downstream boundary are documented |
| AT-032 | current | quality_gate | Validation scope distinguishes regression examples from downstream candidates | Validation scope document exists | docs/VALIDATION_SCOPE.md | PASS | Scenario simulator is downstream candidate, not profile |
| AT-033 | current | governance_audit | Template extension policy is documented | Extension policy and ADR exist | docs/TEMPLATE_EXTENSION_POLICY.md, docs/adr/ADR-0002-base-template-over-domain-profile.md | PASS | Profile creation is approval-gated |
| AT-034 | current | scope_contract | Base template includes source index, project boundary, data scope, phase plan, and approvals | Base templates exist and template schema gate requires them | templates/base/, scripts/gates/template_schema_gate.py | PASS | Base template supports complex downstream projects |
| AT-035 | current | side_effect_contract | Approval-gated side-effect policy is documented | Side-effect ADR and approvals template exist | docs/adr/ADR-0003-approval-gated-side-effect.md, templates/base/APPROVALS.md.template | PASS | Read-only and dry-run first |
| AT-036 | current | scope_contract | Scenario simulator profile was not created | Profiles and examples remain limited to existing variants | docs/PROFILE_MATRIX.md, profiles/, examples/ | PASS | Downstream candidate only |
| AT-037 | current | quality_gate | Regression examples include extended base docs | Each existing example contains the five new base docs | examples/python_cli_minimal/, examples/csharp_desktop_minimal/, examples/plc_tool_minimal/ | PASS | Example skeletons synchronized |
| AT-038 | current | quality_gate | Example gate validates extended base docs | Common required file list includes the five new base docs | scripts/gates/example_gate.py | PASS | Required in all regression examples |
| AT-039 | current | quality_gate | Render drift check exists | Gate checks expected rendered file presence for existing examples | scripts/gates/example_render_drift_gate.py, scripts/quality_gate.py | PASS | Content comparison is intentionally out of scope |
| AT-040 | current | product_contract | Extended base template local target experiment is documented | Experiment record exists | docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md | PASS | Generic/base template target, no profile |
| AT-041 | current | quality_gate | Extended base docs rendered into local target | Actual render generated the five extended base docs | docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md | PASS | 11 base docs generated |
| AT-042 | current | side_effect_contract | No runtime or live-write artifacts were generated | Scope confirmation recorded | docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md | PASS | No app code, C# project, PLC/device code, live write, or live config |
| AT-043 | current | product_contract | rc2 release notes are documented | rc2 release notes exist | docs/RELEASE_NOTES_v0.1.0-rc2.md | PASS | Retained after tag creation |
| AT-044 | current | governance_audit | rc2 candidate closeout is documented | rc2 candidate closeout exists | docs/RC2_CANDIDATE_CLOSEOUT.md | PASS | Candidate evidence recorded |
| AT-045 | current | quality_gate | Latest main commit was verified for rc2 candidate | Verification result recorded for main commit | STATUS.md, docs/RELEASE_RECORD_v0.1.0-rc2.md | PASS | `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| AT-046 | current | governance_audit | v0.1.0-rc2 tag was created | Release record captures created tag state | docs/RELEASE_RECORD_v0.1.0-rc2.md | PASS | GitHub Release page not created |
| AT-047 | current | governance_audit | rc2 tag target commit is recorded | Release record and STATUS capture target commit | docs/RELEASE_RECORD_v0.1.0-rc2.md, STATUS.md | PASS | `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| AT-048 | current | product_contract | rc2 release record exists | Post-tag release record exists | docs/RELEASE_RECORD_v0.1.0-rc2.md | PASS | Tag not modified after creation |
| AT-049 | current | quality_gate | v0.1.0-rc2 clean clone validation is documented | Clean clone validation record exists | docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md | PASS | Bare python launcher blocked, wrapper runtime passed |
| AT-050 | current | governance_audit | rc2 clean clone checkout target is recorded | Checkout target and tag target are recorded | docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md | PASS | `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| AT-051 | current | quality_gate | Local verification passed from rc2 clean clone | Wrapper verification passed from tag checkout | docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md | PASS | pytest 17 passed, quality gate passed, render dry-runs passed |
| AT-052 | current | product_contract | GitHub Release Draft is documented | Release draft document exists | docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md | PASS | GitHub Release page not created |
| AT-053 | current | governance_audit | formal v0.1.0 criteria are documented | Criteria document exists | docs/FORMAL_V0.1.0_CRITERIA.md | PASS | Formal tag created after criteria satisfaction |
| AT-054 | current | scope_contract | GitHub Release page remains deferred after formal tag | Status and release record document post-tag state | STATUS.md, docs/RELEASE_RECORD_v0.1.0.md | PASS | Formal tag created; GitHub Release page not created |
| AT-055 | current | product_contract | Downstream application experiment record exists | Scenario simulator design downstream experiment record exists | docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md | PASS | Candidate tested without profile |
| AT-056 | current | scope_contract | Scenario simulator design was tested as downstream candidate, not profile | Record and repo structure show no profile/example was created | docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md, profiles/, examples/ | PASS | Base template only |
| AT-057 | current | quality_gate | formal v0.1.0 downstream experiment condition is satisfied | Status and criteria document record condition PASS | STATUS.md, docs/FORMAL_V0.1.0_CRITERIA.md | PASS | Formal tag created |
| AT-058 | current | governance_audit | formal v0.1.0 tag was created | Release record captures created formal tag state | docs/RELEASE_RECORD_v0.1.0.md | PASS | GitHub Release page not created |
| AT-059 | current | governance_audit | formal v0.1.0 tag target commit is recorded | Release record and STATUS capture target commit | docs/RELEASE_RECORD_v0.1.0.md, STATUS.md | PASS | `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| AT-060 | current | product_contract | formal v0.1.0 release record exists | Post-tag release record exists | docs/RELEASE_RECORD_v0.1.0.md | PASS | Tag not modified after creation |
| AT-061 | current | quality_gate | v0.1.0 clean clone validation is documented | Clean clone validation record exists | docs/CLEAN_CLONE_VALIDATION_v0.1.0.md | PASS | Bare python launcher blocked, wrapper runtime passed |
| AT-062 | current | governance_audit | v0.1.0 clean clone checkout target is recorded | Checkout target and tag target are recorded | docs/CLEAN_CLONE_VALIDATION_v0.1.0.md | PASS | `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| AT-063 | current | quality_gate | Local verification passed from v0.1.0 clean clone | Wrapper verification passed from formal tag checkout | docs/CLEAN_CLONE_VALIDATION_v0.1.0.md | PASS | pytest 17 passed, quality gate passed, render dry-runs passed |
| AT-064 | current | product_contract | formal v0.1.0 GitHub Release Draft is documented | Formal release draft exists | docs/GITHUB_RELEASE_DRAFT_v0.1.0.md | PASS | GitHub Release page not created |
| AT-065 | current | governance_audit | GitHub Release page remains not created | Status and release draft record unpublished state | STATUS.md, docs/GITHUB_RELEASE_DRAFT_v0.1.0.md | PASS | Draft only |
| AT-066 | current | scope_contract | local-first formal baseline remains unchanged | Release draft preserves scope exclusions | docs/GITHUB_RELEASE_DRAFT_v0.1.0.md | PASS | No workflow, profile, runtime code, or live-write support added |
| AT-067 | current | product_contract | local downstream adoption plan exists | Adoption plan document exists | docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md | PASS | Plan only; no downstream render executed |
| AT-068 | current | scope_contract | formal v0.1.0 tag remains unchanged | Adoption plan references existing tag without modifying it | docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md | PASS | `v0.1.0` remains at `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| AT-069 | current | side_effect_contract | local downstream adoption remains approval-gated | Plan requires dry-run, target path review, and approval before actual render | docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md | PASS | No downstream target created |
| AT-070 | current | product_contract | local downstream adoption run is documented | Adoption run record exists | docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md | PASS | Scenario simulator design baseline target |
| AT-071 | current | quality_gate | v0.1.0 source checkout was verified before adoption render | Run record captures source verification | docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md | PASS | pytest 17 passed, quality gate passed, render dry-runs passed |
| AT-072 | current | side_effect_contract | downstream adoption render generated only base docs | Run record captures generated files and safety checks | docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md | PASS | No profile, runtime code, C# project, PLC/device code, or live-write support |
| AT-073 | current | product_contract | downstream doc review checklist is documented | Review checklist exists | docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md | PASS | 11 generated docs listed |
| AT-074 | current | security_contract | downstream doc review prohibits sensitive content | Checklist records raw source and sensitive value prohibitions | docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md | PASS | No IFF/N3G raw source, IP, port, tag, or live parameter values |
| AT-075 | current | governance_audit | next-phase approval criteria are documented | Checklist records P1 and P2 approval gates | docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md | PASS | Implementation remains deferred |
| AT-076 | current | product_contract | post-v0.1.0 roadmap is documented | Roadmap document exists | docs/POST_V0.1.0_ROADMAP.md | PASS | Planning only; no implementation added |
| AT-077 | current | governance_audit | GitHub Release page decision is documented | Decision document exists | docs/RELEASE_PAGE_DECISION.md | PASS | GitHub Release page remains not created |
| AT-078 | current | scope_contract | local package checklist is documented | Checklist document exists | docs/LOCAL_PACKAGE_CHECKLIST.md | PASS | Package not built; boundary only |
| AT-079 | current | product_contract | optional eval harness plan is documented | Eval plan exists | docs/OPTIONAL_EVAL_HARNESS_PLAN.md | PASS | Eval harness not implemented |
| AT-080 | current | product_contract | known limitations are refreshed for post-v0.1.0 state | Current limitations and future work are updated | docs/KNOWN_LIMITATIONS.md | PASS | CI policy and release tagging guidance are no longer listed as future work |
| AT-081 | current | governance_audit | architecture release/record plane reflects formal v0.1.0 and post-v0.1.0 records | Release/Record Plane lists current evidence documents | docs/ARCHITECTURE.md | PASS | GitHub Release page not created; GitHub Actions not installed |
| AT-082 | current | scope_contract | no implementation was added during document drift cleanup | Scope exclusions remain documented and no new implementation artifact was created | docs/KNOWN_LIMITATIONS.md, docs/ARCHITECTURE.md, STATUS.md | PASS | Eval harness, SBOM, CI workflow, profiles, and application code remain absent |
| AT-083 | current | product_contract | downstream P2 design-only feedback is captured at template level | Feedback document exists and avoids downstream scenario content | docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md | PASS | No IFF/N3G source content, sensitive values, or runtime details copied |
| AT-084 | current | governance_audit | optional design-stage pack plan exists | Planning document lists candidate templates and promotion criteria | docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md | PASS | Experimental Markdown-only template files now exist |
| AT-085 | current | scope_contract | template extension policy covers downstream feedback promotion | Policy includes promotion, optional-pack, downstream-only, and profile-last-resort rules | docs/TEMPLATE_EXTENSION_POLICY.md | PASS | Profile creation remains last resort |
| AT-086 | current | side_effect_contract | no implementation was added while capturing downstream feedback | Status and feedback documents preserve non-goals | STATUS.md, docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md, docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md | PASS | No templates, profile, example, eval harness, SBOM/provenance, CI workflow, application code, C#/PLC/device code, or live-write support added |
| AT-087 | current | governance_audit | optional design-stage pack decision is documented | Decision document records options, recommendation, decision fields, and current decision state | docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md | PASS | Current decision is APPROVED FOR TEMPLATE FILES ONLY |
| AT-088 | current | side_effect_contract | optional design-stage pack implementation remains limited | Decision and status documents record template-files-only scope and deferred integrations | docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md, STATUS.md | PASS | Render, gate, and example integration require separate approval |
| AT-089 | current | product_contract | optional design-stage pack template files are created | Seven Markdown-only optional design-stage templates exist | templates/optional/design_stage/ | PASS | Approved for template files only |
| AT-090 | current | side_effect_contract | optional design-stage integrations remain deferred | Status and decision documents record no render, gate, or example integration | docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md, STATUS.md | PASS | No render_template.py, gate implementation, or example integration added |
| AT-091 | current | product_contract | optional design-stage pack usage guide exists | Manual usage guide exists | docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md | PASS | Documents safe manual use without integration |
| AT-092 | current | side_effect_contract | usage guide preserves manual-only and no-integration boundary | Usage guide states render, gate, and example integration require separate approval | docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md | PASS | No render integration, gate implementation, or example integration added |
| AT-093 | current | governance_audit | optional design-stage pack review record exists | Review record documents usage guide and template review | docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md | PASS | Template-level review captured |
| AT-094 | current | side_effect_contract | optional design-stage review keeps integration deferred | Review recommends manual-use-only and one more feedback cycle before integration | docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md | PASS | No render, gate, or example integration added |

## Status Values

- PASS: evidence supports the requirement.
- FAIL: evidence contradicts the requirement.
- PARTIAL: evidence is incomplete.
- NOT RUN: verification was not executed.
