"""Run the repository quality gate for codex-dev-harness."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gates import docs_gate, example_gate, repo_hygiene_gate, secret_scan_gate, template_schema_gate  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class GateSummary:
    passed: bool
    results: list[object]


def run_quality_gate(repo_root: Path = REPO_ROOT) -> GateSummary:
    gates = [
        docs_gate.run,
        repo_hygiene_gate.run,
        template_schema_gate.run,
        example_gate.run,
        secret_scan_gate.run,
    ]
    results = [gate(repo_root) for gate in gates]
    return GateSummary(all(result.passed for result in results), results)


def print_summary(summary: GateSummary) -> None:
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        for message in result.messages:
            print(f"  - {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run codex-dev-harness quality gates.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to check")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    summary = run_quality_gate(Path(args.repo_root).resolve())
    print_summary(summary)
    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
