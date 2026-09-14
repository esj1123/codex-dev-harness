"""Run the repository quality gate for codex-dev-harness."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import TextIO


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gates import docs_gate, example_gate, example_render_drift_gate, json_evidence_gate, rendered_golden_content_gate, repo_hygiene_gate, secret_scan_gate, template_schema_gate  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_RESULT_LIMIT = 100

GATE_INVENTORY = (
    ("docs_gate", docs_gate, "run"),
    ("repo_hygiene_gate", repo_hygiene_gate, "run"),
    ("template_schema_gate", template_schema_gate, "run"),
    ("example_gate", example_gate, "run"),
    ("example_render_drift_gate", example_render_drift_gate, "run"),
    ("rendered_golden_content_gate", rendered_golden_content_gate, "run"),
    ("secret_scan_gate", secret_scan_gate, "run"),
    ("json_evidence_gate", json_evidence_gate, "run_core"),
)


@dataclass(frozen=True)
class GateSummary:
    passed: bool
    results: list[object]


def run_quality_gate(repo_root: Path = REPO_ROOT) -> GateSummary:
    results = [getattr(module, entrypoint)(repo_root) for _, module, entrypoint in GATE_INVENTORY]
    return GateSummary(all(result.passed for result in results), results)


def print_summary(summary: GateSummary, *, file: TextIO | None = None) -> None:
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}", file=file)
        for message in result.messages:
            print(f"  - {message}", file=file)


def json_summary(summary: GateSummary) -> dict[str, object]:
    """Return the bounded, path-free JSON projection for the CLI."""
    results = summary.results if isinstance(summary.results, list) else []
    total = len(results)
    passed = sum(getattr(result, "passed", None) is True for result in results)
    failed = total - passed
    safe_rows = []
    valid_results = True
    for index, result in enumerate(results[:len(GATE_INVENTORY)]):
        check_id = GATE_INVENTORY[index][0]
        messages = getattr(result, "messages", None)
        result_passed = getattr(result, "passed", None)
        valid_results = valid_results and (
            getattr(result, "name", None) == check_id
            and isinstance(result_passed, bool)
            and isinstance(messages, list)
        )
        safe_rows.append(
            {
                "check_id": check_id,
                "status": "PASS" if result_passed is True else "FAIL",
                "message_count": len(messages) if isinstance(messages, list) else 0,
            }
        )
    projected = (
        [row for row in safe_rows if row["status"] == "FAIL"]
        + [row for row in safe_rows if row["status"] == "PASS"]
    )[:JSON_RESULT_LIMIT]

    reason_codes: list[str] = []
    if total == 0:
        reason_codes.append("GATE_RESULTS_EMPTY")
    if total != len(GATE_INVENTORY):
        reason_codes.append("GATE_RESULT_COUNT_MISMATCH")
    if not valid_results or len(safe_rows) != min(total, len(GATE_INVENTORY)):
        reason_codes.append("GATE_RESULT_INVALID")
    aggregate_passed = (
        total == len(GATE_INVENTORY)
        and valid_results
        and passed == total
    )
    if not isinstance(summary.passed, bool) or summary.passed != aggregate_passed:
        reason_codes.append("GATE_SUMMARY_INCONSISTENT")
    if failed and "GATE_RESULT_INVALID" not in reason_codes:
        reason_codes.append("GATE_FAILED")

    status = "PASS" if aggregate_passed and not reason_codes else "FAIL"
    exit_code = 0 if status == "PASS" else 1
    return {
        "schema_version": "1",
        "checker_id": "quality_gate",
        "status": status,
        "exit_code": exit_code,
        "counts": {"total": total, "passed": passed, "failed": failed},
        "results": projected,
        "omitted_result_count": total - len(projected),
        "reason_codes": reason_codes,
        "report_written": False,
    }


def execution_error_json() -> dict[str, object]:
    return {
        "schema_version": "1",
        "checker_id": "quality_gate",
        "status": "FAIL",
        "exit_code": 1,
        "counts": {"total": 0, "passed": 0, "failed": 0},
        "results": [],
        "omitted_result_count": 0,
        "reason_codes": ["GATE_EXECUTION_ERROR"],
        "report_written": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run codex-dev-harness quality gates.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to check")
    parser.add_argument("--json", action="store_true", help="Emit a safe JSON result")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_quality_gate(Path(args.repo_root).resolve())
    except Exception as exc:
        if not args.json:
            raise
        print(f"[FAIL] quality_gate execution error: {exc}", file=sys.stderr)
        report = execution_error_json()
        print(json.dumps(report, sort_keys=True))
        return 1
    if args.json:
        try:
            print_summary(summary, file=sys.stderr)
            report = json_summary(summary)
        except Exception as exc:
            print(f"[FAIL] quality_gate result error: {exc}", file=sys.stderr)
            report = execution_error_json()
        print(json.dumps(report, sort_keys=True))
        return int(report["exit_code"])
    print_summary(summary)
    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
