"""Run local-only non-LLM evals for codex-dev-harness.

The eval case files use a JSON-compatible YAML subset so this runner can stay
on the Python standard library.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import fnmatch
import json
from pathlib import Path
import re
import sys
from typing import Any


sys.dont_write_bytecode = True

try:
    from render_template import iter_templates, load_config, template_destination
except ModuleNotFoundError:
    from scripts.render_template import iter_templates, load_config, template_destination


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "evals" / "cases"
CASE_PATTERN = "*.yml"
ARTIFACTS_ROOT = "artifacts"
REPORT_SCHEMA_VERSION = "1"

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
]


@dataclass(frozen=True)
class EvalResult:
    name: str
    passed: bool
    messages: list[str]


@dataclass(frozen=True)
class EvalSummary:
    passed: bool
    results: list[EvalResult]


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def load_case(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} must be JSON-compatible YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level object")
    return data


def case_result_name(case: dict[str, Any], fallback: str) -> str:
    value = case.get("name") or case.get("eval") or fallback
    return str(value)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def planned_render_paths(repo_root: Path, config_path: Path, target: Path) -> list[str]:
    config = load_config(config_path)
    base_dir = repo_root / "templates" / "base"
    profile_dir = repo_root / "profiles" / config.profile if config.profile else None
    paths = [
        relpath(template_destination(source, source_root, target), repo_root)
        for source, source_root in iter_templates(base_dir, profile_dir)
    ]
    return paths


def run_render_structure(repo_root: Path, case: dict[str, Any]) -> EvalResult:
    name = case_result_name(case, "render_structure")
    findings: list[str] = []
    all_planned: list[str] = []
    forbidden_suffixes = {suffix.lower() for suffix in case.get("forbidden_suffixes", [])}
    match_mode = str(case.get("match_mode", "exact"))

    for example in case.get("examples", []):
        name = example["name"]
        config_path = repo_root / example["config"]
        target = repo_root / example["target"]
        expected = list(example.get("expected_files", []))

        planned_once = planned_render_paths(repo_root, config_path, target)
        planned_twice = planned_render_paths(repo_root, config_path, target)
        all_planned.extend(planned_once)

        if planned_once != planned_twice:
            findings.append(f"{name}: render path order is not deterministic")
        if match_mode == "exact" and expected and planned_once != expected:
            findings.append(f"{name}: planned output path list drifted")
        if match_mode == "contains":
            missing_planned = [path for path in expected if path not in planned_once]
            if missing_planned:
                findings.append(f"{name}: expected paths absent from render plan: {', '.join(missing_planned)}")

        for expected_path in expected:
            if not (repo_root / expected_path).is_file():
                findings.append(f"{name}: missing expected rendered doc: {expected_path}")

        for path in sorted(target.rglob("*")):
            if path.is_file() and path.suffix.lower() in forbidden_suffixes:
                findings.append(f"{name}: forbidden generated file present: {relpath(path, repo_root)}")

    golden = case.get("golden_paths_file")
    if golden:
        golden_path = repo_root / golden
        if not golden_path.is_file():
            findings.append(f"missing golden path list: {golden}")
        else:
            expected_golden = [line.strip() for line in golden_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if all_planned != expected_golden:
                findings.append("render path list differs from evals/golden/render_structure_paths.txt")

    if findings:
        return EvalResult(case_result_name(case, "render_structure"), False, findings)
    return EvalResult(case_result_name(case, "render_structure"), True, [f"validated render path lists: {len(all_planned)}"])


def run_policy_phrases(repo_root: Path, case: dict[str, Any]) -> EvalResult:
    name = case_result_name(case, "policy_phrases")
    findings: list[str] = []

    for check in case.get("checks", []):
        relative = check["path"]
        path = repo_root / relative
        if not path.is_file():
            findings.append(f"missing policy phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in check.get("phrases", []):
            if phrase.lower() not in text:
                findings.append(f"{relative}: missing phrase: {phrase}")

    if findings:
        return EvalResult(name, False, findings)
    return EvalResult(name, True, [f"validated phrase targets: {len(case.get('checks', []))}"])


def iter_repo_files(repo_root: Path, ignored_root_parts: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        relative_parts = path.relative_to(repo_root).parts
        if relative_parts and relative_parts[0] in ignored_root_parts:
            continue
        if path.is_file():
            files.append(path)
    return files


def matches_glob(relative: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(relative, pattern) for pattern in patterns)


def run_forbidden_artifacts(repo_root: Path, case: dict[str, Any]) -> EvalResult:
    name = case_result_name(case, "forbidden_artifacts")
    findings: list[str] = []
    ignored_root_parts = set(case.get("ignored_root_parts", []))
    forbidden_globs = list(case.get("forbidden_path_globs", []))
    forbidden_suffixes = {suffix.lower() for suffix in case.get("forbidden_suffixes", [])}
    text_suffixes = {suffix.lower() for suffix in case.get("text_suffixes", [])}

    for path in iter_repo_files(repo_root, ignored_root_parts):
        relative = relpath(path, repo_root)
        if matches_glob(relative, forbidden_globs):
            findings.append(f"forbidden path pattern matched: {relative}")
        if path.suffix.lower() in forbidden_suffixes:
            findings.append(f"forbidden suffix matched: {relative}")
        if path.suffix.lower() in text_suffixes or path.name.endswith(".template"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(f"secret/live-value pattern matched: {relative}")
                    break

    if findings:
        return EvalResult(name, False, findings)
    return EvalResult(name, True, ["no forbidden artifacts or obvious secret/live-value patterns found"])


def nested_value(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(path)
    return current


def run_json_shape(repo_root: Path, case: dict[str, Any]) -> EvalResult:
    name = case_result_name(case, "json_shape")
    findings: list[str] = []

    for file_case in case.get("files", []):
        relative = file_case["path"]
        path = repo_root / relative
        if not path.is_file():
            findings.append(f"missing JSON target: {relative}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(f"{relative}: invalid JSON: {exc}")
            continue
        if not isinstance(data, dict):
            findings.append(f"{relative}: top-level JSON value must be an object")
            continue

        for field in file_case.get("required_top_level", []):
            if field not in data:
                findings.append(f"{relative}: missing top-level field: {field}")

        for field_path in file_case.get("required_paths", []):
            try:
                nested_value(data, field_path)
            except KeyError:
                findings.append(f"{relative}: missing field path: {field_path}")

        list_field = file_case.get("list_field")
        required_item_fields = file_case.get("required_list_item_fields", [])
        if list_field:
            value = data.get(list_field)
            if not isinstance(value, list) or not value:
                findings.append(f"{relative}: field must be a non-empty list: {list_field}")
            else:
                for item in value:
                    if not isinstance(item, dict):
                        findings.append(f"{relative}: {list_field} item must be an object")
                        continue
                    for item_field in required_item_fields:
                        if item_field not in item:
                            findings.append(f"{relative}: {list_field} item missing field: {item_field}")
                            break

    if findings:
        return EvalResult(name, False, findings)
    return EvalResult(name, True, [f"validated JSON shape targets: {len(case.get('files', []))}"])


def run_checksum_shape(repo_root: Path, case: dict[str, Any]) -> EvalResult:
    name = case_result_name(case, "checksum_shape")
    relative = case["path"]
    path = repo_root / relative
    findings: list[str] = []

    if not path.is_file():
        return EvalResult(name, False, [f"missing checksum target: {relative}"])

    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        if "  " not in line:
            findings.append(f"{relative}:{line_number}: missing two-space separator")
            continue
        digest, artifact_path = line.split("  ", 1)
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            findings.append(f"{relative}:{line_number}: invalid sha256 digest")
        if not artifact_path:
            findings.append(f"{relative}:{line_number}: missing artifact path")
        entries.append((digest, artifact_path))

    paths = [artifact_path for _, artifact_path in entries]
    if paths != sorted(paths):
        findings.append(f"{relative}: checksum paths are not sorted")

    for required_path in case.get("required_paths", []):
        if required_path not in paths:
            findings.append(f"{relative}: missing required checksum path: {required_path}")

    for present_path in case.get("present_paths_must_be_included", []):
        if (repo_root / present_path).is_file() and present_path not in paths:
            findings.append(f"{relative}: present artifact is not checksummed: {present_path}")

    for forbidden_path in case.get("forbidden_paths", []):
        if forbidden_path in paths:
            findings.append(f"{relative}: forbidden checksum path present: {forbidden_path}")

    if findings:
        return EvalResult(name, False, findings)
    return EvalResult(name, True, [f"validated checksum entries: {len(entries)}"])


def run_jsonl_shape(repo_root: Path, case: dict[str, Any]) -> EvalResult:
    name = case_result_name(case, "jsonl_shape")
    relative = case["path"]
    path = repo_root / relative
    findings: list[str] = []

    if not path.is_file():
        return EvalResult(name, False, [f"missing JSONL target: {relative}"])

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.append(f"{relative}:{line_number}: invalid JSONL row: {exc}")
            continue
        if not isinstance(row, dict):
            findings.append(f"{relative}:{line_number}: JSONL row must be an object")
            continue
        rows.append(row)

    if not rows:
        findings.append(f"{relative}: JSONL file has no records")

    for row in rows:
        for field in case.get("required_top_level", []):
            if field not in row:
                findings.append(f"{relative}: missing top-level field: {field}")
        expected_predicate_type = case.get("expected_predicate_type")
        if expected_predicate_type and row.get("predicateType") != expected_predicate_type:
            findings.append(f"{relative}: unexpected predicateType: {row.get('predicateType')}")
        predicate = row.get("predicate")
        if case.get("require_local_only") and not (isinstance(predicate, dict) and predicate.get("local_only") is True):
            findings.append(f"{relative}: predicate.local_only must be true")
        if isinstance(predicate, dict):
            for field in case.get("required_predicate_fields", []):
                if field not in predicate:
                    findings.append(f"{relative}: missing predicate field: {field}")

    if findings:
        return EvalResult(name, False, findings)
    return EvalResult(name, True, [f"validated JSONL records: {len(rows)}"])


def run_case(repo_root: Path, case_path: Path) -> EvalResult:
    case = load_case(case_path)
    eval_name = case.get("eval")
    if eval_name == "render_structure":
        return run_render_structure(repo_root, case)
    if eval_name == "policy_phrases":
        return run_policy_phrases(repo_root, case)
    if eval_name == "forbidden_artifacts":
        return run_forbidden_artifacts(repo_root, case)
    if eval_name == "json_shape":
        return run_json_shape(repo_root, case)
    if eval_name == "checksum_shape":
        return run_checksum_shape(repo_root, case)
    if eval_name == "jsonl_shape":
        return run_jsonl_shape(repo_root, case)
    return EvalResult(case_result_name(case, case_path.stem), False, [f"unknown eval type: {eval_name or 'missing'}"])


def discover_case_paths(repo_root: Path) -> list[Path]:
    case_dir = repo_root / "evals" / "cases"
    return sorted(case_dir.glob(CASE_PATTERN), key=lambda path: path.name)


def run_all(repo_root: Path = REPO_ROOT, case_paths: list[Path] | None = None) -> EvalSummary:
    repo_root = repo_root.resolve()
    if case_paths is None:
        case_paths = discover_case_paths(repo_root)
    results = [run_case(repo_root, path) for path in case_paths]
    return EvalSummary(all(result.passed for result in results), results)


def summary_to_report(summary: EvalSummary, generated_at_utc: str | None = None) -> dict[str, Any]:
    passed_cases = sum(1 for result in summary.results if result.passed)
    failed_cases = len(summary.results) - passed_cases
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc or utc_now(),
        "total_cases": len(summary.results),
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "passed": summary.passed,
        "cases": [
            {
                "name": result.name,
                "passed": result.passed,
                "messages": result.messages,
            }
            for result in summary.results
        ],
    }


def resolve_report_path(repo_root: Path, report_arg: str) -> Path:
    raw_path = Path(report_arg)
    if raw_path.is_absolute() or raw_path.drive or raw_path.anchor:
        raise ValueError("--report must be a repo-internal relative path")
    if not raw_path.parts:
        raise ValueError("--report must name a report file")
    if any(part == ".." for part in raw_path.parts):
        raise ValueError("--report must not contain parent traversal")
    if raw_path.parts[0] != ARTIFACTS_ROOT or len(raw_path.parts) < 2:
        raise ValueError("--report must be under artifacts/")

    resolved_root = repo_root.resolve()
    report_path = (resolved_root / raw_path).resolve()
    try:
        report_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("--report must resolve inside the repository") from exc
    if report_path == resolved_root:
        raise ValueError("--report must name a report file")
    return report_path


def print_summary(summary: EvalSummary) -> None:
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        for message in result.messages:
            print(f"  - {message}")
    print("Local evals passed." if summary.passed else "Local evals failed.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local-only codex-dev-harness evals.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to check")
    parser.add_argument("--case", action="append", default=None, help="Specific case file to run; may be repeated")
    parser.add_argument(
        "--report",
        default=None,
        help="Optional repo-internal relative JSON report path, e.g. artifacts/eval-report.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    case_paths = [Path(path).resolve() for path in args.case] if args.case else None
    report_path = None
    if args.report:
        try:
            report_path = resolve_report_path(repo_root, args.report)
        except ValueError as exc:
            parser.error(str(exc))

    summary = run_all(repo_root, case_paths)
    print_summary(summary)

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary_to_report(summary), indent=2) + "\n", encoding="utf-8")
        print(f"Wrote eval report: {relpath(report_path, repo_root)}")

    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
