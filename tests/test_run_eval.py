import json
from pathlib import Path

from scripts import run_eval


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_repo(root: Path) -> None:
    write(root / "templates/base/README.md.template", "# demo\n")
    write(root / "templates/base/STATUS.md.template", "status\n")
    write(root / "profiles/python_cli/README.profile.md.template", "profile\n")
    write(
        root / "examples/demo/template.config.yml",
        "project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n",
    )
    write(root / "examples/demo/README.md", "# demo\n")
    write(root / "examples/demo/STATUS.md", "status\n")
    write(root / "examples/demo/README.profile.md", "profile\n")
    write(
        root / "evals/golden/render_structure_paths.txt",
        "examples/demo/README.md\nexamples/demo/STATUS.md\nexamples/demo/README.profile.md\n",
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
                "expected_files": [
                    "examples/demo/README.md",
                    "examples/demo/STATUS.md",
                    "examples/demo/README.profile.md",
                ],
            }
        ],
    }


def test_render_structure_passes_expected_paths(tmp_path: Path) -> None:
    render_repo(tmp_path)

    result = run_eval.run_render_structure(tmp_path, render_case())

    assert result.passed is True
    assert "3" in result.messages[0]


def test_render_structure_detects_missing_expected_file(tmp_path: Path) -> None:
    render_repo(tmp_path)
    (tmp_path / "examples/demo/STATUS.md").unlink()

    result = run_eval.run_render_structure(tmp_path, render_case())

    assert result.passed is False
    assert any("STATUS.md" in message for message in result.messages)


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
