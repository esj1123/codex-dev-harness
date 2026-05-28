"""Local read-only AI readiness scanner.

The scanner inspects safe repository metadata and selected policy documents.
It does not run target repository commands, follow symlinks, or write reports.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Iterable


SKIPPED_DIR_NAMES = {
    ".git",
    ".venv",
    ".pytest_cache",
    "venv",
    "node_modules",
    "__pycache__",
    "bin",
    "obj",
    "artifacts",
    "raw",
    "processed",
    "exports",
    "logs",
    "attachments",
    "local",
    "private",
    "secrets",
    "credentials",
    "vault",
    "live_vault",
    "live-vault",
}

SAFE_TEXT_FILES = {
    "README.md",
    "AGENTS.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    "docs/SAFETY_POLICY.md",
    "docs/VERIFICATION.md",
}

QUALITY_GATE_NAMES = {
    "quality_gate.py",
    "quality-gate.py",
    "run_local_verify.ps1",
    "run-local-verify.ps1",
    "verify.ps1",
    "verify.py",
}

SMOKE_OR_TEST_NAMES = {
    "tests",
    "test",
    "smoke",
    "pytest.ini",
}

DOMAIN_RISK_KEYWORDS = {
    "PLC_DEVICE_LIVE_TARGET": ("plc", "device", "equipment", "live_target", "live-target", "tagmap", "tag_map"),
    "OUTLOOK_MAIL": ("outlook", "mail", "email", "msg", "pst"),
    "BROKER_FINANCE": ("broker", "finance", "stock", "trade", "trading", "account"),
    "VAULT_OBSIDIAN": ("vault", "obsidian"),
    "RSID": ("rsid",),
    "CREDENTIALS_SECRETS": ("credential", "credentials", "secret", "secrets", "token", "password", ".env"),
    "GENERATED_ARTIFACTS": ("artifact", "artifacts", "generated", "dist", "build"),
    "EXTERNAL_SERVICES": ("api", "webhook", "external", "service", "cloud"),
    "CI_RELEASE_DEPLOY": ("ci", "workflow", ".github", "release", "deploy", "deployment"),
}


@dataclass(frozen=True)
class ScoreDimension:
    name: str
    score: int
    status: str
    evidence: list[str]


@dataclass(frozen=True)
class RiskFlag:
    name: str
    paths: list[str]


@dataclass(frozen=True)
class ScanResult:
    target: str
    exists: bool
    score: int
    result: str
    dimensions: list[ScoreDimension]
    risk_flags: list[RiskFlag]
    skipped_paths: list[str]
    findings: list[str]
    inspected_paths: list[str]


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def normalize_path_text(path: Path, root: Path) -> str:
    try:
        value = relpath(path, root)
    except ValueError:
        value = path.name
    return value.lower().replace("\\", "/")


def safe_read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def iter_repo_paths(root: Path) -> tuple[list[Path], list[str]]:
    paths: list[Path] = []
    skipped: list[str] = []
    if not root.exists() or not root.is_dir():
        return paths, skipped

    stack = [root]
    while stack:
        current = stack.pop()
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            continue

        for child in children:
            relative = relpath(child, root)
            paths.append(child)
            name_lower = child.name.lower()

            if child.is_symlink():
                skipped.append(f"{relative}: symlink skipped")
                continue

            if child.is_dir():
                if name_lower in SKIPPED_DIR_NAMES:
                    skipped.append(f"{relative}: skipped directory")
                    continue
                stack.append(child)

    return paths, skipped


def has_file(root: Path, relative: str) -> bool:
    path = root / relative
    return path.is_file() and not path.is_symlink()


def has_dir(root: Path, relative: str) -> bool:
    path = root / relative
    return path.is_dir() and not path.is_symlink()


def score_purpose(root: Path) -> ScoreDimension:
    if not has_file(root, "README.md"):
        return ScoreDimension("Purpose clarity", 0, "INSUFFICIENT_EVIDENCE", ["README.md missing"])
    text = safe_read_text(root, "README.md")
    if contains_any(text, ("purpose", "goal", "overview", "current state", "project")):
        return ScoreDimension("Purpose clarity", 2, "PASS", ["README.md present with purpose-like language"])
    return ScoreDimension("Purpose clarity", 1, "PARTIAL", ["README.md present"])


def score_ai_rules(root: Path) -> ScoreDimension:
    if not has_file(root, "AGENTS.md"):
        return ScoreDimension("AI operating rules", 0, "INSUFFICIENT_EVIDENCE", ["AGENTS.md missing"])
    text = safe_read_text(root, "AGENTS.md")
    if contains_any(text, ("read-only", "side effect", "scope", "verification", "no-touch")):
        return ScoreDimension("AI operating rules", 2, "PASS", ["AGENTS.md present with operating-boundary language"])
    return ScoreDimension("AI operating rules", 1, "PARTIAL", ["AGENTS.md present"])


def score_safety(root: Path) -> ScoreDimension:
    candidates = ["docs/SAFETY_POLICY.md", "SAFETY_POLICY.md"]
    present = [path for path in candidates if has_file(root, path)]
    if not present:
        return ScoreDimension("Safety boundary", 0, "INSUFFICIENT_EVIDENCE", ["safety policy missing"])
    text = "\n".join(safe_read_text(root, path) for path in present)
    if contains_any(text, ("side effect", "read-only", "private data", "secret", "live target", "prohibited")):
        return ScoreDimension("Safety boundary", 2, "PASS", [f"{present[0]} present with safety-boundary language"])
    return ScoreDimension("Safety boundary", 1, "PARTIAL", [f"{present[0]} present"])


def score_verification(root: Path, path_texts: list[str]) -> ScoreDimension:
    script_hits = [
        path
        for path in path_texts
        if Path(path).name.lower() in QUALITY_GATE_NAMES or "quality_gate" in path or "verify" in path
    ]
    has_verification_doc = has_file(root, "docs/VERIFICATION.md") or has_file(root, "VERIFICATION.md")
    if has_verification_doc and script_hits:
        return ScoreDimension("Verification script", 2, "PASS", ["verification doc and local verification script present"])
    if has_verification_doc or script_hits:
        evidence = "verification doc present" if has_verification_doc else "local verification script name present"
        return ScoreDimension("Verification script", 1, "PARTIAL", [evidence])
    return ScoreDimension("Verification script", 0, "INSUFFICIENT_EVIDENCE", ["verification surface missing"])


def score_tests(path_texts: list[str]) -> ScoreDimension:
    hits = [path for path in path_texts if any(part in path.lower() for part in SMOKE_OR_TEST_NAMES)]
    if any(path.lower().startswith("tests/") for path in path_texts) or "tests" in [Path(path).name.lower() for path in path_texts]:
        if hits:
            return ScoreDimension("Tests or smoke checks", 2, "PASS", ["tests or smoke check paths present"])
    if hits:
        return ScoreDimension("Tests or smoke checks", 1, "PARTIAL", ["test or smoke indicator present"])
    return ScoreDimension("Tests or smoke checks", 0, "INSUFFICIENT_EVIDENCE", ["tests or smoke checks missing"])


def score_private_data(root: Path) -> ScoreDimension:
    texts = "\n".join(safe_read_text(root, path) for path in SAFE_TEXT_FILES if has_file(root, path))
    if contains_any(texts, ("private data", "synthetic", "secret", "credential", "token", "customer data")):
        return ScoreDimension("Private data protection", 2, "PASS", ["private-data protection language present"])
    if has_file(root, ".gitignore"):
        return ScoreDimension("Private data protection", 1, "PARTIAL", [".gitignore present"])
    return ScoreDimension("Private data protection", 0, "INSUFFICIENT_EVIDENCE", ["private-data protection evidence missing"])


def score_acceptance(root: Path) -> ScoreDimension:
    if has_file(root, "ACCEPTANCE_TRACE.md"):
        text = safe_read_text(root, "ACCEPTANCE_TRACE.md")
        if contains_any(text, ("evidence", "pass", "fail", "not run", "acceptance")):
            return ScoreDimension("Acceptance trace or evidence discipline", 2, "PASS", ["ACCEPTANCE_TRACE.md present with evidence language"])
        return ScoreDimension("Acceptance trace or evidence discipline", 1, "PARTIAL", ["ACCEPTANCE_TRACE.md present"])
    return ScoreDimension("Acceptance trace or evidence discipline", 0, "INSUFFICIENT_EVIDENCE", ["acceptance trace missing"])


def score_next_action(root: Path) -> ScoreDimension:
    candidates = ["STATUS.md", "docs/AI_HANDOFF.md", "AI_HANDOFF.md"]
    present = [path for path in candidates if has_file(root, path)]
    if not present:
        return ScoreDimension("Next action clarity", 0, "INSUFFICIENT_EVIDENCE", ["status or handoff document missing"])
    text = "\n".join(safe_read_text(root, path) for path in present)
    if contains_any(text, ("next", "current phase", "current state", "recommended", "todo")):
        return ScoreDimension("Next action clarity", 2, "PASS", ["status or handoff document includes next-action language"])
    return ScoreDimension("Next action clarity", 1, "PARTIAL", [f"{present[0]} present"])


def interpret_score(score: int, dimensions: list[ScoreDimension]) -> str:
    if any(dimension.status == "INSUFFICIENT_EVIDENCE" for dimension in dimensions) and score == 0:
        return "INSUFFICIENT_EVIDENCE"
    if score >= 13:
        return "READY_FOR_AI_ASSISTED_WORK"
    if score >= 9:
        return "LIMITED_AI_ASSISTED_WORK_ALLOWED"
    if score >= 5:
        return "NEEDS_DOCUMENTATION_OR_HARNESS_IMPROVEMENT"
    return "HOLD_BEFORE_AI_ASSISTED_WORK"


def collect_risk_flags(root: Path, paths: list[Path]) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    for flag_name, keywords in DOMAIN_RISK_KEYWORDS.items():
        matched: list[str] = []
        for path in paths:
            path_text = normalize_path_text(path, root)
            if any(keyword in path_text for keyword in keywords):
                matched.append(path_text)
        if matched:
            flags.append(RiskFlag(flag_name, sorted(set(matched))[:10]))
    return flags


def scan_target(target: Path) -> ScanResult:
    root = target.resolve()
    paths, skipped = iter_repo_paths(root)
    path_texts = sorted(relpath(path, root) for path in paths if path.exists())
    inspected_paths = sorted(path for path in path_texts if path in SAFE_TEXT_FILES or Path(path).name in QUALITY_GATE_NAMES)

    if not root.exists() or not root.is_dir():
        return ScanResult(
            target=str(target),
            exists=False,
            score=0,
            result="INSUFFICIENT_EVIDENCE",
            dimensions=[],
            risk_flags=[],
            skipped_paths=[],
            findings=["target path missing or not a directory"],
            inspected_paths=[],
        )

    dimensions = [
        score_purpose(root),
        score_ai_rules(root),
        score_safety(root),
        score_verification(root, path_texts),
        score_tests(path_texts),
        score_private_data(root),
        score_acceptance(root),
        score_next_action(root),
    ]
    score = sum(dimension.score for dimension in dimensions)
    risk_flags = collect_risk_flags(root, paths)
    findings = [f"{dimension.name}: {dimension.status}" for dimension in dimensions if dimension.status != "PASS"]
    findings.extend(f"domain risk flag: {flag.name}" for flag in risk_flags)

    return ScanResult(
        target=str(root),
        exists=True,
        score=score,
        result=interpret_score(score, dimensions),
        dimensions=dimensions,
        risk_flags=risk_flags,
        skipped_paths=sorted(skipped),
        findings=findings,
        inspected_paths=inspected_paths,
    )


def result_to_markdown(result: ScanResult) -> str:
    lines = [
        "# AI 준비도 점검 보고서",
        "",
        "## 결론",
        "",
        f"- 대상: `{result.target}`",
        f"- 판정: `{result.result}`",
        f"- 총점: {result.score}/16",
        "",
        "## 근거",
        "",
    ]
    if result.dimensions:
        for dimension in result.dimensions:
            evidence = "; ".join(dimension.evidence)
            lines.append(f"- {dimension.name}: {dimension.score}/2, {dimension.status} ({evidence})")
    else:
        lines.append("- 확인 가능한 점수 근거가 없습니다.")

    lines.extend(["", "## 실행 체크리스트", ""])
    lines.extend(
        [
            "- [ ] 읽기 전용 점검 결과 검토",
            "- [ ] 변경 금지 영역 확인",
            "- [ ] 검증 명령 확인",
            "- [ ] 다음 작업 범위 확인",
        ]
    )

    lines.extend(["", "## 리스크 / 영향범위", ""])
    if result.risk_flags:
        for flag in result.risk_flags:
            lines.append(f"- {flag.name}: {len(flag.paths)} path indicator(s)")
    else:
        lines.append("- 도메인 리스크 플래그 없음")

    lines.extend(["", "## Repo 점수표", ""])
    lines.extend(["| 항목 | 점수 | 근거 | 상태 |", "|---|---:|---|---|"])
    for dimension in result.dimensions:
        evidence = "; ".join(dimension.evidence)
        lines.append(f"| {dimension.name} | {dimension.score}/2 | {evidence} | {dimension.status} |")

    lines.extend(["", "## 부족 항목", ""])
    if result.findings:
        for finding in result.findings:
            lines.append(f"- {finding}")
    else:
        lines.append("- 없음")

    lines.extend(["", "## 다음 작업 우선순위", ""])
    lines.extend(
        [
            "1. 부족 항목을 문서 또는 로컬 검증 표면으로 보강합니다.",
            "2. 도메인 리스크 플래그가 있으면 승인 경계와 no-touch 영역을 명확히 합니다.",
            "3. AI-assisted work 전에 작은 배치의 읽기 전용 계획을 먼저 작성합니다.",
        ]
    )

    lines.extend(["", "## 확인 필요 항목", ""])
    if result.skipped_paths:
        lines.append(f"- 기본 제외 또는 symlink skip 경로: {len(result.skipped_paths)}개")
    else:
        lines.append("- 추가 확인 필요 항목 없음")

    return "\n".join(lines)


def results_to_markdown(results: list[ScanResult]) -> str:
    return "\n\n---\n\n".join(result_to_markdown(result) for result in results)


def results_to_json(results: list[ScanResult]) -> str:
    return json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local read-only AI readiness scan.")
    parser.add_argument("targets", nargs="+", help="Repository path(s) to inspect")
    parser.add_argument("--json", action="store_true", help="Write JSON results to stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    results = [scan_target(Path(target)) for target in args.targets]
    if args.json:
        print(results_to_json(results))
    else:
        print(results_to_markdown(results))
    return 0 if all(result.exists for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
