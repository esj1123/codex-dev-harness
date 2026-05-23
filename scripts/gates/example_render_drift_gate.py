"""Example render drift gate.

Checks that each regression example contains the files that the renderer would
produce from its template.config.yml. This gate does not compare file content.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_template import iter_templates, load_config, template_destination  # noqa: E402

from gates.example_gate import REQUIRED_EXAMPLES  # noqa: E402


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def expected_rendered_files(repo_root: Path, example_name: str) -> list[Path]:
    example_dir = repo_root / "examples" / example_name
    config = load_config(example_dir / "template.config.yml")
    base_dir = repo_root / "templates" / "base"
    profile_dir = repo_root / "profiles" / config.profile if config.profile else None
    return [
        template_destination(source, source_root, example_dir)
        for source, source_root in iter_templates(base_dir, profile_dir)
    ]


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    checked = 0

    for example_name in REQUIRED_EXAMPLES:
        example_dir = repo_root / "examples" / example_name
        if not example_dir.is_dir():
            findings.append(f"missing example directory: examples/{example_name}")
            continue

        for expected_path in expected_rendered_files(repo_root, example_name):
            checked += 1
            if not expected_path.is_file():
                relative = expected_path.relative_to(repo_root)
                findings.append(f"missing rendered example file: {relative}")

    if findings:
        return GateResult("example_render_drift_gate", False, findings)
    return GateResult("example_render_drift_gate", True, [f"expected rendered example files present: {checked}"])
