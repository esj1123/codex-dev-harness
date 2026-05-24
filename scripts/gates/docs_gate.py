"""Documentation presence gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_DOCS = [
    "AGENTS.md",
    "README.md",
    "PRODUCT.md",
    "MVP.md",
    "ROADMAP.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    "code_review.md",
    "docs/ARCHITECTURE.md",
    "docs/HARNESS_SPEC.md",
    "docs/PROFILE_MATRIX.md",
    "docs/SAFETY_POLICY.md",
    "docs/AI_HANDOFF.md",
    "docs/VERIFICATION.md",
    "docs/VALIDATION_SCOPE.md",
    "docs/TEMPLATE_EXTENSION_POLICY.md",
    "docs/DOMAIN_ADAPTATION_GUIDE.md",
    "docs/adr/ADR-0001-local-first.md",
    "docs/adr/ADR-0002-base-template-over-domain-profile.md",
    "docs/adr/ADR-0003-approval-gated-side-effect.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/KNOWN_LIMITATIONS.md",
    "docs/CI_POLICY.md",
    "docs/LOCAL_USAGE.md",
    "docs/LOCAL_RELEASE_PACKAGE.md",
    "docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md",
    "docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md",
    "docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md",
    "docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md",
    "docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md",
    "docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md",
    "docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md",
    "docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md",
    "docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_001.md",
    "docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_002.md",
    "docs/POST_V0.1.0_ROADMAP.md",
    "docs/RELEASE_PAGE_DECISION.md",
    "docs/LOCAL_PACKAGE_CHECKLIST.md",
    "docs/OPTIONAL_EVAL_HARNESS_PLAN.md",
    "docs/P6_RELEASE_CLOSEOUT.md",
    "docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md",
    "docs/GITHUB_RELEASE_DRAFT_v0.1.0.md",
    "docs/FORMAL_V0.1.0_CRITERIA.md",
    "docs/RELEASE_NOTES_v0.1.0-rc1.md",
    "docs/RELEASE_NOTES_v0.1.0-rc2.md",
    "docs/RELEASE_RECORD_v0.1.0-rc1.md",
    "docs/RELEASE_RECORD_v0.1.0-rc2.md",
    "docs/RELEASE_RECORD_v0.1.0.md",
    "docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md",
    "docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md",
    "docs/CLEAN_CLONE_VALIDATION_v0.1.0.md",
    "docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md",
    "docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md",
    "docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md",
    "docs/RC2_CANDIDATE_CLOSEOUT.md",
    "docs/OPTIONAL_GITHUB_ACTIONS.md",
]


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def run(repo_root: Path) -> GateResult:
    missing = [path for path in REQUIRED_DOCS if not (repo_root / path).is_file()]
    if missing:
        return GateResult("docs_gate", False, [f"missing required doc: {path}" for path in missing])
    return GateResult("docs_gate", True, [f"required docs present: {len(REQUIRED_DOCS)}"])
