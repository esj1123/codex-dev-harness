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
    "docs/P6_RELEASE_CLOSEOUT.md",
    "docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md",
    "docs/FORMAL_V0.1.0_CRITERIA.md",
    "docs/RELEASE_NOTES_v0.1.0-rc1.md",
    "docs/RELEASE_NOTES_v0.1.0-rc2.md",
    "docs/RELEASE_RECORD_v0.1.0-rc1.md",
    "docs/RELEASE_RECORD_v0.1.0-rc2.md",
    "docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md",
    "docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md",
    "docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md",
    "docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md",
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
