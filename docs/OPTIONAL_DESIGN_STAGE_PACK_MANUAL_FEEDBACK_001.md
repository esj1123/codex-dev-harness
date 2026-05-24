# Optional Design-Stage Pack Manual Feedback 001

## Purpose

Record one manual-use feedback cycle for the optional design-stage pack after the usage guide was refined with downstream naming, skip/merge/review-only guidance, and manual scan examples.

This feedback record is documentation-only. It does not modify the downstream target, implement render integration, add gate implementation, create examples, create profiles, add eval harness code, create CI workflows, add application code, create C# assets, add PLC/device artifacts, or add live target write support.

## Feedback Source

- Source repository: `codex-dev-harness`.
- Reviewed usage guide version: local `main` at commit `36bda0e`.
- Feedback mode: read-only downstream review.
- Reviewed downstream target: separate local downstream design target, path generalized.
- Downstream target modification: NOT DONE.

## Reviewed Codex-Dev-Harness Documents

- `docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md`
- `docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md`
- `docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md`
- `docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md`
- `templates/optional/design_stage/DESIGN_WORKPLAN.md.template`
- `templates/optional/design_stage/CONCEPT_BOUNDARY.md.template`
- `templates/optional/design_stage/CATEGORY_MAP.md.template`
- `templates/optional/design_stage/SYNTHETIC_FIXTURE_PLAN.md.template`
- `templates/optional/design_stage/ACCEPTANCE_EVIDENCE_PLAN.md.template`
- `templates/optional/design_stage/OPEN_QUESTIONS.md.template`
- `templates/optional/design_stage/DESIGN_REVIEW_RECORD.md.template`

## Reviewed Downstream Documents

- `P2_SIMULATOR_DESIGN_PLAN.md`
- `SIMULATOR_CONCEPT_BOUNDARY.md`
- `SCENARIO_CATEGORY_MAP.md`
- `SYNTHETIC_FIXTURE_PLAN.md`
- `P2_DESIGN_REVIEW_RECORD.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `APPROVALS.md`
- `SOURCE_INDEX.md`
- `PHASE_PLAN.md`

## Refined Usage Guide Applicability

| check | result | notes |
|---|---|---|
| Downstream Naming Map matches existing downstream documents | PASS | Existing phase-specific P2 document names map cleanly to optional template roles |
| skip / merge / review-only guidance is useful | PASS | Existing first P2 outputs are best treated as review-only or skip; missing evidence/open-question outputs remain future candidates |
| prohibited content scan examples are useful | PASS | Examples cover policy terms, file artifacts, workflow artifacts, and executable artifacts without adding gate integration |
| source-use rules are comparable to downstream `SOURCE_INDEX.md` | PASS | Usable, owner-review, and excluded source rows can be cross-checked against P2 documents |
| manual adoption flow conflicts with downstream state | PASS | No conflict; downstream already started from base template and has phase approval for design-only work |

## Downstream Naming Map Result

| optional template | downstream equivalent | fit | notes |
|---|---|---|---|
| `DESIGN_WORKPLAN` | `P2_SIMULATOR_DESIGN_PLAN.md` | PASS | Phase-specific design plan records design-only scope, source-use decisions, candidate outputs, and exit criteria |
| `CONCEPT_BOUNDARY` | `SIMULATOR_CONCEPT_BOUNDARY.md` | PASS | Existing concept boundary records generalized, mock/synthetic, no-live-target, no-device, and no-C# boundaries |
| `CATEGORY_MAP` | `SCENARIO_CATEGORY_MAP.md` | PASS | Existing map uses generalized categories, synthetic inputs, abstract outputs, and source row references |
| `SYNTHETIC_FIXTURE_PLAN` | `SYNTHETIC_FIXTURE_PLAN.md` | PASS | Existing plan defines synthetic fixture categories without fixture files or runtime code |
| `ACCEPTANCE_EVIDENCE_PLAN` | no dedicated downstream equivalent yet | PARTIAL | Evidence concepts exist in other docs, but a phase-specific evidence plan is not created yet |
| `OPEN_QUESTIONS` | no dedicated downstream equivalent yet | PARTIAL | Open questions are embedded in existing docs, but a dedicated phase-specific open-question document is not created yet |
| `DESIGN_REVIEW_RECORD` | `P2_DESIGN_REVIEW_RECORD.md` | PASS | Existing review record checks design-only compliance, source use, sensitive information, and prohibited artifacts |

## Skip / Merge / Review-Only Result

| template | recommended use mode | verdict | reason | next action |
|---|---|---|---|---|
| `DESIGN_WORKPLAN` | review-only | PASS | Equivalent downstream workplan already exists and is sufficient for current P2 scope | Skip copying; use template as checklist for future refresh |
| `CONCEPT_BOUNDARY` | review-only | PASS | Existing concept boundary already records the required manual-use boundaries | Skip copying; keep as existing downstream document |
| `CATEGORY_MAP` | review-only | PASS | Existing category map already follows generalized and synthetic category rules | Skip copying; use template checklist for later expansion |
| `SYNTHETIC_FIXTURE_PLAN` | review-only | PASS | Existing fixture plan already defines synthetic-only categories and prohibited fields | Skip copying; use template checklist before any future fixture file work |
| `ACCEPTANCE_EVIDENCE_PLAN` | copy or merge candidate | PARTIAL | No dedicated downstream equivalent exists yet | Candidate for next design-only downstream output |
| `OPEN_QUESTIONS` | copy or merge candidate | PARTIAL | No dedicated downstream equivalent exists yet | Candidate for next design-only downstream output |
| `DESIGN_REVIEW_RECORD` | review-only | PASS | Existing review record already evaluates first P2 outputs | Keep as current review evidence; reuse template for next review cycle |

## Source-Use Rule Usefulness

Result: PASS.

The refined source-use rules are directly useful for the downstream target:

- usable rows map to the first P2 outputs;
- owner-review rows remain held until owner accept/revise/defer;
- excluded rows remain outside downstream content;
- P2 documents can be checked by source row identifiers without copying source content.

## Prohibited Content Check Result

Result: PASS WITH KNOWN NON-P2 PACKAGING FOLLOW-UP.

Manual review and read-only scans found:

- no C# source, solution, project, or XAML artifacts;
- no workflow directory;
- no executable or binary runtime artifacts from P2 work;
- no PLC/device code artifacts;
- policy-term matches only for prohibited categories and review statements;
- no sensitive values recorded in the reviewed P2 documents.

Known non-P2 packaging follow-up: a hidden/system zero-byte document artifact exists in the downstream target and remains an owner remove/ignore decision before packaging. It is not created by the optional design-stage pack and is not evidence of runtime or integration work.

## Findings

- The refined Downstream Naming Map works for phase-specific downstream names.
- The skip/merge/review-only guidance prevents unnecessary duplication when equivalent downstream docs already exist.
- The manual scan examples are sufficient for read-only review and do not require gate integration.
- `ACCEPTANCE_EVIDENCE_PLAN` and `OPEN_QUESTIONS` remain useful next downstream manual-use candidates.
- The downstream target can continue manual-use validation without render, gate, or example integration.

## Recommendation

- Keep the optional design-stage pack manual-use-only.
- Keep render integration DEFERRED.
- Keep gate integration DEFERRED.
- Keep example integration DEFERRED.
- Keep `ACCEPTANCE_EVIDENCE_PLAN` and `OPEN_QUESTIONS` as next downstream manual-use candidates.
- Defer optional pack integration until at least one additional manual-use feedback cycle or explicit owner approval.
- If a follow-up documentation refinement is approved, add a small usage-guide note for phase-specific evidence/open-question naming patterns.
