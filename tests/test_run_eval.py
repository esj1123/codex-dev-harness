import hashlib
import json
from pathlib import Path

from scripts import run_eval


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
                "allowed_results": ["READY_FOR_AI_ASSISTED_WORK"],
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


def test_forbidden_artifacts_ignores_root_local(tmp_path: Path) -> None:
    write(tmp_path / "local/examples/demo/App.csproj", "<Project />\n")
    case = {
        "eval": "forbidden_artifacts",
        "ignored_root_parts": ["local"],
        "forbidden_path_globs": ["examples/**/*.csproj"],
        "forbidden_suffixes": [".csproj"],
        "text_suffixes": [".md", ".yml"],
    }

    result = run_eval.run_forbidden_artifacts(tmp_path, case)

    assert result.passed is True


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
            "builder": {},
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
        "expected_predicate_type": "https://codex-dev-harness.local/provenance/v1",
        "require_local_only": True,
        "required_predicate_fields": ["schema_version", "local_only", "builder", "materials", "products"],
    }

    result = run_eval.run_jsonl_shape(tmp_path, case)

    assert result.passed is True
    assert result.name == "provenance_shape"
