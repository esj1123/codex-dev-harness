"""Golden rendered content drift gate.

This gate compares raw renderer output against a tracked golden fixture. It does
not inspect the curated examples, which may intentionally differ from generated
snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_template import (  # noqa: E402
    TemplateConfig,
    iter_templates,
    render_text,
    template_destination,
    validate_render_tier,
)


GATE_NAME = "rendered_golden_content_gate"
FIXTURE_RELATIVE = Path("evals/golden/rendered_python_cli_contract.json")
SCHEMA_VERSION = "1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def canonical_render_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(canonical_render_text(text).encode("utf-8")).hexdigest()


def rendered_file_hashes(repo_root: Path, config: TemplateConfig) -> dict[str, str]:
    base_dir = repo_root / "templates" / "base"
    profile_dir = repo_root / "profiles" / config.profile if config.profile else None
    synthetic_target = Path("__golden_render_target__")
    hashes: dict[str, str] = {}

    if not base_dir.is_dir():
        raise FileNotFoundError(f"missing base template directory: {base_dir}")
    if config.profile and (profile_dir is None or not profile_dir.is_dir()):
        raise FileNotFoundError(f"missing profile template directory: {profile_dir}")

    for source, source_root in iter_templates(base_dir, profile_dir, config.tier):
        destination = template_destination(source, source_root, synthetic_target)
        relative = destination.relative_to(synthetic_target).as_posix()
        rendered = render_text(source.read_text(encoding="utf-8"), config)
        if relative in hashes:
            raise ValueError(f"duplicate rendered path: {relative}")
        hashes[relative] = sha256_text(rendered)

    return dict(sorted(hashes.items()))


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def load_fixture(repo_root: Path) -> tuple[TemplateConfig, dict[str, str]]:
    fixture_path = repo_root / FIXTURE_RELATIVE
    if not fixture_path.is_file():
        raise FileNotFoundError(f"missing golden render fixture: {FIXTURE_RELATIVE.as_posix()}")

    data = _require_object(json.loads(fixture_path.read_text(encoding="utf-8")), "fixture")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"fixture schema_version must be {SCHEMA_VERSION}")
    if data.get("hash_algorithm") != "sha256":
        raise ValueError("fixture hash_algorithm must be sha256")
    if data.get("newline_policy") != "lf-normalized":
        raise ValueError("fixture newline_policy must be lf-normalized")

    render = _require_object(data.get("render"), "fixture.render")
    tier = _require_string(render.get("tier", "full"), "fixture.render.tier")
    validate_render_tier(tier)
    config = TemplateConfig(
        project_name=_require_string(render.get("project_name"), "fixture.render.project_name"),
        project_status=_require_string(render.get("project_status"), "fixture.render.project_status"),
        profile=_require_string(render.get("profile"), "fixture.render.profile"),
        tier=tier,
    )
    if config.project_status != "seed":
        raise ValueError("fixture.render.project_status must be seed")

    records = data.get("expected_files")
    if not isinstance(records, list) or not records:
        raise ValueError("fixture.expected_files must be a non-empty list")

    expected: dict[str, str] = {}
    ordered_paths: list[str] = []
    for index, record in enumerate(records):
        entry = _require_object(record, f"fixture.expected_files[{index}]")
        relative = _require_string(entry.get("path"), f"fixture.expected_files[{index}].path")
        digest = _require_string(entry.get("sha256"), f"fixture.expected_files[{index}].sha256")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or "\\" in relative:
            raise ValueError(f"fixture path must be repo-neutral relative POSIX path: {relative}")
        if relative.startswith("examples/"):
            raise ValueError(f"fixture path must target the synthetic render root, not examples/: {relative}")
        if not SHA256_RE.fullmatch(digest):
            raise ValueError(f"fixture sha256 must be lowercase hex: {relative}")
        if relative in expected:
            raise ValueError(f"duplicate fixture path: {relative}")
        expected[relative] = digest
        ordered_paths.append(relative)

    if ordered_paths != sorted(ordered_paths):
        raise ValueError("fixture.expected_files paths must be sorted")

    return config, expected


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    try:
        config, expected = load_fixture(repo_root)
        actual = rendered_file_hashes(repo_root, config)
    except Exception as exc:  # noqa: BLE001 - gate should report validation errors.
        return GateResult(GATE_NAME, False, [str(exc)])

    expected_paths = set(expected)
    actual_paths = set(actual)
    for path in sorted(expected_paths - actual_paths):
        findings.append(f"missing rendered golden file: {path}")
    for path in sorted(actual_paths - expected_paths):
        findings.append(f"unexpected rendered golden file: {path}")
    for path in sorted(expected_paths & actual_paths):
        if expected[path] != actual[path]:
            findings.append(f"rendered golden content hash drift: {path}")

    if findings:
        return GateResult(GATE_NAME, False, findings)
    return GateResult(GATE_NAME, True, [f"validated golden rendered content hashes: {len(actual)} files"])
