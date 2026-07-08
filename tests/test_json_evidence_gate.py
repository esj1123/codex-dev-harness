import json
from pathlib import Path

from scripts import quality_gate
from scripts.gates import json_evidence_gate


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def policy_text() -> str:
    return "\n".join(
        [
            "# JSON Evidence Policy",
            "Phase 4B JSON Evidence Core",
            "Evidence Serialization Policy",
            "repo-relative paths",
            "safe summaries",
            "hashes",
            "no audit automation",
            "no real audit logs",
            "no raw prompts",
            "no private data",
            "no raw command logs",
            "no unredacted tool-call bodies",
            "no local absolute paths",
        ]
    )


def schema(required_fields: list[str], evidence_kind: str) -> dict:
    properties = {field: {"type": "string"} for field in required_fields}
    properties["evidence_kind"] = {"type": "string", "const": evidence_kind}
    properties["status_label"] = {"$ref": "#/$defs/status_label"}
    if "payload_capture" in required_fields:
        properties["payload_capture"] = {"type": "string", "enum": ["none", "redacted_summary_only"]}
    if evidence_kind == "receipt_summary":
        properties["eval_evidence"] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "eval_command",
                "eval_scope",
                "eval_report_generation_status",
                "eval_integration_status",
                "eval_gate_status",
                "release_blocking_status",
            ],
            "properties": {
                "eval_command": {"type": "string"},
                "eval_scope": {"type": "string"},
                "eval_case_count": {"type": "integer"},
                "eval_pass_count": {"type": "integer"},
                "eval_fail_count": {"type": "integer"},
                "summary_report_path": {"$ref": "#/$defs/repo_relative_path"},
                "summary_report_sha256": {"$ref": "#/$defs/sha256_value"},
                "cases_ref": {"$ref": "#/$defs/repo_relative_path"},
                "cases_sha256": {"$ref": "#/$defs/sha256_value"},
                "eval_report_generation_status": {"type": "string"},
                "eval_integration_status": {"type": "string"},
                "eval_gate_status": {"type": "string"},
                "release_blocking_status": {"type": "string"},
                "notes_or_failures_summary": {"type": "string"},
            },
        }
        properties["hermes_git_push_preflight_evidence"] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "preflight_evidence_status",
                "preflight_output_mode",
                "caller_schema_version",
                "caller_mode",
                "decision",
                "side_effect_requested",
                "guarded_command",
                "would_run_git_push",
                "performed_actions_empty",
                "reason_code",
                "stop_reasons",
                "approval_ref_present",
                "evidence_refs",
                "output_capture",
                "preflight_integration_status",
            ],
            "properties": {
                "preflight_evidence_status": {"type": "string"},
                "preflight_output_mode": {"type": "string"},
                "caller_schema_version": {"type": "string"},
                "caller_mode": {"type": "string"},
                "decision": {"type": "string"},
                "side_effect_requested": {"type": "string"},
                "guarded_command": {"type": "string"},
                "would_run_git_push": {"type": "boolean"},
                "performed_actions_empty": {"type": "boolean"},
                "reason_code": {"type": "string"},
                "stop_reasons": {"type": "array", "items": {"type": "string"}},
                "approval_ref_present": {"type": "boolean"},
                "evidence_refs": {"type": "array", "items": {"$ref": "#/$defs/repo_relative_path"}},
                "hermes_result_summary": {"type": "string"},
                "safe_task_summary": {"type": "string"},
                "safety_notes": {"type": "array", "items": {"type": "string"}},
                "observed_head_commit": {"$ref": "#/$defs/commit_or_unknown"},
                "local_verify_run_id": {"type": "string"},
                "local_verify_job_id": {"type": "string"},
                "output_capture": {"type": "string"},
                "preflight_integration_status": {"type": "string"},
            },
        }
    if evidence_kind == "trace_event":
        properties["hermes_git_push_preflight_evidence_ref"] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "preflight_evidence_status",
                "decision",
                "reason_code",
                "side_effect_requested",
                "receipt_evidence_key",
                "summary",
            ],
            "properties": {
                "preflight_evidence_status": {"type": "string"},
                "decision": {"type": "string"},
                "reason_code": {"type": "string"},
                "side_effect_requested": {"type": "string"},
                "receipt_evidence_key": {"type": "string", "const": "hermes_git_push_preflight_evidence"},
                "observed_head_commit": {"$ref": "#/$defs/commit_or_unknown"},
                "summary": {"type": "string"},
            },
        }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://example.invalid/{evidence_kind}.schema.json",
        "type": "object",
        "additionalProperties": False,
        "required": required_fields,
        "properties": properties,
        "$defs": {
            "status_label": {
                "type": "string",
                "enum": [
                    "PASS",
                    "PASS WITH NOTES",
                    "BLOCKED",
                    "NOT RUN",
                    "ENVIRONMENT BLOCKED",
                    "FAIL",
                ],
            },
            "redaction_status": {
                "type": "object",
                "required": ["status", "notes"],
                "properties": {"status": {"type": "string"}, "notes": {"type": "string"}},
            },
            "repo_relative_path": {
                "type": "string",
                "pattern": "^(?![A-Za-z]:)(?!/)",
            },
            "sha256_value": {
                "type": "string",
                "pattern": "^[0-9a-fA-F]{64}$",
            },
            "commit_or_unknown": {
                "type": "string",
                "pattern": "^([0-9a-fA-F]{7,40}|unknown|not checked|not applicable)$",
            },
        },
    }


def receipt_required_fields() -> list[str]:
    return [
        "schema_version",
        "evidence_kind",
        "receipt_id",
        "task_id",
        "repository",
        "basis",
        "approval",
        "side_effect_class",
        "changed_files",
        "commands",
        "verification",
        "safety",
        "artifacts",
        "status_label",
        "unresolved_risks",
        "next_step",
    ]


def trace_required_fields() -> list[str]:
    return [
        "schema_version",
        "evidence_kind",
        "event_id",
        "task_id",
        "sequence",
        "event_type",
        "event_summary",
        "status_label",
        "redaction_status",
        "payload_capture",
    ]


def write_valid_bundle(root: Path) -> None:
    write(root / "docs" / "JSON_EVIDENCE_POLICY.md", policy_text())
    write(
        root / "audits" / "receipt-summary.schema.json",
        json.dumps(schema(receipt_required_fields(), "receipt_summary")),
    )
    write(
        root / "audits" / "trace-event.schema.json",
        json.dumps(schema(trace_required_fields(), "trace_event")),
    )


def test_json_evidence_gate_is_not_applicable_without_marker_or_bundle(tmp_path: Path) -> None:
    result = json_evidence_gate.run(tmp_path)

    assert result.passed is True
    assert "not applicable" in result.messages[0]


def test_json_evidence_gate_fails_when_phase_marker_has_no_bundle(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "CAPABILITY_IMPLEMENTATION_ROADMAP.md", "Phase 4B JSON Evidence Core\n")

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("Phase 4B marker present" in message for message in result.messages)
    assert any("docs/JSON_EVIDENCE_POLICY.md" in message for message in result.messages)


def test_json_evidence_gate_fails_partial_bundle_without_marker(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "JSON_EVIDENCE_POLICY.md", policy_text())

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("incomplete JSON evidence bundle" in message for message in result.messages)


def test_json_evidence_gate_validates_full_bundle_with_status_marker(tmp_path: Path) -> None:
    write(tmp_path / "STATUS.md", "JSON Evidence Core is present\n")
    write_valid_bundle(tmp_path)

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is True
    assert "validated" in result.messages[0]


def test_json_evidence_gate_reports_invalid_json(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "CAPABILITY_IMPLEMENTATION_ROADMAP.md", "Phase 4B\n")
    write_valid_bundle(tmp_path)
    write(tmp_path / "audits" / "trace-event.schema.json", "{not-json")

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("invalid JSON" in message for message in result.messages)


def test_json_evidence_gate_reports_missing_receipt_id_required_schema_field(tmp_path: Path) -> None:
    write_valid_bundle(tmp_path)
    bad_schema = schema(receipt_required_fields(), "receipt_summary")
    bad_schema["required"].remove("receipt_id")
    write(tmp_path / "audits" / "receipt-summary.schema.json", json.dumps(bad_schema))

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("missing required field: receipt_id" in message for message in result.messages)


def test_json_evidence_gate_reports_required_eval_evidence_schema_field(tmp_path: Path) -> None:
    write_valid_bundle(tmp_path)
    bad_schema = schema(receipt_required_fields(), "receipt_summary")
    bad_schema["required"].append("eval_evidence")
    write(tmp_path / "audits" / "receipt-summary.schema.json", json.dumps(bad_schema))

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("eval_evidence must be optional" in message for message in result.messages)


def test_json_evidence_gate_reports_missing_eval_evidence_reference_shape(tmp_path: Path) -> None:
    write_valid_bundle(tmp_path)
    bad_schema = schema(receipt_required_fields(), "receipt_summary")
    del bad_schema["properties"]["eval_evidence"]["properties"]["cases_sha256"]
    write(tmp_path / "audits" / "receipt-summary.schema.json", json.dumps(bad_schema))

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("eval_evidence missing property: cases_sha256" in message for message in result.messages)


def test_json_evidence_gate_reports_missing_hermes_preflight_receipt_shape(tmp_path: Path) -> None:
    write_valid_bundle(tmp_path)
    bad_schema = schema(receipt_required_fields(), "receipt_summary")
    del bad_schema["properties"]["hermes_git_push_preflight_evidence"]["properties"]["evidence_refs"]
    write(tmp_path / "audits" / "receipt-summary.schema.json", json.dumps(bad_schema))

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("hermes_git_push_preflight_evidence missing property: evidence_refs" in message for message in result.messages)


def test_json_evidence_gate_reports_missing_hermes_preflight_trace_ref_shape(tmp_path: Path) -> None:
    write_valid_bundle(tmp_path)
    bad_schema = schema(trace_required_fields(), "trace_event")
    del bad_schema["properties"]["hermes_git_push_preflight_evidence_ref"]["properties"]["receipt_evidence_key"]
    write(tmp_path / "audits" / "trace-event.schema.json", json.dumps(bad_schema))

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any(
        "hermes_git_push_preflight_evidence_ref missing property: receipt_evidence_key" in message
        for message in result.messages
    )


def test_json_evidence_gate_reports_missing_policy_boundary(tmp_path: Path) -> None:
    write_valid_bundle(tmp_path)
    write(tmp_path / "docs" / "JSON_EVIDENCE_POLICY.md", "Phase 4B JSON Evidence Core\n")

    result = json_evidence_gate.run(tmp_path)

    assert result.passed is False
    assert any("no raw prompts" in message for message in result.messages)


def test_quality_gate_runs_json_evidence_gate(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def passing_gate(name: str):
        def run(repo_root: Path) -> json_evidence_gate.GateResult:
            calls.append(name)
            return json_evidence_gate.GateResult(name, True, ["ok"])

        return run

    monkeypatch.setattr(quality_gate.docs_gate, "run", passing_gate("docs_gate"))
    monkeypatch.setattr(quality_gate.repo_hygiene_gate, "run", passing_gate("repo_hygiene_gate"))
    monkeypatch.setattr(quality_gate.template_schema_gate, "run", passing_gate("template_schema_gate"))
    monkeypatch.setattr(quality_gate.example_gate, "run", passing_gate("example_gate"))
    monkeypatch.setattr(quality_gate.example_render_drift_gate, "run", passing_gate("example_render_drift_gate"))
    monkeypatch.setattr(
        quality_gate.rendered_golden_content_gate,
        "run",
        passing_gate("rendered_golden_content_gate"),
    )
    monkeypatch.setattr(quality_gate.secret_scan_gate, "run", passing_gate("secret_scan_gate"))
    monkeypatch.setattr(quality_gate.json_evidence_gate, "run", passing_gate("json_evidence_gate"))

    summary = quality_gate.run_quality_gate(tmp_path)

    assert summary.passed is True
    assert calls[-1] == "json_evidence_gate"
