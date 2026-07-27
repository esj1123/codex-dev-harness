from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agent_quality_lib.adoption import build_baseline, compare_baseline
from scripts.agent_quality_lib.aggregation import aggregate_runs, compare_role_aggregates
from scripts.agent_quality_lib.capture import capture_run, write_captured_run
from scripts.agent_quality_lib.contracts import (
    AgentQualityValidationError,
    load_json_file,
    validate_run,
)
from scripts.agent_quality_lib.failure import validate_failure_case, validate_failure_transition


SCHEMA_VERSION = "1"
CLI_ID = "agent_quality"
MAX_OUTPUT_BYTES = 16 * 1024
MAX_RUN_FILES = 64
BASELINE_PATH = REPO_ROOT / "artifacts" / "agent-quality-baseline.json"
READ_ROOTS = (
    REPO_ROOT / "evals" / "agentic",
    REPO_ROOT / "local" / "agent-quality",
    Path(tempfile.gettempdir()),
)


class UsageError(ValueError):
    pass


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError("CLI_USAGE_INVALID")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_allowed_input(value: str, *, directory: bool = False) -> Path:
    candidate = Path(value)
    if not directory and candidate.suffix.lower() != ".json":
        raise AgentQualityValidationError(("JSON_INPUT_EXTENSION_INVALID",))
    try:
        if candidate.is_symlink():
            raise AgentQualityValidationError(("JSON_INPUT_SYMLINK_FORBIDDEN",))
        resolved = candidate.resolve(strict=True)
    except AgentQualityValidationError:
        raise
    except OSError as exc:
        raise AgentQualityValidationError(("JSON_INPUT_UNAVAILABLE",)) from exc

    roots = []
    for root in READ_ROOTS:
        try:
            roots.append(root.resolve(strict=False))
        except OSError:
            continue
    if not any(_is_within(resolved, root) for root in roots):
        raise AgentQualityValidationError(("JSON_INPUT_BOUNDARY_INVALID",))
    if directory:
        if not resolved.is_dir():
            raise AgentQualityValidationError(("RUNS_DIRECTORY_INVALID",))
    elif not resolved.is_file():
        raise AgentQualityValidationError(("JSON_INPUT_NOT_REGULAR_FILE",))
    return resolved


def _load_allowed_json(value: str) -> Any:
    return load_json_file(_resolve_allowed_input(value))


def _load_exact_baseline(value: str) -> Any:
    candidate = Path(value)
    if candidate.suffix.lower() != ".json":
        raise AgentQualityValidationError(("JSON_INPUT_EXTENSION_INVALID",))
    try:
        if candidate.is_symlink():
            raise AgentQualityValidationError(("JSON_INPUT_SYMLINK_FORBIDDEN",))
        resolved = candidate.resolve(strict=True)
    except AgentQualityValidationError:
        raise
    except OSError as exc:
        raise AgentQualityValidationError(("JSON_INPUT_UNAVAILABLE",)) from exc
    if resolved != BASELINE_PATH.resolve(strict=False):
        raise AgentQualityValidationError(("JSON_INPUT_BOUNDARY_INVALID",))
    if not resolved.is_file():
        raise AgentQualityValidationError(("JSON_INPUT_NOT_REGULAR_FILE",))
    return load_json_file(resolved)


def _result(status: str, reason_codes: list[str], command: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": CLI_ID,
        "command": command,
        "status": status,
        "reason_codes": sorted(set(reason_codes)),
        "performed_actions": [],
    }


def _validate_run_command(path: str) -> dict[str, Any]:
    run = validate_run(_load_allowed_json(path))
    return {
        **_result("PASS", [], "validate-run"),
        "validation_summary": {
            "comparability": run["fingerprint"]["comparability"],
            "run_count": 1,
        },
    }


def _aggregate_command(suite_path: str, runs_dir: str) -> dict[str, Any]:
    suite, runs = _load_suite_and_runs(suite_path, runs_dir)
    return aggregate_runs(suite, runs)


def _load_suite_and_runs(
    suite_path: str, runs_dir: str
) -> tuple[dict[str, Any], list[Any]]:
    suite = _load_allowed_json(suite_path)
    if not isinstance(suite, dict):
        raise AgentQualityValidationError(("SUITE_INPUT_INVALID",))
    directory = _resolve_allowed_input(runs_dir, directory=True)
    run_paths = sorted(directory.glob("*.json"), key=lambda path: path.name)
    if not run_paths or len(run_paths) > MAX_RUN_FILES:
        raise AgentQualityValidationError(("RUN_FILE_COUNT_INVALID",))
    if any(path.is_symlink() or not path.is_file() for path in run_paths):
        raise AgentQualityValidationError(("RUN_FILE_INVALID",))
    return suite, [load_json_file(path) for path in run_paths]


def _compare_command(
    baseline_path: str, suite_path: str, runs_dir: str
) -> dict[str, Any]:
    baseline = _load_exact_baseline(baseline_path)
    suite, runs = _load_suite_and_runs(suite_path, runs_dir)
    candidate = aggregate_runs(suite, runs)
    if candidate.get("schema_version") == "2":
        return compare_role_aggregates(baseline, candidate)
    return compare_baseline(baseline, candidate, suite=suite)


def _validate_failure_command(path: str, next_case: str | None) -> dict[str, Any]:
    failure = _load_allowed_json(path)
    if next_case is None:
        return validate_failure_case(failure)
    return validate_failure_transition(failure, _load_allowed_json(next_case))


def _write_baseline_command(
    suite_path: str,
    runs_dir: str,
    output_path: str,
    approval_ref: str,
    created_at: str,
) -> dict[str, Any]:
    output = Path(output_path).resolve(strict=False)
    if output != BASELINE_PATH.resolve(strict=False):
        raise AgentQualityValidationError(("BASELINE_OUTPUT_PATH_INVALID",))
    if output.exists():
        raise AgentQualityValidationError(("BASELINE_OVERWRITE_FORBIDDEN",))
    suite, runs = _load_suite_and_runs(suite_path, runs_dir)
    aggregate = aggregate_runs(suite, runs)
    if aggregate["status"] != "PASS":
        raise AgentQualityValidationError(("BASELINE_ADOPTION_INELIGIBLE",))
    baseline = build_baseline(
        aggregate,
        suite=suite,
        approval_ref=approval_ref,
        created_at=created_at,
    )
    data = (json.dumps(baseline, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode(
        "utf-8"
    )
    if len(data) > MAX_OUTPUT_BYTES:
        raise AgentQualityValidationError(("BASELINE_OUTPUT_TOO_LARGE",))
    output.parent.mkdir(parents=False, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(data)
    return {
        **_result("PASS WITH NOTES", ["PROVISIONAL_BASELINE_RECORDED"], "write-baseline"),
        "baseline_summary": {
            "baseline_id": baseline["baseline_id"],
            "run_count": baseline["run_count"],
            "task_count": baseline["task_count"],
        },
        "performed_actions": ["local_write"],
    }


def _resolve_capture_output(value: str) -> Path:
    candidate = Path(value)
    if candidate.suffix.lower() != ".json":
        raise AgentQualityValidationError(("RUN_OUTPUT_EXTENSION_INVALID",))
    resolved = candidate.resolve(strict=False)
    roots = (
        (REPO_ROOT / "local" / "agent-quality").resolve(strict=False),
        Path(tempfile.gettempdir()).resolve(strict=False),
    )
    if not any(_is_within(resolved, root) for root in roots):
        raise AgentQualityValidationError(("RUN_OUTPUT_BOUNDARY_INVALID",))
    if resolved.exists():
        raise AgentQualityValidationError(("RUN_OUTPUT_OVERWRITE_FORBIDDEN",))
    if resolved.parent.is_symlink():
        raise AgentQualityValidationError(("RUN_OUTPUT_SYMLINK_FORBIDDEN",))
    return resolved


def _capture_run_command(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = _resolve_allowed_input(args.repo_root, directory=True)
    package_path = _resolve_allowed_input(args.package)
    try:
        package_relative = package_path.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise AgentQualityValidationError(("PACKAGE_REPOSITORY_BOUNDARY_INVALID",)) from exc
    suite = _load_allowed_json(args.suite)
    profiles = _load_allowed_json(args.profiles)
    package = load_json_file(package_path)
    launch_receipt = _load_allowed_json(args.launch_receipt)
    grader_manifest_path = _resolve_allowed_input(args.grader_manifest)
    grader_manifest = load_json_file(grader_manifest_path)
    if not all(
        isinstance(value, dict)
        for value in (suite, profiles, package, launch_receipt, grader_manifest)
    ):
        raise AgentQualityValidationError(("CAPTURE_INPUT_INVALID",))
    run = capture_run(
        suite=suite,
        profiles=profiles,
        package=package,
        package_path=package_relative,
        task_id=args.task_id,
        trial_id=args.trial_id,
        repo_root=repo_root,
        launch_receipt=launch_receipt,
        grader_manifest=grader_manifest,
        grader_manifest_path=grader_manifest_path,
        harness_root=REPO_ROOT,
    )
    output = _resolve_capture_output(args.output)
    write_captured_run(output, run)
    return {
        **_result("PASS", [], "capture-run"),
        "capture_summary": {
            "run_id": run["run_id"],
            "execution_status": run["execution"]["status"],
            "grading_status": run["grading"]["status"],
            "command_count": len(run["execution"]["command_results"]),
        },
        "performed_actions": ["execute", "local_write"],
    }


def json_bytes(result: dict[str, Any]) -> bytes:
    data = (
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")
    if len(data) > MAX_OUTPUT_BYTES:
        raise ValueError("OUTPUT_LIMIT_EXCEEDED")
    return data


def _exit_code(result: dict[str, Any]) -> int:
    if result.get("status") in {"PASS", "PASS WITH NOTES"}:
        return 0
    if result.get("status") == "NOT RUN":
        return 2
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = SafeArgumentParser(description="Validate manual agent-quality evidence.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_run_parser = subparsers.add_parser("validate-run")
    validate_run_parser.add_argument("--run", required=True)
    validate_run_parser.add_argument("--json", action="store_true")

    aggregate_parser = subparsers.add_parser("aggregate")
    aggregate_parser.add_argument("--suite", required=True)
    aggregate_parser.add_argument("--runs-dir", required=True)
    aggregate_parser.add_argument("--json", action="store_true")

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--baseline", required=True)
    compare_parser.add_argument("--suite", required=True)
    compare_parser.add_argument("--runs-dir", required=True)
    compare_parser.add_argument("--json", action="store_true")

    failure_parser = subparsers.add_parser("validate-failure")
    failure_parser.add_argument("--case", required=True)
    failure_parser.add_argument("--next-case")
    failure_parser.add_argument("--json", action="store_true")

    baseline_parser = subparsers.add_parser("write-baseline")
    baseline_parser.add_argument("--suite", required=True)
    baseline_parser.add_argument("--runs-dir", required=True)
    baseline_parser.add_argument("--output", required=True)
    baseline_parser.add_argument("--approval-ref", required=True)
    baseline_parser.add_argument("--created-at", required=True)

    capture_parser = subparsers.add_parser("capture-run")
    capture_parser.add_argument("--suite", required=True)
    capture_parser.add_argument("--profiles", required=True)
    capture_parser.add_argument("--package", required=True)
    capture_parser.add_argument("--task-id", required=True)
    capture_parser.add_argument("--trial-id", required=True)
    capture_parser.add_argument("--repo-root", required=True)
    capture_parser.add_argument("--launch-receipt", required=True)
    capture_parser.add_argument("--grader-manifest", required=True)
    capture_parser.add_argument("--output", required=True)
    capture_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    command = "unknown"
    try:
        args = build_parser().parse_args(argv)
        command = args.command
        if command == "validate-run":
            result = _validate_run_command(args.run)
        elif command == "aggregate":
            result = _aggregate_command(args.suite, args.runs_dir)
        elif command == "compare":
            result = _compare_command(args.baseline, args.suite, args.runs_dir)
        elif command == "validate-failure":
            result = _validate_failure_command(args.case, args.next_case)
        elif command == "capture-run":
            result = _capture_run_command(args)
        else:
            result = _write_baseline_command(
                args.suite,
                args.runs_dir,
                args.output,
                args.approval_ref,
                args.created_at,
            )
    except UsageError:
        result = _result("NOT RUN", ["CLI_USAGE_INVALID"], command)
    except AgentQualityValidationError as exc:
        result = _result("FAIL", list(exc.issues), command)
    except (KeyError, TypeError, ValueError):
        result = _result("FAIL", ["AGENT_QUALITY_INPUT_INVALID"], command)
    except OSError:
        result = _result("ENVIRONMENT BLOCKED", ["FILESYSTEM_UNAVAILABLE"], command)

    try:
        sys.stdout.buffer.write(json_bytes(result))
    except ValueError:
        fallback = _result("FAIL", ["OUTPUT_LIMIT_EXCEEDED"], command)
        sys.stdout.buffer.write(json_bytes(fallback))
        return 1
    return _exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
