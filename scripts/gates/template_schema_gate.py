"""Template config/schema gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_template import load_config  # noqa: E402


REQUIRED_BASE_TEMPLATES = [
    "templates/base/AGENTS.md.template",
    "templates/base/README.md.template",
    "templates/base/PRODUCT.md.template",
    "templates/base/MVP.md.template",
    "templates/base/STATUS.md.template",
    "templates/base/ACCEPTANCE_TRACE.md.template",
    "templates/base/SOURCE_INDEX.md.template",
    "templates/base/PROJECT_BOUNDARY.md.template",
    "templates/base/DATA_SCOPE.md.template",
    "templates/base/PHASE_PLAN.md.template",
    "templates/base/APPROVALS.md.template",
]


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def run(repo_root: Path) -> GateResult:
    messages: list[str] = []
    config_path = repo_root / "template.config.example.yml"
    if not config_path.is_file():
        return GateResult("template_schema_gate", False, ["missing template.config.example.yml"])

    try:
        config = load_config(config_path)
    except Exception as exc:  # noqa: BLE001 - gate should report validation errors.
        return GateResult("template_schema_gate", False, [f"invalid config: {exc}"])

    missing = [path for path in REQUIRED_BASE_TEMPLATES if not (repo_root / path).is_file()]
    if missing:
        return GateResult("template_schema_gate", False, [f"missing base template: {path}" for path in missing])

    messages.append(f"project.name={config.project_name}")
    messages.append(f"project.status={config.project_status}")
    messages.append(f"profile.name={config.profile or 'none'}")
    messages.append(f"base templates present: {len(REQUIRED_BASE_TEMPLATES)}")
    return GateResult("template_schema_gate", True, messages)
