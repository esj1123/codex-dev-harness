"""Standalone eval gate wrapper.

This gate is intentionally not wired into scripts/quality_gate.py by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_eval  # noqa: E402


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def run(repo_root: Path) -> GateResult:
    summary = run_eval.run_all(repo_root)
    messages: list[str] = []
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        messages.append(f"{status} {result.name}")
        messages.extend(result.messages)
    return GateResult("eval_gate", summary.passed, messages)


def main() -> int:
    result = run(Path(__file__).resolve().parents[2])
    status = "PASS" if result.passed else "FAIL"
    print(f"[{status}] {result.name}")
    for message in result.messages:
        print(f"  - {message}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
