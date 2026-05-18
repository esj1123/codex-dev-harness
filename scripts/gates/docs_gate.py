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
    "docs/HARNESS_SPEC.md",
    "docs/PROFILE_MATRIX.md",
    "docs/SAFETY_POLICY.md",
    "docs/AI_HANDOFF.md",
    "docs/VERIFICATION.md",
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
