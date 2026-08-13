"""Documentation presence gate."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


MANIFEST_PATH = "docs/AUTHORITY_MANIFEST.json"
CLASSIFICATION_KEYS = ("current_authority", "durable_policy", "historical_evidence")

BASELINE_REQUIRED_DOCS = [
    "AGENTS.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
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
    "docs/OPTIONAL_DESIGN_STAGE_PACK_INTEGRATION_DECISION.md",
    "docs/PROMPT_PATTERNS.md",
    "docs/BUG_REVIEW_TEMPLATE.md",
    "docs/SIMPLIFICATION_CHECKLIST.md",
    "docs/POST_V0.1.0_ROADMAP.md",
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
    "docs/RELEASE_PAGE_DECISION.md",
    "docs/LOCAL_PACKAGE_CHECKLIST.md",
    "docs/RELEASE_BUNDLE_POLICY.md",
    "docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md",
    "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
    "docs/RELEASE_MANIFEST_POLICY.md",
    "docs/SBOM_PROVENANCE_PLAN.md",
    "docs/PYTHON_RUNTIME_POLICY.md",
    "docs/APPROVED_CORPUS_RAG_PLAN.md",
    "docs/MODEL_CHANGE_POLICY.md",
    "docs/AGENT_QUALITY_STABILITY_POLICY.md",
    "docs/OPTIONAL_EVAL_HARNESS_PLAN.md",
    "docs/MINIMAL_EVAL_HARNESS_DESIGN.md",
    "docs/CHANGE_CONTROL.md",
    "docs/HUMAN_APPROVALS.md",
    "docs/EVAL_POLICY.md",
    "docs/AUDIT_LOG_POLICY.md",
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
    "docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md",
    "docs/OPTIONAL_GITHUB_ACTIONS.md",
]


def manifest_required_docs(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("authority manifest must be an object")

    required: list[str] = []
    for key in CLASSIFICATION_KEYS:
        paths = payload.get(key)
        if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
            raise ValueError(f"authority manifest {key} must be a string list")
        required.extend(paths)
    if len(required) != len(set(required)):
        raise ValueError("authority manifest classifications must be disjoint")
    if MANIFEST_PATH not in required:
        raise ValueError("authority manifest must classify itself")
    return required


REQUIRED_DOCS = [*BASELINE_REQUIRED_DOCS, MANIFEST_PATH]


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def run(repo_root: Path) -> GateResult:
    try:
        required_docs = manifest_required_docs(repo_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return GateResult("docs_gate", False, [f"authority manifest invalid: {exc}"])

    missing = [path for path in required_docs if not (repo_root / path).is_file()]
    if missing:
        return GateResult("docs_gate", False, [f"missing required doc: {path}" for path in missing])

    try:
        from scripts.authority_manifest_check import inspect_manifest
    except ImportError:  # pragma: no cover - direct script execution
        from authority_manifest_check import inspect_manifest

    manifest_result = inspect_manifest(repo_root=repo_root)
    if manifest_result["status"] != "PASS":
        reasons = manifest_result["reason_codes"] or ["UNKNOWN"]
        return GateResult(
            "docs_gate",
            False,
            [f"authority manifest check failed: {reason}" for reason in reasons],
        )
    return GateResult(
        "docs_gate",
        True,
        [
            f"required docs present: {len(required_docs)}",
            f"authority state: {manifest_result['current_state']}",
        ],
    )
