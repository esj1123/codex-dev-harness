"""Release evidence checksum verification gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_checksums  # noqa: E402


GATE_NAME = "checksum_verify_gate"


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def run(repo_root: Path) -> GateResult:
    repo_root = repo_root.resolve()
    try:
        manifest_path = generate_checksums.resolve_repo_path(
            repo_root,
            generate_checksums.DEFAULT_MANIFEST_PATH,
            "--manifest",
        )
        output_path = generate_checksums.resolve_repo_path(
            repo_root,
            generate_checksums.DEFAULT_CHECKSUMS_PATH,
            "--output",
        )
        passed, messages = generate_checksums.verify_checksums(
            repo_root,
            manifest_path,
            output_path,
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        return GateResult(GATE_NAME, False, [str(exc)])
    return GateResult(GATE_NAME, passed, messages)


def main() -> int:
    result = run(Path(__file__).resolve().parents[2])
    status = "PASS" if result.passed else "FAIL"
    print(f"[{status}] {result.name}")
    for message in result.messages:
        print(f"  - {message}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())