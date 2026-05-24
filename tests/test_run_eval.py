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
