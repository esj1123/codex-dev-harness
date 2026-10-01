from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import task_evidence_summary as summary

SESSION = "11111111-1111-1111-1111-111111111111"
TURN = "22222222-2222-2222-2222-222222222222"
TURN2 = "33333333-3333-3333-3333-333333333333"
SHA = "a" * 40
PRIVATE = "BODY_MUST_NEVER_APPEAR_IN_OUTPUT"
STATES = {"completed": ["PASS", "COMPLETE"], "pending": ["HOLD", "NOT_RUN"], "unknown": ["UNKNOWN"]}


def write_json(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value) + "\n").encode()
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "input"
    root.mkdir()
    artifact_sha = write_json(root / "evidence/artifact.json", {"private": PRIVATE})
    receipt_sha = write_json(root / "evidence/receipt.json", {"sha": artifact_sha, "private": PRIVATE})
    state = {"current": {"sha": SHA, "gates": {"build": "PASS"}, "evidence": [
        {"path": "artifact.json", "sha256": artifact_sha},
        {"path": "receipt.json", "sha256": receipt_sha}]}, "old": {"build": "NOT_RUN"}, "private": PRIVATE}
    spec = {"schema_version": "1", "state": {"path": "state.json", "sha256": write_json(root / "state.json", state),
        "pointer": ["current"]}, "evidence": {"root": "evidence", "pointer": ["evidence"]},
        "identities": [{"id": "target", "pointer": ["sha"], "expected": SHA}],
        "candidate": {"path": "evidence/artifact.json", "sha256": artifact_sha},
        "links": [{"receipt": "evidence/receipt.json", "pointer": ["sha"], "target": "evidence/artifact.json"}],
        "gates": [{"id": "build", "pointer": ["gates", "build"], "states": copy.deepcopy(STATES),
                   "proofs": ["evidence/receipt.json", "evidence/artifact.json"]}],
        "history": [{"id": "initial", "path": "state.json", "pointer": ["old", "build"],
                     "states": copy.deepcopy(STATES), "gate": "build"}], "runtime": []}
    return root, spec


def inspect(root: Path, spec: dict, *, runtime_root: Path | None = None) -> dict:
    write_json(root / "spec.json", spec)
    result = summary.inspect_summary("spec.json", spec_root=root, input_root=root, runtime_root=runtime_root)
    assert PRIVATE not in json.dumps(result)
    assert str(root) not in json.dumps(result)
    return result


def change_state(root: Path, spec: dict, fn) -> None:
    state = json.loads((root / "state.json").read_bytes())
    fn(state)
    spec["state"]["sha256"] = write_json(root / "state.json", state)


def test_bound_candidate_and_current_scope_are_complete(fixture) -> None:
    root, spec = fixture
    result = inspect(root, spec)
    assert result["status"] == "PASS"
    assert result["state"]["completion"] is True
    assert result["state"]["counts"] == {"completed": 1, "pending": 0, "unknown": 0}
    assert result["state"]["superseded_claims"] == [{"id": "initial", "gate": "build",
        "previous": "PENDING", "current": "COMPLETED", "code": "SUPERSEDED_CLAIM"}]
    assert result["authorization_status"] == "NOT_AUTHENTICATED"
    assert result["performed_actions"] == [] and result["savings"] == "NOT_MEASURED"


def test_old_pass_never_overrides_current_hold(fixture) -> None:
    root, spec = fixture
    change_state(root, spec, lambda d: (d["current"]["gates"].update(build="HOLD"), d["old"].update(build="PASS")))
    result = inspect(root, spec)["state"]
    assert result["completion"] is False
    assert result["counts"] == {"completed": 0, "pending": 1, "unknown": 0}
    assert result["superseded_claims"][0]["previous"] == "COMPLETED"


def test_no_candidate_or_unbound_candidate_never_completes(fixture) -> None:
    root, spec = fixture
    spec["candidate"] = {"path": "absent.json", "sha256": None}
    result = inspect(root, spec)["state"]
    assert result["candidate_binding"] == "MISSING" and result["completion"] is False
    spec["candidate"]["path"] = "evidence/artifact.json"
    result = inspect(root, spec)["state"]
    assert result["candidate_binding"] == "UNKNOWN" and result["completion"] is False


def test_state_only_summary_never_accesses_runtime(fixture, monkeypatch) -> None:
    root, spec = fixture
    runtime_root = root / "runtime-must-not-be-read"
    original_root = summary.paths._physical_package_root
    def physical_root(path):
        assert path != runtime_root
        return original_root(path)
    monkeypatch.setattr(summary.paths, "_physical_package_root", physical_root)
    monkeypatch.setattr(summary, "inspect_runtime", lambda *a: pytest.fail("unexpected runtime access"))
    result = inspect(root, spec, runtime_root=runtime_root)
    assert spec["runtime"] == []
    assert result["status"] == "PASS" and result["state"]["completion"] is True
    assert result["usage"] == [] and result["usage_totals"] is None
    assert result["savings"] == "NOT_MEASURED"


@pytest.mark.parametrize(("candidate", "gates", "mismatch", "next_action"), [
    ("bound", ["PASS"], False, "TARGET_OWNER_REVIEW_COMPLETION"),
    ("bound", ["HOLD"], False, "TARGET_OWNER_COMPLETE_PENDING_GATES"),
    ("bound", ["UNKNOWN"], False, "TARGET_OWNER_RESOLVE_UNKNOWN_GATES"),
    ("bound", ["HOLD", "UNKNOWN"], False, "TARGET_OWNER_COMPLETE_PENDING_GATES"),
    ("missing", ["HOLD", "UNKNOWN"], False, "TARGET_OWNER_SUPPLY_CANDIDATE"),
    ("unbound", ["HOLD"], False, "TARGET_OWNER_BIND_CANDIDATE"),
    ("unbound", ["UNKNOWN"], False, "TARGET_OWNER_BIND_CANDIDATE"),
    ("bound", ["HOLD", "UNKNOWN"], True, "RESOLVE_EVIDENCE_MISMATCHES"),
    ("unbound", ["HOLD"], True, "RESOLVE_EVIDENCE_MISMATCHES"),
    ("missing_bound", ["UNKNOWN"], False, "RESOLVE_EVIDENCE_MISMATCHES"),
    ("wrong_sha", ["HOLD"], False, "RESOLVE_EVIDENCE_MISMATCHES"),
])
def test_next_action_prioritizes_binding_and_retains_all_gates(
    fixture, candidate, gates, mismatch, next_action,
) -> None:
    root, spec = fixture
    current_gates = {"build": gates[0]}
    if len(gates) > 1:
        current_gates["review"] = gates[1]
        gate = copy.deepcopy(spec["gates"][0])
        gate.update(id="review", pointer=["gates", "review"])
        spec["gates"].append(gate)
    change_state(root, spec, lambda d: d["current"].update(gates=current_gates))
    if candidate in {"missing", "missing_bound"}:
        spec["candidate"]["path"] = "absent.json"
    if candidate in {"missing", "unbound"}:
        spec["candidate"]["sha256"] = None
    if candidate == "wrong_sha":
        spec["candidate"]["sha256"] = "b" * 64
    if mismatch:
        spec["identities"][0]["expected"] = "b" * 40
    result = inspect(root, spec)
    state = result["state"]
    failed = mismatch or candidate in {"missing_bound", "wrong_sha"}
    assert result["status"] == ("FAIL" if failed else "PASS")
    assert state["next_action"] == next_action
    assert state["completion"] is (next_action == "TARGET_OWNER_REVIEW_COMPLETION")
    assert set(state["gates"]) == set(current_gates)
    assert sum(state["counts"].values()) == len(gates)
    for key, value in current_gates.items():
        if value in {"HOLD", "UNKNOWN"}:
            assert state["gates"][key] != "COMPLETED"
    assert result["authorization_status"] == "NOT_AUTHENTICATED"
    assert result["performed_actions"] == []


@pytest.mark.parametrize("distribution", ["pending", "unknown", "mixed"])
def test_text_summary_caps_gate_ids_at_maximum_input(fixture, distribution) -> None:
    root, spec = fixture
    states = {}
    spec["gates"] = []
    spec["history"] = []
    for index in reversed(range(32)):
        name = "unknown" if distribution == "unknown" or distribution == "mixed" and index % 2 else "pending"
        key = (f"{name}_{index:02d}_" + "x" * 64)[:64]
        states[key] = "UNKNOWN" if name == "unknown" else "HOLD"
        spec["gates"].append({"id": key, "pointer": ["gates", key],
                             "states": copy.deepcopy(STATES), "proofs": ["evidence/receipt.json"]})
    change_state(root, spec, lambda d: d["current"].update(gates=states))
    result = inspect(root, spec)
    text = summary.text_summary(result)
    assert len(text.encode()) < 2048
    assert len(text.splitlines()) == 1
    assert "candidate_binding=BOUND completion=False" in text
    assert PRIVATE not in text and str(root) not in text
    assert "usage" not in text and "tokens" not in text
    for name, value in (("pending", "HOLD"), ("unknown", "UNKNOWN")):
        keys = sorted(key for key, state in states.items() if state == value)
        shown = ",".join(keys[:summary.MAX_TEXT_GATE_IDS]) or "NONE"
        assert f"{name}={shown} " in text
        assert f"{name}_omitted={max(0, len(keys) - summary.MAX_TEXT_GATE_IDS)}" in text
        assert all(key not in text for key in keys[summary.MAX_TEXT_GATE_IDS:])
    assert result["state"]["counts"]["completed"] == 0
    assert sum(result["state"]["counts"].values()) == 32


def test_text_summary_retains_fail_closed_size_envelope(fixture, monkeypatch) -> None:
    root, spec = fixture
    result = inspect(root, spec)
    monkeypatch.setattr(summary, "MAX_OUTPUT", 256)
    emitted = json.loads(summary.output_bytes(result))
    assert emitted["status"] == "FAIL" and emitted["reason_codes"] == ["OUTPUT_TOO_LARGE"]
    text = summary.text_summary(result)
    assert "status=FAIL candidate_binding=UNKNOWN completion=False" in text
    assert "next_action=RESOLVE_INPUT_INSPECTION_FAILURE" in text
    assert "reasons=OUTPUT_TOO_LARGE" in text
    assert PRIVATE not in text and str(root) not in text


@pytest.mark.parametrize("field", ["state", "candidate", "identity", "evidence", "link"])
def test_changed_or_inconsistent_shas_fail(fixture, field) -> None:
    root, spec = fixture
    if field == "state": spec["state"]["sha256"] = "b" * 64
    if field == "candidate": spec["candidate"]["sha256"] = "b" * 64
    if field == "identity": spec["identities"][0]["expected"] = "b" * 40
    if field == "evidence": (root / "evidence/artifact.json").write_bytes(b'"changed"')
    if field == "link":
        r = {"sha": "b" * 64, "private": PRIVATE}
        sha = write_json(root / "evidence/receipt.json", r)
        change_state(root, spec, lambda d: d["current"]["evidence"][1].update(sha256=sha))
    result = inspect(root, spec)
    assert result["status"] == "FAIL"
    assert not result.get("state", {}).get("completion", False)


def test_uppercase_sha_and_unknown_status_are_safe(fixture) -> None:
    root, spec = fixture
    spec["state"]["sha256"] = spec["state"]["sha256"].upper()
    spec["identities"][0]["expected"] = SHA.upper()
    assert inspect(root, spec)["status"] == "PASS"
    change_state(root, spec, lambda d: d["current"]["gates"].update(build=PRIVATE))
    result = inspect(root, spec)["state"]
    assert result["gates"]["build"] == "UNKNOWN" and result["completion"] is False


@pytest.mark.parametrize("mutate", [
    lambda s: s["state"].update(path="../outside.json"),
    lambda s: s["state"].update(path="https://outside.invalid/state.json"),
    lambda s: s["links"][0].update(target="../outside.json"),
    lambda s: s["gates"][0]["states"]["pending"].append("PASS"),
    lambda s: s["gates"][0].update(proofs=[]),
])
def test_invalid_boundaries_and_absent_proof_do_not_complete(fixture, mutate) -> None:
    root, spec = fixture
    mutate(spec)
    result = inspect(root, spec)
    assert not result.get("state", {}).get("completion", False)


def test_truncated_json_and_duplicate_key_do_not_reflect_payload(fixture) -> None:
    root, spec = fixture
    for data in [b'{"private":"'+PRIVATE.encode(), b'{"current":1,"current":2}']:
        (root / "state.json").write_bytes(data)
        spec["state"]["sha256"] = hashlib.sha256(data).hexdigest()
        assert inspect(root, spec)["status"] == "FAIL"


def test_hardlink_input_is_rejected(fixture) -> None:
    root, spec = fixture
    os.link(root / "state.json", root / "second.json")
    assert inspect(root, spec)["reason_codes"] == ["INPUT_MULTIPLE_LINKS"]


def test_native_utf8_bom_preserves_raw_hash(fixture) -> None:
    root, spec = fixture
    data = b"\xef\xbb\xbf" + (root / "state.json").read_bytes()
    (root / "state.json").write_bytes(data)
    spec["state"]["sha256"] = hashlib.sha256(data).hexdigest()
    result = inspect(root, spec)
    assert result["status"] == "PASS"
    assert result["state"]["input_sha256"] == hashlib.sha256(data).hexdigest()


def test_reparse_ancestor_is_rejected_without_following_it(fixture, monkeypatch) -> None:
    root, spec = fixture
    original = summary.paths._is_unsafe_link
    def unsafe(info):
        return stat_is_dir(info) or original(info)
    def stat_is_dir(info):
        import stat
        return stat.S_ISDIR(info.st_mode)
    monkeypatch.setattr(summary.paths, "_is_unsafe_link", unsafe)
    assert inspect(root, spec)["status"] == "FAIL"


def event(kind: str, payload: dict, second: int) -> dict:
    return {"type": kind, "timestamp": f"2026-01-01T00:00:{second:02d}Z", "payload": payload}


def usage(i: int, c: int, o: int, r: int = 0) -> dict:
    return dict(zip(summary.TOKEN_KEYS, (i, c, o, r, i + o)))


def count(total: dict, last: dict, second: int) -> dict:
    return event("event_msg", {"type": "token_count", "info": {
        "total_token_usage": total, "last_token_usage": last}, "private": PRIVATE}, second)


def runtime(root: Path, spec: dict, events: list[dict], *, tail: bytes = b"", turns=None) -> dict:
    rows = [event("session_meta", {"id": SESSION}, 0),
            event("turn_context", {"turn_id": TURN, "model": "gpt-6.1-sol", "effort": "xhigh"}, 1), *events]
    (root / "run.jsonl").write_bytes(b"".join((json.dumps(e)+"\n").encode() for e in rows) + tail)
    spec["runtime"] = [{"id": "parent", "path": "run.jsonl", "session_id": SESSION,
                        "turns": turns or [TURN], "cutoff": "2026-01-01T00:00:59Z"}]
    return inspect(root, spec, runtime_root=root)["usage"][0]


def test_counter_deltas_subsets_duplicates_and_routing_changes(fixture) -> None:
    root, spec = fixture
    a, b, c = usage(100, 80, 10, 3), usage(210, 160, 21, 6), usage(330, 240, 33, 9)
    e1 = count(a, a, 2)
    rows = [e1, copy.deepcopy(e1), count(b, usage(110, 80, 11, 3), 3), copy.deepcopy(e1),
            event("turn_context", {"turn_id": TURN2, "model": "gpt-6-astra", "effort": "low"}, 4),
            count(c, usage(120, 80, 12, 3), 5), count(c, usage(120, 80, 12, 3), 6)]
    result = runtime(root, spec, rows, turns=[TURN, TURN2])
    assert result["tokens"] == usage(330, 240, 33, 9)
    assert result["duplicate_events"] == 2 and result["zero_snapshots"] == 1
    assert sum(g["positive_token_events"] for g in result["groups"]) == 3
    assert result["groups"][1]["model"] == "gpt-6-astra"
    assert result["model_calls"] is None and result["app_turn_duration_ms"] is None
    assert result["coverage"] == "SELECTED_COUNTER_WINDOW"


def test_missing_initial_boundary_reset_and_partial_coverage(fixture) -> None:
    root, spec = fixture
    result = runtime(root, spec, [count(usage(100, 80, 10), usage(10, 8, 1), 2),
        count(usage(110, 88, 11), usage(10, 8, 1), 3),
        count(usage(5, 0, 1), usage(5, 0, 1), 4),
        count(usage(9, 2, 2), usage(4, 2, 1), 5)])
    assert result["tokens"] == usage(14, 10, 2)
    assert result["resets"] == 1 and result["coverage"] == "PARTIAL"
    assert "INITIAL_BOUNDARY_MISSING" in result["reason_codes"]
    assert "COUNTER_RESET_BOUNDARY_MISSING" in result["reason_codes"]


def test_predecessor_outside_selected_turn_includes_first_selected_response(fixture) -> None:
    root, spec = fixture
    result = runtime(root, spec, [count(usage(100, 80, 10), usage(100, 80, 10), 2),
        event("turn_context", {"turn_id": TURN2, "model": "gpt-6.1-sol", "effort": "high"}, 3),
        count(usage(120, 90, 12), usage(20, 10, 2), 4)], turns=[TURN2])
    assert result["tokens"] == usage(20, 10, 2)
    assert result["coverage"] == "SELECTED_COUNTER_WINDOW"


def test_missing_event_truncation_and_invalid_subsets_are_explicit(fixture) -> None:
    root, spec = fixture
    result = runtime(root, spec, [count(usage(100, 80, 10), usage(100, 80, 10), 2),
        count(usage(140, 100, 14), usage(20, 10, 2), 3)], tail=b'{"type":"event_msg","payload":{"type":"token_count","private":"'+PRIVATE.encode())
    assert result["tokens"] == usage(140, 100, 14)
    assert result["coverage"] == "PARTIAL"
    assert "TOKEN_EVENT_GAP_OR_LAST_DISCREPANCY" in result["reason_codes"]
    assert result["invalid_events"] == 1
    result = runtime(root, spec, [count(usage(10, 20, 1), usage(10, 20, 1), 2)])
    assert result["tokens"] == usage(0, 0, 0) and result["coverage"] == "PARTIAL"


def test_duplicate_source_is_not_aggregated(fixture) -> None:
    root, spec = fixture
    runtime(root, spec, [count(usage(1, 0, 1), usage(1, 0, 1), 2)])
    spec["runtime"].append(copy.deepcopy(spec["runtime"][0]))
    assert inspect(root, spec, runtime_root=root)["reason_codes"] == ["RUNTIME_SOURCE_OVERLAP"]


def test_wrong_session_identity_is_rejected(fixture) -> None:
    root, spec = fixture
    runtime(root, spec, [count(usage(1, 0, 1), usage(1, 0, 1), 2)])
    spec["runtime"][0]["session_id"] = TURN2
    assert inspect(root, spec, runtime_root=root)["reason_codes"] == ["SESSION_ID_MISMATCH"]


def test_cumulative_totals_survive_inconsistent_advisory_interval_subsets(fixture) -> None:
    root, spec = fixture
    result = runtime(root, spec, [count(usage(100, 80, 10), usage(100, 80, 10), 2),
        count(usage(101, 90, 11), usage(1, 10, 1), 3)])
    assert result["tokens"] == usage(101, 90, 11)
    assert result["coverage"] == "PARTIAL"
    assert result["reason_codes"] == ["INTERVAL_SUBSETS_INCONSISTENT", "LAST_USAGE_SUBSETS_INCONSISTENT"]


@pytest.mark.parametrize("kind", ["turn_context", "event_msg"])
def test_uninspected_oversized_record_invalidates_attribution(fixture, monkeypatch, kind) -> None:
    root, spec = fixture
    monkeypatch.setattr(summary, "MAX_LINE", 512)
    payload = {"turn_id": TURN2, "model": "gpt-6-astra", "effort": "max",
               "type": "token_count", "padding": "x" * 1024}
    result = runtime(root, spec, [count(usage(100, 80, 10), usage(100, 80, 10), 2),
        event(kind, payload, 3), count(usage(150, 100, 15), usage(50, 20, 5), 4),
        event("turn_context", {"turn_id": TURN, "model": "gpt-6.1-sol", "effort": "xhigh"}, 5),
        count(usage(160, 108, 16), usage(10, 8, 1), 6)])
    assert result["tokens"] == usage(110, 88, 11)
    assert result["coverage"] == "PARTIAL"
    assert "OVERSIZED_LINE_UNINSPECTED" in result["reason_codes"]


@pytest.mark.parametrize("kind", ["response_item", "compacted"])
def test_known_oversized_body_record_keeps_valid_boundary(fixture, monkeypatch, kind) -> None:
    root, spec = fixture
    monkeypatch.setattr(summary, "MAX_LINE", 512)
    oversized = {"timestamp": "2026-01-01T00:00:03Z", "type": kind,
                 "payload": {"padding": "x" * 1024}}
    result = runtime(root, spec, [count(usage(100, 80, 10), usage(100, 80, 10), 2),
        oversized, count(usage(110, 88, 11), usage(10, 8, 1), 4)])
    assert result["tokens"] == usage(110, 88, 11)
    assert result["coverage"] == "SELECTED_COUNTER_WINDOW"


@pytest.mark.parametrize("json_mode", [False, True])
@pytest.mark.parametrize(("state", "next_action", "exit_code"), [
    ("PASS", "TARGET_OWNER_REVIEW_COMPLETION", 0),
    ("UNKNOWN", "TARGET_OWNER_RESOLVE_UNKNOWN_GATES", 0),
    ("mismatch", "RESOLVE_EVIDENCE_MISMATCHES", 1),
])
def test_cli_exit_json_and_plain_are_safe_and_do_not_write(fixture, json_mode, state, next_action, exit_code) -> None:
    root, spec = fixture
    if state == "mismatch":
        spec["identities"][0]["expected"] = "b" * 40
    else:
        change_state(root, spec, lambda d: d["current"]["gates"].update(build=state))
    write_json(root / "spec.json", spec)
    before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    args = [sys.executable, "-B", str(Path(summary.__file__)), "--spec", "spec.json",
            "--spec-root", str(root), "--input-root", str(root)]
    if json_mode:
        args.append("--json")
    result = subprocess.run(args, capture_output=True, check=False, timeout=30)
    assert result.returncode == exit_code
    assert not result.stderr and PRIVATE.encode() not in result.stdout
    assert str(root).encode() not in result.stdout
    assert len(result.stdout) <= summary.MAX_OUTPUT and len(result.stdout.splitlines()) == 1
    if json_mode:
        emitted = json.loads(result.stdout)
        assert emitted["state"]["next_action"] == next_action
        assert emitted["state"]["completion"] is (state == "PASS")
        assert emitted["authorization_status"] == "NOT_AUTHENTICATED"
        assert emitted["usage"] == [] and emitted["usage_totals"] is None
    else:
        assert f"next_action={next_action}".encode() in result.stdout
        assert f"completion={state == 'PASS'}".encode() in result.stdout
        assert b"candidate_binding=BOUND" in result.stdout
        assert b"usage" not in result.stdout and b"tokens" not in result.stdout
    assert before == {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
