import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import run_eval


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_directory_link(link: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr or result.stdout
    else:
        link.symlink_to(target, target_is_directory=True)


def remove_directory_link(link: Path) -> None:
    if os.name == "nt":
        link.rmdir()
    else:
        link.unlink()


FULL_BASE_OUTPUTS = (
    "AGENTS.md",
    "README.md",
    "PRODUCT.md",
    "MVP.md",
    "PROJECT_BOUNDARY.md",
    "DATA_SCOPE.md",
    "APPROVALS.md",
    "PHASE_PLAN.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    "SOURCE_INDEX.md",
)
FULL_PROFILE_OUTPUTS = (
    "AGENTS.override.md",
    "README.profile.md",
    "STATUS.profile.md",
    "SAFETY_POLICY.profile.md",
    "VERIFICATION.profile.md",
)
FULL_OUTPUTS = tuple(sorted((*FULL_BASE_OUTPUTS, *FULL_PROFILE_OUTPUTS)))
TIER_OUTPUTS = {
    "minimal": (
        "AGENTS.md",
        "AGENTS.override.md",
        "MVP.md",
        "PRODUCT.md",
        "PROJECT_BOUNDARY.md",
        "README.md",
        "SAFETY_POLICY.profile.md",
        "VERIFICATION.profile.md",
    ),
    "standard": (
        "ACCEPTANCE_TRACE.md",
        "AGENTS.md",
        "AGENTS.override.md",
        "APPROVALS.md",
        "DATA_SCOPE.md",
        "MVP.md",
        "PHASE_PLAN.md",
        "PRODUCT.md",
        "PROJECT_BOUNDARY.md",
        "README.md",
        "SAFETY_POLICY.profile.md",
        "STATUS.md",
        "STATUS.profile.md",
        "VERIFICATION.profile.md",
    ),
}


def write_full_tier_templates(root: Path) -> None:
    for output in FULL_BASE_OUTPUTS:
        write(root / "templates" / "base" / f"{output}.template", f"# {output}\n")
    for output in FULL_PROFILE_OUTPUTS:
        write(root / "profiles" / "python_cli" / f"{output}.template", f"# {output}\n")


def render_repo(root: Path) -> None:
    write_full_tier_templates(root)
    write(
        root / "examples/demo/template.config.yml",
        "project:\n  name: demo\n  status: seed\n"
        "profile:\n  name: python_cli\n"
        "render:\n  tier: full\n",
    )
    for output in FULL_OUTPUTS:
        write(root / "examples" / "demo" / output, f"# {output}\n")
    write(
        root / "evals/golden/render_structure_paths.txt",
        "".join(f"examples/demo/{output}\n" for output in FULL_OUTPUTS),
    )


def render_case() -> dict[str, object]:
    return {
        "eval": "render_structure",
        "golden_paths_file": "evals/golden/render_structure_paths.txt",
        "forbidden_suffixes": [".csproj"],
        "examples": [
            {
                "name": "demo",
                "config": "examples/demo/template.config.yml",
                "target": "examples/demo",
                "expected_files": [f"examples/demo/{output}" for output in FULL_OUTPUTS],
            }
        ],
    }


def rendered_readiness_repo(root: Path) -> None:
    write_full_tier_templates(root)
    write(
        root / "templates/base/README.md.template",
        "# {{ project.name }}\n\nProject purpose and current state.\n",
    )
    write(
        root / "templates/base/AGENTS.md.template",
        "Read-only first. Side effect scope, verification, and no-touch rules.\n",
    )
    write(root / "templates/base/STATUS.md.template", "Current state. Next recommended action.\n")
    write(root / "templates/base/ACCEPTANCE_TRACE.md.template", "Acceptance evidence: PASS / FAIL / NOT RUN.\n")
    write(
        root / "profiles/python_cli/SAFETY_POLICY.profile.md.template",
        "Private data, secrets, and live target writes are prohibited.\n",
    )
    write(root / "profiles/python_cli/VERIFICATION.profile.md.template", "Run local verification with synthetic fixtures only.\n")
    write(
        root / "examples/demo/template.config.yml",
        "project:\n  name: demo\n  status: seed\n"
        "profile:\n  name: python_cli\n"
        "render:\n  tier: full\n",
    )


def rendered_readiness_case(min_score: int = 13) -> dict[str, object]:
    return {
        "name": "rendered_demo_readiness",
        "eval": "rendered_readiness",
        "renders": [
            {
                "name": "demo_render",
                "config": "examples/demo/template.config.yml",
                "min_score": min_score,
            }
        ],
    }


def write_passing_eval_case(root: Path, name: str = "alpha_case") -> Path:
    write(root / "AGENTS.md", "explicit confirmation\n")
    case_path = root / "evals/cases/policy.yml"
    write(
        case_path,
        json.dumps(
            {
                "name": name,
                "eval": "policy_phrases",
                "checks": [{"path": "AGENTS.md", "phrases": ["explicit confirmation"]}],
            }
        )
        + "\n",
    )
    return case_path


def test_render_structure_passes_expected_paths(tmp_path: Path) -> None:
    render_repo(tmp_path)

    result = run_eval.run_render_structure(tmp_path, render_case())

    assert result.passed is True
    assert "16" in result.messages[0]


def test_planned_render_paths_honors_minimal_tier(tmp_path: Path) -> None:
    render_repo(tmp_path)
    config_path = tmp_path / "examples/demo/template.config.yml"
    config_text = config_path.read_text(encoding="utf-8")
    write(config_path, config_text.replace("tier: full", "tier: minimal"))

    paths = run_eval.planned_render_paths(tmp_path, config_path, tmp_path / "examples/demo")

    assert paths == [f"examples/demo/{output}" for output in TIER_OUTPUTS["minimal"]]


def test_planned_render_paths_honors_standard_tier(tmp_path: Path) -> None:
    render_repo(tmp_path)
    config_path = tmp_path / "examples/demo/template.config.yml"
    config_text = config_path.read_text(encoding="utf-8")
    write(config_path, config_text.replace("tier: full", "tier: standard"))

    paths = run_eval.planned_render_paths(tmp_path, config_path, tmp_path / "examples/demo")

    assert paths == [f"examples/demo/{output}" for output in TIER_OUTPUTS["standard"]]


def test_render_structure_detects_missing_expected_file(tmp_path: Path) -> None:
    render_repo(tmp_path)
    (tmp_path / "examples/demo/STATUS.md").unlink()

    result = run_eval.run_render_structure(tmp_path, render_case())

    assert result.passed is False
    assert any("STATUS.md" in message for message in result.messages)


def test_rendered_readiness_passes_scanner_threshold(tmp_path: Path) -> None:
    rendered_readiness_repo(tmp_path)

    result = run_eval.run_rendered_readiness(tmp_path, rendered_readiness_case())

    assert result.passed is True
    assert "1" in result.messages[0]


def test_rendered_readiness_detects_low_score(tmp_path: Path) -> None:
    rendered_readiness_repo(tmp_path)

    result = run_eval.run_rendered_readiness(tmp_path, rendered_readiness_case(min_score=16))

    assert result.passed is False
    assert any("below minimum 16" in message for message in result.messages)


def test_policy_phrases_detects_missing_phrase(tmp_path: Path) -> None:
    write(tmp_path / "AGENTS.md", "read-only first\n")
    case = {"eval": "policy_phrases", "checks": [{"path": "AGENTS.md", "phrases": ["explicit confirmation"]}]}

    result = run_eval.run_policy_phrases(tmp_path, case)

    assert result.passed is False
    assert "explicit confirmation" in result.messages[0]


def test_forbidden_artifacts_detects_application_file(tmp_path: Path) -> None:
    write(tmp_path / "examples/demo/App.csproj", "<Project />\n")
    case = {
        "eval": "forbidden_artifacts",
        "ignored_root_parts": [".git", "local"],
        "forbidden_path_globs": ["examples/**/*.csproj"],
        "forbidden_suffixes": [".csproj"],
        "text_suffixes": [".md", ".yml"],
    }

    result = run_eval.run_forbidden_artifacts(tmp_path, case)

    assert result.passed is False
    assert any("App.csproj" in message for message in result.messages)


@pytest.mark.parametrize("root_name", ["local", ".venv"])
def test_forbidden_artifacts_ignores_tool_root(
    tmp_path: Path, root_name: str
) -> None:
    write(tmp_path / root_name / "examples/demo/App.csproj", "<Project />\n")
    case = {
        "eval": "forbidden_artifacts",
        "ignored_root_parts": [root_name],
        "forbidden_path_globs": ["examples/**/*.csproj"],
        "forbidden_suffixes": [".csproj"],
        "text_suffixes": [".md", ".yml"],
    }

    result = run_eval.run_forbidden_artifacts(tmp_path, case)

    assert result.passed is True


def test_iter_repo_files_preserves_rglob_path_order(tmp_path: Path) -> None:
    write(tmp_path / "root.txt", "root\n")
    write(tmp_path / "alpha" / "alpha.txt", "alpha\n")
    write(tmp_path / "alpha" / "deep" / "deep.txt", "deep\n")
    write(tmp_path / "beta" / "beta.txt", "beta\n")
    write(tmp_path / "docs" / "local" / "nested.txt", "nested\n")
    write(tmp_path / "local" / "ignored.txt", "ignored\n")
    ignored_root_parts = {"local"}
    expected = []
    for path in tmp_path.rglob("*"):
        relative_parts = path.relative_to(tmp_path).parts
        if relative_parts and relative_parts[0] in ignored_root_parts:
            continue
        if path.is_file():
            expected.append(path)

    actual = run_eval.iter_repo_files(tmp_path, ignored_root_parts)

    assert [path.relative_to(tmp_path) for path in actual] == [
        path.relative_to(tmp_path) for path in expected
    ]


def test_iter_repo_files_prunes_ignored_roots_before_visit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path / "local" / "deep" / "ignored.txt", "ignored\n")
    write(tmp_path / ".venv" / "deep" / "ignored.txt", "ignored\n")
    write(tmp_path / "kept" / "visible.txt", "visible\n")
    original_walk = run_eval.os.walk
    visited: list[Path] = []

    def recording_walk(*args, **kwargs):
        for item in original_walk(*args, **kwargs):
            visited.append(Path(item[0]))
            yield item

    monkeypatch.setattr(run_eval.os, "walk", recording_walk)

    files = run_eval.iter_repo_files(tmp_path, {".venv", "local"})

    assert [path.relative_to(tmp_path).as_posix() for path in files] == [
        "kept/visible.txt"
    ]
    assert all(
        not relative.parts or relative.parts[0] not in {".venv", "local"}
        for relative in (path.relative_to(tmp_path) for path in visited)
    )


def test_iter_repo_files_prunes_directory_link_and_keeps_sibling(
    tmp_path: Path,
) -> None:
    target = tmp_path / "local" / "outside"
    write(target / "linked.csproj", "<Project />\n")
    link = tmp_path / "linked"
    create_directory_link(link, target)
    sibling = tmp_path / "examples" / "demo" / "App.csproj"
    write(sibling, "<Project />\n")
    try:
        files = run_eval.iter_repo_files(tmp_path, {"local"})
    finally:
        remove_directory_link(link)

    relative = [path.relative_to(tmp_path) for path in files]
    assert Path("examples/demo/App.csproj") in relative
    assert all(not path.parts or path.parts[0] != "linked" for path in relative)


@pytest.mark.parametrize(
    "render_name",
    ["../escape", "nested/escape", r"nested\escape", r"C:\escape", "/escape", ".."],
)
def test_rendered_readiness_rejects_unsafe_render_name(
    tmp_path: Path, render_name: str
) -> None:
    case = {
        "name": "unsafe_render_name",
        "renders": [{"name": render_name, "config": "missing.yml"}],
    }

    result = run_eval.run_rendered_readiness(tmp_path, case)

    assert result.passed is False
    assert result.messages == [f"unsafe render name rejected: {render_name!r}"]


def test_resolve_report_path_accepts_repo_relative_path(tmp_path: Path) -> None:
    result = run_eval.resolve_report_path(tmp_path, "artifacts/eval-report.json")

    assert result == tmp_path.resolve() / "artifacts" / "eval-report.json"


def test_resolve_report_path_rejects_non_artifact_path(tmp_path: Path) -> None:
    try:
        run_eval.resolve_report_path(tmp_path, "STATUS.md")
    except ValueError as exc:
        assert "artifacts/" in str(exc)
    else:
        raise AssertionError("non-artifact report path should be rejected")


def test_resolve_report_path_rejects_absolute_path(tmp_path: Path) -> None:
    absolute_report = tmp_path.resolve() / "eval-report.json"

    try:
        run_eval.resolve_report_path(tmp_path, str(absolute_report))
    except ValueError as exc:
        assert "relative path" in str(exc)
    else:
        raise AssertionError("absolute report path should be rejected")


def test_resolve_report_path_rejects_parent_traversal(tmp_path: Path) -> None:
    try:
        run_eval.resolve_report_path(tmp_path, "../eval-report.json")
    except ValueError as exc:
        assert "parent traversal" in str(exc)
    else:
        raise AssertionError("parent traversal should be rejected")


def test_default_eval_case_discovery_has_expanded_named_cases() -> None:
    case_paths = run_eval.discover_case_paths(run_eval.REPO_ROOT)
    case_names = [run_eval.load_case(path).get("name") for path in case_paths]

    assert len(case_paths) >= 10
    assert "render_structure_base_docs" in case_names
    assert "rendered_python_cli_readiness" in case_names
    assert "checksum_shape" in case_names
    assert "provenance_shape" in case_names
    assert all(case_names)


def test_eval_case_discovery_order_is_deterministic() -> None:
    case_paths = run_eval.discover_case_paths(run_eval.REPO_ROOT)
    case_filenames = [path.name for path in case_paths]

    assert case_filenames == sorted(case_filenames)


def test_empty_eval_inventory_is_a_bounded_control_failure(
    tmp_path: Path,
) -> None:
    summary = run_eval.run_all(tmp_path, [])

    assert summary.passed is False
    assert summary.results == [
        run_eval.EvalResult(
            "eval_case_inventory",
            False,
            ["no eval cases discovered"],
        )
    ]


def test_empty_discovered_eval_inventory_makes_cli_exit_one(
    tmp_path: Path,
    capsys,
) -> None:
    exit_code = run_eval.main(["--repo-root", str(tmp_path)])

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "[FAIL] eval_case_inventory" in output
    assert "Local evals failed." in output
    assert not (tmp_path / "artifacts").exists()


def test_json_cli_success_is_safe_non_reporting_and_uses_indexed_ids(
    tmp_path: Path,
    capsys,
) -> None:
    unsafe_name = "private-case-C:/Users/example-secret"
    case_path = write_passing_eval_case(tmp_path, name=unsafe_name)

    exit_code = run_eval.main(
        ["--repo-root", str(tmp_path), "--case", str(case_path), "--json"]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload == {
        "schema_version": "1",
        "checker_id": "local_eval",
        "status": "PASS",
        "exit_code": 0,
        "counts": {"total": 1, "passed": 1, "failed": 0},
        "results": [{"check_id": "case_0001", "status": "PASS", "message_count": 1}],
        "omitted_result_count": 0,
        "reason_codes": [],
        "report_written": False,
    }
    assert unsafe_name not in captured.out
    assert "validated phrase targets" not in captured.out
    assert unsafe_name in captured.err
    assert not (tmp_path / "artifacts").exists()


def test_json_cli_failure_and_case_filtering_preserve_invocation_order(
    tmp_path: Path,
    capsys,
) -> None:
    passing = write_passing_eval_case(tmp_path, name="unsafe-pass-name")
    failing = tmp_path / "evals/cases/failing.yml"
    write(failing, json.dumps({"name": "unsafe-fail-name", "eval": "unknown"}) + "\n")

    exit_code = run_eval.main(
        [
            "--repo-root",
            str(tmp_path),
            "--case",
            str(failing),
            "--case",
            str(passing),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["counts"] == {"total": 2, "passed": 1, "failed": 1}
    assert payload["results"] == [
        {"check_id": "case_0001", "status": "FAIL", "message_count": 1},
        {"check_id": "case_0002", "status": "PASS", "message_count": 1},
    ]
    assert payload["reason_codes"] == ["RESULT_FAILED"]
    assert "unsafe-fail-name" not in captured.out
    assert "unsafe-pass-name" not in captured.out


def test_json_cli_no_cases_fails_closed(tmp_path: Path, capsys) -> None:
    exit_code = run_eval.main(["--repo-root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["counts"] == {"total": 1, "passed": 0, "failed": 1}
    assert payload["reason_codes"] == ["NO_CASES", "RESULT_FAILED"]
    assert payload["report_written"] is False
    assert not (tmp_path / "artifacts").exists()


def test_json_cli_invalid_case_emits_one_safe_failure_object(
    tmp_path: Path,
    capsys,
) -> None:
    invalid_case = tmp_path / "evals/cases/invalid.yml"
    write(invalid_case, "not json\n")

    exit_code = run_eval.main(
        ["--repo-root", str(tmp_path), "--case", str(invalid_case), "--json"]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["counts"] == {"total": 0, "passed": 0, "failed": 0}
    assert payload["results"] == []
    assert payload["reason_codes"] == ["EXECUTION_ERROR"]
    assert str(invalid_case) not in captured.out
    assert str(invalid_case) in captured.err


def test_json_projection_is_bounded_but_counts_use_all_results() -> None:
    results = [
        run_eval.EvalResult(f"unsafe-{index}", index != 104, ["message"])
        for index in range(105)
    ]

    payload = run_eval.summary_to_json_result(run_eval.EvalSummary(False, results))

    assert payload["counts"] == {"total": 105, "passed": 104, "failed": 1}
    assert len(payload["results"]) == 100
    assert payload["results"][0] == {
        "check_id": "case_0105",
        "status": "FAIL",
        "message_count": 1,
    }
    assert payload["results"][-1]["check_id"] == "case_0099"
    assert payload["omitted_result_count"] == 5
    assert payload["status"] == "FAIL"
    assert payload["reason_codes"] == ["RESULT_FAILED"]
    assert "unsafe-" not in json.dumps(payload)


@pytest.mark.parametrize(
    ("summary", "reason_codes"),
    [
        (run_eval.EvalSummary(True, []), ["NO_RESULTS", "SUMMARY_INCONSISTENT"]),
        (
            run_eval.EvalSummary(False, [run_eval.EvalResult("unsafe", True, [])]),
            ["SUMMARY_INCONSISTENT"],
        ),
        (
            run_eval.EvalSummary(True, [run_eval.EvalResult("unsafe", False, [])]),
            ["RESULT_FAILED", "SUMMARY_INCONSISTENT"],
        ),
    ],
)
def test_json_empty_or_inconsistent_summary_never_passes(
    summary: run_eval.EvalSummary,
    reason_codes: list[str],
) -> None:
    payload = run_eval.summary_to_json_result(summary)

    assert payload["status"] == "FAIL"
    assert payload["exit_code"] == 1
    assert payload["reason_codes"] == reason_codes


def test_json_cli_catches_execution_exception(monkeypatch, capsys) -> None:
    def fail_run(*_args, **_kwargs):
        raise RuntimeError("unsafe-exception-detail")

    monkeypatch.setattr(run_eval, "run_all", fail_run)

    exit_code = run_eval.main(["--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["reason_codes"] == ["EXECUTION_ERROR"]
    assert "unsafe-exception-detail" not in captured.out
    assert "unsafe-exception-detail" in captured.err


@pytest.mark.parametrize(
    "report_flags",
    [
        ["--report", "artifacts/eval.json"],
        ["--summary-report", "artifacts/summary.json"],
        ["--cases-report", "artifacts/cases.jsonl"],
        ["--report="],
        ["--summary-report="],
        ["--cases-report="],
    ],
)
def test_json_rejects_report_flags_before_eval_or_write(
    tmp_path: Path,
    monkeypatch,
    report_flags: list[str],
) -> None:
    called = False

    def record_run(*_args, **_kwargs):
        nonlocal called
        called = True
        return run_eval.EvalSummary(True, [])

    monkeypatch.setattr(run_eval, "run_all", record_run)

    with pytest.raises(SystemExit) as exc_info:
        run_eval.main(["--repo-root", str(tmp_path), "--json", *report_flags])

    assert exc_info.value.code == 2
    assert called is False
    assert not (tmp_path / "artifacts").exists()


def test_summary_report_shape_is_safe_and_stable() -> None:
    summary = run_eval.EvalSummary(
        False,
        [
            run_eval.EvalResult("alpha_case", True, ["ok"]),
            run_eval.EvalResult("beta_case", False, ["bad"]),
        ],
    )

    report = run_eval.summary_to_report(summary, generated_at_utc="2026-05-26T00:00:00Z")

    assert report["schema_version"] == "1"
    assert report["generated_at_utc"] == "2026-05-26T00:00:00Z"
    assert report["total_cases"] == 2
    assert report["passed_cases"] == 1
    assert report["failed_cases"] == 1
    assert report["cases"] == [
        {"name": "alpha_case", "passed": True, "messages": ["ok"]},
        {"name": "beta_case", "passed": False, "messages": ["bad"]},
    ]
    assert "results" not in report


def test_legacy_report_cli_writes_backward_compatible_report(tmp_path: Path) -> None:
    case_path = write_passing_eval_case(tmp_path)

    exit_code = run_eval.main(
        [
            "--repo-root",
            str(tmp_path),
            "--case",
            str(case_path),
            "--report",
            "artifacts/eval-report.json",
        ]
    )

    report_path = tmp_path / "artifacts/eval-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["schema_version"] == "1"
    assert report["total_cases"] == 1
    assert report["passed_cases"] == 1
    assert report["failed_cases"] == 0
    assert report["passed"] is True
    assert report["cases"] == [{"name": "alpha_case", "passed": True, "messages": ["validated phrase targets: 1"]}]
    assert "cases_ref" not in report
    assert "cases_sha256" not in report
    assert not (tmp_path / "artifacts/eval-report-summary.json").exists()
    assert not (tmp_path / "artifacts/eval-cases.jsonl").exists()


def test_cases_report_bytes_are_jsonl_case_results() -> None:
    summary = run_eval.EvalSummary(
        False,
        [
            run_eval.EvalResult("alpha_case", True, ["ok"]),
            run_eval.EvalResult("beta_case", False, ["bad"]),
        ],
    )

    data = run_eval.cases_report_bytes(summary)
    records = [json.loads(line) for line in data.decode("utf-8").splitlines()]

    assert records == [
        {"messages": ["ok"], "name": "alpha_case", "passed": True},
        {"messages": ["bad"], "name": "beta_case", "passed": False},
    ]
    assert data.endswith(b"\n")


def test_split_summary_report_shape_is_safe_and_stable() -> None:
    summary = run_eval.EvalSummary(True, [run_eval.EvalResult("alpha_case", True, ["ok"])])
    cases_bytes = run_eval.cases_report_bytes(summary)
    cases_sha256 = hashlib.sha256(cases_bytes).hexdigest()

    report = run_eval.summary_to_split_report(
        summary,
        "artifacts/eval-cases.jsonl",
        cases_sha256,
        generated_at_utc="2026-05-26T00:00:00Z",
    )

    assert report == {
        "schema_version": "1",
        "generated_at_utc": "2026-05-26T00:00:00Z",
        "total_cases": 1,
        "passed_cases": 1,
        "failed_cases": 0,
        "passed": True,
        "cases_ref": "artifacts/eval-cases.jsonl",
        "cases_sha256": cases_sha256,
    }
    assert "cases" not in report
    assert "results" not in report


def test_split_reports_cli_writes_summary_cases_and_sha256(tmp_path: Path) -> None:
    case_path = write_passing_eval_case(tmp_path)

    exit_code = run_eval.main(
        [
            "--repo-root",
            str(tmp_path),
            "--case",
            str(case_path),
            "--summary-report",
            "artifacts/eval-report-summary.json",
            "--cases-report",
            "artifacts/eval-cases.jsonl",
        ]
    )

    summary_path = tmp_path / "artifacts/eval-report-summary.json"
    cases_path = tmp_path / "artifacts/eval-cases.jsonl"
    cases_bytes = cases_path.read_bytes()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    case_records = [json.loads(line) for line in cases_bytes.decode("utf-8").splitlines()]

    assert exit_code == 0
    assert summary["schema_version"] == "1"
    assert summary["total_cases"] == 1
    assert summary["passed_cases"] == 1
    assert summary["failed_cases"] == 0
    assert summary["passed"] is True
    assert summary["cases_ref"] == "artifacts/eval-cases.jsonl"
    assert summary["cases_sha256"] == hashlib.sha256(cases_bytes).hexdigest()
    assert case_records == [{"messages": ["validated phrase targets: 1"], "name": "alpha_case", "passed": True}]
    assert not (tmp_path / "artifacts/eval-report.json").exists()


def test_eval_reports_are_not_generated_without_report_flags(tmp_path: Path) -> None:
    case_path = write_passing_eval_case(tmp_path)

    exit_code = run_eval.main(["--repo-root", str(tmp_path), "--case", str(case_path)])

    assert exit_code == 0
    assert not (tmp_path / "artifacts").exists()


def test_split_report_flags_must_be_paired(tmp_path: Path) -> None:
    try:
        run_eval.main(["--repo-root", str(tmp_path), "--summary-report", "artifacts/eval-report-summary.json"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("split report flags should be required as a pair")


def test_split_report_rejects_invalid_path(tmp_path: Path) -> None:
    try:
        run_eval.main(
            [
                "--repo-root",
                str(tmp_path),
                "--summary-report",
                "STATUS.md",
                "--cases-report",
                "artifacts/eval-cases.jsonl",
            ]
        )
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("split summary report path should be restricted to artifacts/")


def test_json_shape_validates_required_fields(tmp_path: Path) -> None:
    write(
        tmp_path / "artifacts/release-manifest.json",
        json.dumps({"schema_version": "1", "files": [{"path": "README.md", "size_bytes": 1, "sha256": "0" * 64}]})
        + "\n",
    )
    case = {
        "name": "release_manifest_shape",
        "eval": "json_shape",
        "files": [
            {
                "path": "artifacts/release-manifest.json",
                "required_top_level": ["schema_version", "files"],
                "list_field": "files",
                "required_list_item_fields": ["path", "size_bytes", "sha256"],
            }
        ],
    }

    result = run_eval.run_json_shape(tmp_path, case)

    assert result.passed is True
    assert result.name == "release_manifest_shape"


def test_checksum_shape_detects_missing_required_artifact(tmp_path: Path) -> None:
    write(tmp_path / "artifacts/checksums.sha256", "0" * 64 + "  artifacts/release-manifest.json\n")
    case = {
        "name": "checksum_shape",
        "eval": "checksum_shape",
        "path": "artifacts/checksums.sha256",
        "required_paths": ["artifacts/release-manifest.json", "artifacts/sbom.spdx.json"],
        "forbidden_paths": ["artifacts/checksums.sha256"],
    }

    result = run_eval.run_checksum_shape(tmp_path, case)

    assert result.passed is False
    assert any("artifacts/sbom.spdx.json" in message for message in result.messages)


def test_checksum_shape_detects_self_reference(tmp_path: Path) -> None:
    write(tmp_path / "artifacts/checksums.sha256", "0" * 64 + "  artifacts/checksums.sha256\n")
    case = {
        "name": "checksum_shape",
        "eval": "checksum_shape",
        "path": "artifacts/checksums.sha256",
        "required_paths": [],
        "forbidden_paths": ["artifacts/checksums.sha256"],
    }

    result = run_eval.run_checksum_shape(tmp_path, case)

    assert result.passed is False
    assert any("forbidden checksum path" in message for message in result.messages)


def test_jsonl_shape_validates_local_provenance(tmp_path: Path) -> None:
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "https://codex-dev-harness.local/provenance/v1",
        "predicate": {
            "schema_version": "1",
            "local_only": True,
            "builder": {"id": "codex-dev-harness-local"},
            "materials": [],
            "products": [],
        },
    }
    write(tmp_path / "artifacts/provenance.intoto.jsonl", json.dumps(statement) + "\n")
    case = {
        "name": "provenance_shape",
        "eval": "jsonl_shape",
        "path": "artifacts/provenance.intoto.jsonl",
        "required_top_level": ["_type", "subject", "predicateType", "predicate"],
        "allowed_predicate_profiles": [
            {
                "predicate_type": "https://codex-dev-harness.local/provenance/v1",
                "schema_version": "1",
                "execution_context": None,
                "local_only": True,
                "builder_id": "codex-dev-harness-local",
            }
        ],
        "required_predicate_fields": ["schema_version", "local_only", "builder", "materials", "products"],
    }

    result = run_eval.run_jsonl_shape(tmp_path, case)

    assert result.passed is True
    assert result.name == "provenance_shape"


def test_jsonl_shape_validates_hosted_manual_export_provenance(tmp_path: Path) -> None:
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "https://codex-dev-harness.local/provenance/v2",
        "predicate": {
            "schema_version": "2",
            "execution_context": "github_actions_manual_export",
            "local_only": False,
            "builder": {"id": "codex-dev-harness-github-actions-manual-export"},
            "repo": {},
            "python_version": "3.12.10",
            "commands": [],
            "input_manifest": {},
            "materials": [],
            "products": [],
        },
    }
    write(tmp_path / "artifacts/provenance.intoto.jsonl", json.dumps(statement) + "\n")
    case = json.loads((run_eval.REPO_ROOT / "evals/cases/provenance_shape.yml").read_text(encoding="utf-8"))

    result = run_eval.run_jsonl_shape(tmp_path, case)

    assert result.passed is True


def test_jsonl_shape_rejects_unapproved_provenance_profile(tmp_path: Path) -> None:
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "https://codex-dev-harness.local/provenance/v2",
        "predicate": {
            "schema_version": "2",
            "execution_context": "github_actions_manual_export",
            "local_only": True,
            "builder": {"id": "codex-dev-harness-github-actions-manual-export"},
            "materials": [],
            "products": [],
        },
    }
    write(tmp_path / "artifacts/provenance.intoto.jsonl", json.dumps(statement) + "\n")
    case = json.loads((run_eval.REPO_ROOT / "evals/cases/provenance_shape.yml").read_text(encoding="utf-8"))

    result = run_eval.run_jsonl_shape(tmp_path, case)

    assert result.passed is False
    assert any("profile is not approved" in message for message in result.messages)


def _report_options() -> dict[str, str]:
    return {
        "--report": "artifacts/legacy.json",
        "--summary-report": "artifacts/summary.json",
        "--cases-report": "artifacts/cases.jsonl",
    }


def _report_flags(options: dict[str, str]) -> list[str]:
    return [token for option, relative in options.items() for token in (option, relative)]


@pytest.mark.parametrize("slot", ["--report", "--summary-report", "--cases-report"])
@pytest.mark.parametrize("inside_repo", [False, True])
def test_report_hardlink_is_rejected_before_any_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, slot: str, inside_repo: bool,
) -> None:
    repo = tmp_path / "repo"
    case = write_passing_eval_case(repo)
    options = _report_options()
    protected = repo / "STATUS.md" if inside_repo else tmp_path / "outside.txt"
    protected.write_bytes(b"preserve protected content\n")
    for option, relative in options.items():
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if option == slot:
            os.link(protected, destination)
        else:
            destination.write_bytes(b"preserve companion report\n")
    before = {relative: (repo / relative).read_bytes() for relative in options.values()}
    monkeypatch.setattr(
        run_eval, "run_all", lambda *_args: pytest.fail("unsafe output must stop before eval")
    )

    with pytest.raises(SystemExit) as error:
        run_eval.main(["--repo-root", str(repo), "--case", str(case), *_report_flags(options)])

    assert error.value.code == 2
    assert protected.read_bytes() == b"preserve protected content\n"
    assert {relative: (repo / relative).read_bytes() for relative in options.values()} == before
    assert not list((repo / "artifacts").glob(".*.codex-*.tmp"))


@pytest.mark.parametrize("slot", ["--report", "--summary-report", "--cases-report"])
@pytest.mark.parametrize("inside_repo", [False, True])
def test_report_parent_link_cannot_redirect_within_or_outside_repo(
    tmp_path: Path, slot: str, inside_repo: bool,
) -> None:
    repo = tmp_path / "repo"
    case = write_passing_eval_case(repo)
    options = _report_options()
    target = repo / "docs" if inside_repo else tmp_path / "outside"
    target.mkdir()
    protected = target / "payload.json"
    protected.write_bytes(b"preserve redirected content\n")
    (repo / "artifacts").mkdir()
    link = repo / "artifacts" / "redirect"
    create_directory_link(link, target)
    options[slot] = "artifacts/redirect/payload.json"
    try:
        with pytest.raises(SystemExit) as error:
            run_eval.main(["--repo-root", str(repo), "--case", str(case), *_report_flags(options)])
        assert error.value.code == 2
        assert protected.read_bytes() == b"preserve redirected content\n"
        assert all(
            not (repo / relative).exists()
            for option, relative in options.items() if option != slot
        )
    finally:
        remove_directory_link(link)


def test_artifacts_root_link_is_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    case = write_passing_eval_case(repo)
    target = repo / "docs"
    target.mkdir()
    protected = target / "legacy.json"
    protected.write_bytes(b"preserve root-link target\n")
    link = repo / "artifacts"
    create_directory_link(link, target)
    try:
        with pytest.raises(SystemExit) as error:
            run_eval.main([
                "--repo-root", str(repo), "--case", str(case),
                "--report", "artifacts/legacy.json",
            ])
        assert error.value.code == 2
        assert protected.read_bytes() == b"preserve root-link target\n"
        assert sorted(path.name for path in target.iterdir()) == ["legacy.json"]
    finally:
        remove_directory_link(link)


def test_all_report_paths_are_rechecked_after_eval_before_first_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    case = write_passing_eval_case(repo)
    options = _report_options()
    (repo / "artifacts").mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"preserve late-linked target\n")
    legacy = repo / options["--report"]
    legacy.write_bytes(b"preserve previous legacy\n")
    called = []

    def evaluate_then_link(*_args):
        called.append(True)
        os.link(outside, repo / options["--cases-report"])
        return run_eval.EvalSummary(True, [run_eval.EvalResult("synthetic", True, ["ok"])])

    monkeypatch.setattr(run_eval, "run_all", evaluate_then_link)
    with pytest.raises(ValueError):
        run_eval.main(["--repo-root", str(repo), "--case", str(case), *_report_flags(options)])

    assert called == [True]
    assert outside.read_bytes() == b"preserve late-linked target\n"
    assert legacy.read_bytes() == b"preserve previous legacy\n"
    assert not (repo / options["--summary-report"]).exists()
    assert not list((repo / "artifacts").glob(".*.codex-*.tmp"))


def test_report_writer_rejects_link_added_after_path_validation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "artifacts").mkdir(parents=True)
    destination = run_eval.resolve_report_path(repo, "artifacts/report.json")
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"preserve write-time target\n")
    os.link(outside, destination)

    with pytest.raises(ValueError):
        run_eval.write_report_text(repo, destination, "replacement\n")

    assert outside.read_bytes() == b"preserve write-time target\n"
    assert destination.read_bytes() == outside.read_bytes()


@pytest.mark.parametrize("passing", [False, True])
def test_regular_report_replacements_preserve_legacy_and_split_contracts(
    tmp_path: Path, passing: bool,
) -> None:
    case = write_passing_eval_case(tmp_path)
    if not passing:
        write(tmp_path / "AGENTS.md", "missing required phrase\n")
    options = _report_options()
    for relative in options.values():
        write(tmp_path / relative, "old report\n")

    exit_code = run_eval.main([
        "--repo-root", str(tmp_path), "--case", str(case), *_report_flags(options)
    ])

    legacy = json.loads((tmp_path / options["--report"]).read_text(encoding="utf-8"))
    summary = json.loads((tmp_path / options["--summary-report"]).read_text(encoding="utf-8"))
    cases_bytes = (tmp_path / options["--cases-report"]).read_bytes()
    cases = [json.loads(line) for line in cases_bytes.splitlines()]
    assert exit_code == (0 if passing else 1)
    assert legacy["schema_version"] == summary["schema_version"] == "1"
    assert legacy["passed"] is passing and summary["passed"] is passing
    assert legacy["cases"] == cases
    assert summary["cases_ref"] == options["--cases-report"]
    assert summary["cases_sha256"] == hashlib.sha256(cases_bytes).hexdigest()
    assert all((tmp_path / relative).stat().st_nlink == 1 for relative in options.values())
    assert not list((tmp_path / "artifacts").glob(".*.codex-*.tmp"))


_REPORT_COLLISION_CASES = [
    pytest.param("--summary-report", "--cases-report", False, id="split-only"),
    pytest.param("--summary-report", "--cases-report", True, id="split-with-legacy"),
    pytest.param("--report", "--summary-report", True, id="legacy-summary"),
    pytest.param("--report", "--cases-report", True, id="legacy-cases"),
]


def _report_file_snapshot(repo: Path) -> dict[str, bytes]:
    return {
        path.relative_to(repo).as_posix(): path.read_bytes()
        for path in repo.rglob("*") if path.is_file()
    }


def _report_collision_fixture(
    tmp_path: Path, left_slot: str, right_slot: str, with_legacy: bool,
    *, alias_spelling: bool = True, destination_exists: bool = True,
) -> tuple[Path, Path, dict[str, str], Path, Path]:
    repo = tmp_path.resolve() / "r"
    case = write_passing_eval_case(repo)
    options = _report_options()
    for relative in options.values():
        write(repo / relative, f"preserve companion {relative}\n")
    if not with_legacy:
        options.pop("--report")
    canonical = repo / "artifacts/canonical/result.json"
    alias = repo / "artifacts/alias/result.json"
    for path in (canonical, alias):
        path.parent.mkdir(parents=True, exist_ok=True)
        if destination_exists:
            path.write_bytes(f"preserve {path.parent.name}\n".encode("ascii"))
    options[left_slot] = canonical.relative_to(repo).as_posix()
    options[right_slot] = (alias if alias_spelling else canonical).relative_to(repo).as_posix()
    return repo, case, options, canonical, alias


def _report_collision_message(left_slot: str) -> str:
    if left_slot == "--summary-report":
        return "--summary-report and --cases-report must name different files"
    return "--report, --summary-report, and --cases-report must name distinct files"


@pytest.mark.parametrize(("left_slot", "right_slot", "with_legacy"), _REPORT_COLLISION_CASES)
@pytest.mark.parametrize("alias_spelling", [False, True], ids=["same-spelling", "simulated-alias"])
@pytest.mark.parametrize("destination_exists", [False, True], ids=["new-leaf", "existing-leaf"])
def test_report_destination_collision_cli_fails_before_eval_or_write(
    tmp_path: Path, left_slot: str, right_slot: str, with_legacy: bool,
    alias_spelling: bool, destination_exists: bool,
) -> None:
    repo, case, options, _, _ = _report_collision_fixture(
        tmp_path, left_slot, right_slot, with_legacy,
        alias_spelling=alias_spelling, destination_exists=destination_exists,
    )
    before = _report_file_snapshot(repo)
    # Simulate only one Path.resolve() OS result. These fixture directories
    # are physically separate; this is NOT a native Windows 8.3 reproduction.
    # The real CLI/parser and link checks run in a native child process.
    driver = (
        "import sys\n"
        "from pathlib import Path\n"
        "from unittest.mock import patch\n"
        "from scripts import run_eval\n"
        "root = Path(sys.argv[1])\n"
        "alias = root / 'artifacts/alias/result.json'\n"
        "canonical = root / 'artifacts/canonical/result.json'\n"
        "original_resolve = Path.resolve\n"
        "def resolve_alias(path, *args, **kwargs):\n"
        "    return original_resolve(canonical if path == alias else path, *args, **kwargs)\n"
        "def record_eval(*args, **kwargs):\n"
        "    (root / 'eval-called.txt').write_text('called', encoding='utf-8')\n"
        "    raise AssertionError('report collision reached eval')\n"
        "with patch.object(Path, 'resolve', resolve_alias), patch.object(run_eval, 'run_all', record_eval):\n"
        "    raise SystemExit(run_eval.main(sys.argv[2:]))\n"
    )
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            sys.executable, "-B", "-c", driver, str(repo),
            "--repo-root", str(repo), "--case", str(case), *_report_flags(options),
        ],
        cwd=run_eval.REPO_ROOT, env=environment, capture_output=True,
        text=True, check=False, timeout=30,
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert _report_collision_message(left_slot) in completed.stderr
    assert "Traceback" not in completed.stderr
    assert completed.stdout == ""
    assert not (repo / "eval-called.txt").exists()
    assert _report_file_snapshot(repo) == before


@pytest.mark.parametrize(("left_slot", "right_slot", "with_legacy"), _REPORT_COLLISION_CASES)
def test_report_alias_collision_after_eval_stops_before_first_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys,
    left_slot: str, right_slot: str, with_legacy: bool,
) -> None:
    repo, case, options, canonical, alias = _report_collision_fixture(
        tmp_path, left_slot, right_slot, with_legacy
    )
    before = _report_file_snapshot(repo)
    aliases: dict[Path, Path] = {}
    original_resolve = Path.resolve
    original_run_all = run_eval.run_all
    eval_calls = []

    def resolve_alias(path, *args, **kwargs):
        return original_resolve(aliases.get(path, path), *args, **kwargs)

    def evaluate_then_alias(*args, **kwargs):
        summary = original_run_all(*args, **kwargs)
        eval_calls.append(summary.passed)
        # Inject a changed OS resolution only after the real synthetic eval.
        aliases[alias] = canonical
        return summary

    monkeypatch.setattr(Path, "resolve", resolve_alias)
    monkeypatch.setattr(run_eval, "run_all", evaluate_then_alias)
    with pytest.raises(ValueError) as error:
        run_eval.main([
            "--repo-root", str(repo), "--case", str(case), *_report_flags(options)
        ])

    assert str(error.value) == _report_collision_message(left_slot)
    assert eval_calls == [True]
    assert capsys.readouterr().out == ""
    assert _report_file_snapshot(repo) == before


@pytest.mark.parametrize("slot", ["--report", "--summary-report", "--cases-report"])
def test_distinct_resolved_report_keys_keep_lexical_safety_and_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, slot: str,
) -> None:
    repo = tmp_path.resolve() / "r"
    case = write_passing_eval_case(repo)
    options = _report_options()
    alias = repo / "artifacts/alias/result.json"
    canonical = repo / "artifacts/canonical/result.json"
    write(alias, "replace lexical file\n")
    write(canonical, "preserve canonical sentinel\n")
    canonical_before = canonical.read_bytes()
    options[slot] = alias.relative_to(repo).as_posix()
    original_resolve = Path.resolve
    original_boundary = run_eval._validate_destination_boundary
    original_writer = run_eval._write_destination_text
    checked_paths = []
    written_paths = []

    def resolve_alias(path, *args, **kwargs):
        return original_resolve(canonical if path == alias else path, *args, **kwargs)

    def record_boundary(destination, **kwargs):
        checked_paths.append(destination)
        return original_boundary(destination, **kwargs)

    def record_writer(destination, text, **kwargs):
        written_paths.append(destination)
        return original_writer(destination, text, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve_alias)
    monkeypatch.setattr(run_eval, "_validate_destination_boundary", record_boundary)
    monkeypatch.setattr(run_eval, "_write_destination_text", record_writer)
    exit_code = run_eval.main([
        "--repo-root", str(repo), "--case", str(case), *_report_flags(options)
    ])

    assert exit_code == 0
    assert alias in checked_paths and canonical not in checked_paths
    assert written_paths == [
        repo / options[option]
        for option in ("--report", "--cases-report", "--summary-report")
    ]
    # With our resolve-only simulation these remain separate real files.
    # Their bytes prove that the writer received lexical, not resolved, paths.
    assert canonical.read_bytes() == canonical_before
    legacy = json.loads((repo / options["--report"]).read_text(encoding="utf-8"))
    summary = json.loads((repo / options["--summary-report"]).read_text(encoding="utf-8"))
    cases_bytes = (repo / options["--cases-report"]).read_bytes()
    assert legacy["cases"] == [json.loads(line) for line in cases_bytes.splitlines()]
    assert summary["cases_ref"] == options["--cases-report"]
    assert summary["cases_sha256"] == hashlib.sha256(cases_bytes).hexdigest()
    assert all(path.stat().st_nlink == 1 for path in written_paths)
    assert not list((repo / "artifacts").rglob(".*.codex-*.tmp"))


def test_rendered_readiness_honors_explicit_coverage_result_filter(tmp_path: Path) -> None:
    rendered_readiness_repo(tmp_path)
    case = rendered_readiness_case()
    case["renders"][0]["allowed_results"] = ["RECOGNIZED_EVIDENCE_COMPLETE"]
    result = run_eval.run_rendered_readiness(tmp_path, case)
    assert result.passed is False
    assert any("not in allowed results" in finding for finding in result.messages)
