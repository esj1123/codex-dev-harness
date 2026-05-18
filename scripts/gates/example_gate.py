"""Example skeleton validation gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

try:
    from render_template import parse_scalar_config
except ModuleNotFoundError:
    from scripts.render_template import parse_scalar_config


REQUIRED_EXAMPLES = {
    "python_cli_minimal": "python_cli",
    "csharp_desktop_minimal": "csharp_desktop",
    "plc_tool_minimal": "plc_or_device_tool",
}

COMMON_REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "AGENTS.override.md",
    "PRODUCT.md",
    "MVP.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    "SAFETY_POLICY.profile.md",
    "VERIFICATION.profile.md",
    "template.config.yml",
]


@dataclass(frozen=True)
class PhraseCheck:
    label: str
    pattern: re.Pattern[str]


PROFILE_CHECKS = {
    "python_cli": [
        PhraseCheck("pytest NOT RUN", re.compile(r"pytest[\s|:.-]+not run", re.IGNORECASE)),
        PhraseCheck("CLI smoke NOT RUN", re.compile(r"cli smoke[\s|:.-]+not run", re.IGNORECASE)),
        PhraseCheck("synthetic fixtures only", re.compile(r"synthetic fixtures only", re.IGNORECASE)),
    ],
    "csharp_desktop": [
        PhraseCheck("build NOT RUN", re.compile(r"build[\s|:.-]+not run", re.IGNORECASE)),
        PhraseCheck("test NOT RUN", re.compile(r"test[\s|:.-]+not run", re.IGNORECASE)),
        PhraseCheck("smoke NOT RUN", re.compile(r"smoke[\s|:.-]+not run", re.IGNORECASE)),
        PhraseCheck("no solution/project/source/scripts in skeleton", re.compile(r"no .*source code.*solution.*project.*script", re.IGNORECASE | re.DOTALL)),
    ],
    "plc_or_device_tool": [
        PhraseCheck("simulator/mock first", re.compile(r"simulator/mock first", re.IGNORECASE)),
        PhraseCheck("live device write prohibited", re.compile(r"live device write (?:is )?prohibited", re.IGNORECASE)),
        PhraseCheck("IP/port/tag/live parameter prohibited", re.compile(r"equipment ip.*ports?.*tag.*live (?:control )?parameters?", re.IGNORECASE | re.DOTALL)),
        PhraseCheck("start/stop/reset/mode change prohibited", re.compile(r"start.*stop.*reset.*mode change", re.IGNORECASE | re.DOTALL)),
    ],
}


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def read_example_text(example_dir: Path) -> str:
    chunks: list[str] = []
    for path in sorted(example_dir.glob("*.md")) + sorted(example_dir.glob("*.yml")):
        chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def validate_example_config(example_dir: Path, example_name: str, profile: str) -> list[str]:
    findings: list[str] = []
    config_path = example_dir / "template.config.yml"
    if not config_path.is_file():
        return [f"missing examples/{example_name}/template.config.yml"]

    values = parse_scalar_config(config_path)
    expected_values = {
        "project.name": example_name,
        "project.status": "seed",
        "profile.name": profile,
        "paths.target": f"examples/{example_name}",
    }
    if example_name == "plc_tool_minimal":
        expected_values["safety.live_device_write"] = "prohibited"

    for key, expected in expected_values.items():
        actual = values.get(key, "")
        if actual != expected:
            findings.append(f"examples/{example_name}/template.config.yml expected {key}={expected}, got {actual or 'missing'}")

    return findings


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    examples_root = repo_root / "examples"
    if not examples_root.is_dir():
        return GateResult("example_gate", False, ["missing examples/ directory"])

    for example_name, profile in REQUIRED_EXAMPLES.items():
        example_dir = examples_root / example_name
        if not example_dir.is_dir():
            findings.append(f"missing example directory: examples/{example_name}")
            continue

        for filename in COMMON_REQUIRED_FILES:
            if not (example_dir / filename).is_file():
                findings.append(f"missing examples/{example_name}/{filename}")

        findings.extend(validate_example_config(example_dir, example_name, profile))

        text = read_example_text(example_dir)
        for check in PROFILE_CHECKS[profile]:
            if not check.pattern.search(text):
                findings.append(f"examples/{example_name} missing phrase: {check.label}")

    if findings:
        return GateResult("example_gate", False, findings)
    return GateResult("example_gate", True, [f"validated examples: {len(REQUIRED_EXAMPLES)}"])
