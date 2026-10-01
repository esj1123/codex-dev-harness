"""Bounded read-only closeout projection and Codex cumulative usage inspection.

Target-owned selectors/mappings supply meaning. This module never discovers
inputs, executes target commands, authenticates approval, or writes evidence.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any

sys.dont_write_bytecode = True
try:
    from scripts import work_package_conflict_check as paths
except ImportError:  # direct script execution
    import work_package_conflict_check as paths

MAX_JSON = 4 * 1024 * 1024
MAX_SPEC = 64 * 1024
MAX_FILE = 64 * 1024 * 1024
MAX_RUNTIME = 512 * 1024 * 1024
MAX_LINE = 2 * 1024 * 1024
MAX_EVENTS = 100_000
MAX_OUTPUT = 16 * 1024
MAX_TEXT_GATE_IDS = 5
TOKEN_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens",
              "reasoning_output_tokens", "total_tokens")
UUID = re.compile(r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
FIELD = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,79}$")
MODELS = {"gpt-6.1-sol", "gpt-6-sol", "gpt-6-astra", "gpt-6-luna",
          "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.5"}
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def digest(value: Any, width: int = 64) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{%d}" % width, value)
            is not None, "SHA_INVALID")
    return value.lower()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def parse_json(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("JSON_INVALID") from exc


def select(value: Any, pointer: Any) -> Any:
    require(isinstance(pointer, list) and len(pointer) <= 8 and
            all(isinstance(k, str) and FIELD.fullmatch(k) for k in pointer),
            "SELECTOR_INVALID")
    for key in pointer:
        require(isinstance(value, dict) and key in value, "SELECTOR_MISSING")
        value = value[key]
    return value


def safe_file(root: Path, relative: str, limit: int) -> tuple[Path, os.stat_result]:
    require(paths.safe_repo_path(relative), "INPUT_PATH_INVALID")
    candidate = paths._validate_package_parents(root, PurePosixPath(relative))
    info = candidate.lstat()
    require(stat.S_ISREG(info.st_mode) and not paths._is_unsafe_link(info),
            "INPUT_NOT_REGULAR")
    require(info.st_nlink == 1, "INPUT_MULTIPLE_LINKS")
    require(info.st_size <= limit, "INPUT_TOO_LARGE")
    return candidate, info


class Inputs:
    def __init__(self, root: Path):
        self.root = paths._physical_package_root(root)
        self.cache: dict[str, tuple[bytes | None, str]] = {}
        self.bytes_read = 0

    def read(self, relative: str, *, document: bool = False,
             limit: int | None = None) -> tuple[Any, str]:
        maximum = limit if limit is not None else (MAX_JSON if document else MAX_FILE)
        require(paths.safe_repo_path(relative), "INPUT_PATH_INVALID")
        key = relative.lower()
        if key not in self.cache:
            candidate, info = safe_file(self.root, relative, maximum)
            sha = hashlib.sha256()
            chunks: list[bytes] = []
            with candidate.open("rb") as handle:
                before = os.fstat(handle.fileno())
                require(paths._path_descriptor_identity(info) ==
                        paths._path_descriptor_identity(before), "INPUT_IDENTITY_DRIFT")
                while chunk := handle.read(64 * 1024):
                    self.bytes_read += len(chunk)
                    require(self.bytes_read <= 64 * MAX_FILE, "INPUT_BUDGET_EXCEEDED")
                    sha.update(chunk)
                    if document:
                        chunks.append(chunk)
                    require(handle.tell() <= maximum,
                            "INPUT_TOO_LARGE")
                after = os.fstat(handle.fileno())
            paths._physical_package_root(self.root)
            paths._validate_package_parents(self.root, PurePosixPath(relative))
            require(paths._stat_snapshot(before) == paths._stat_snapshot(after) and
                    paths._stat_snapshot(info) == paths._stat_snapshot(candidate.lstat()),
                    "INPUT_IDENTITY_DRIFT")
            self.cache[key] = (b"".join(chunks) if document else None, sha.hexdigest())
        data, sha_hex = self.cache[key]
        if document and data is None:
            # A hash-only read cannot later turn into an unbounded JSON parse.
            del self.cache[key]
            parsed, reread_sha = self.read(relative, document=True, limit=maximum)
            require(reread_sha == sha_hex, "INPUT_IDENTITY_DRIFT")
            return parsed, reread_sha
        return (parse_json(data) if document else None), sha_hex


def classify(value: Any, mapping: Any) -> str:
    require(isinstance(mapping, dict) and set(mapping) == {"completed", "pending", "unknown"},
            "STATE_MAPPING_INVALID")
    seen: set[tuple[type, Any]] = set()
    found = "UNKNOWN"
    for name, codes in mapping.items():
        require(isinstance(codes, list) and len(codes) <= 8, "STATE_MAPPING_INVALID")
        for code in codes:
            require(type(code) is bool or code is None or
                    isinstance(code, str) and re.fullmatch(r"[A-Z][A-Z0-9_]{0,127}", code),
                    "STATE_CODE_INVALID")
            require((type(code), code) not in seen, "STATE_MAPPING_AMBIGUOUS")
            seen.add((type(code), code))
            if type(value) is type(code) and value == code:
                found = name.upper()
    return found


def identifier(value: Any) -> str:
    require(paths.safe_identifier(value), "IDENTIFIER_INVALID")
    return value


def inspect_state(spec: dict[str, Any], inputs: Inputs) -> dict[str, Any]:
    declaration = spec["state"]
    require(set(declaration) == {"path", "sha256", "pointer"}, "STATE_INPUT_INVALID")
    document, state_sha = inputs.read(declaration["path"], document=True)
    require(state_sha == digest(declaration["sha256"]), "STATE_SHA_MISMATCH")
    current = select(document, declaration["pointer"])
    evidence_spec = spec["evidence"]
    require(set(evidence_spec) == {"root", "pointer"}, "EVIDENCE_INPUT_INVALID")
    prefix = evidence_spec["root"]
    require(paths.safe_repo_path(prefix), "EVIDENCE_ROOT_INVALID")
    rows = select(current, evidence_spec["pointer"])
    require(isinstance(rows, list) and 0 < len(rows) <= 64, "EVIDENCE_SET_INVALID")
    hashes: dict[str, str] = {}
    issues: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        require(isinstance(row, dict) and set(row) == {"path", "sha256"}, "EVIDENCE_ROW_INVALID")
        relative = row["path"]
        require(paths.safe_repo_path(relative), "INPUT_PATH_INVALID")
        joined = prefix + "/" + relative
        require(joined.lower() not in hashes, "EVIDENCE_DUPLICATE")
        _, actual = inputs.read(joined)
        hashes[joined.lower()] = actual
        if actual != digest(row["sha256"]):
            issues.append({"kind": "evidence", "index": index, "code": "SHA_MISMATCH"})
    links = spec["links"]
    require(isinstance(links, list) and len(links) <= 64, "LINK_SET_INVALID")
    for index, link in enumerate(links):
        require(set(link) == {"receipt", "pointer", "target"}, "LINK_INVALID")
        require(isinstance(link["receipt"], str) and isinstance(link["target"], str) and
                link["receipt"].lower() in hashes and link["target"].lower() in hashes,
                "LINK_OUTSIDE_EVIDENCE")
        receipt, receipt_sha = inputs.read(link["receipt"], document=True)
        require(receipt_sha == hashes[link["receipt"].lower()], "INPUT_IDENTITY_DRIFT")
        if digest(select(receipt, link["pointer"])) != hashes[link["target"].lower()]:
            issues.append({"kind": "link", "index": index, "code": "SHA_MISMATCH"})
    identities: dict[str, str] = {}
    require(isinstance(spec["identities"], list) and len(spec["identities"]) <= 8,
            "IDENTITY_SET_INVALID")
    for row in spec["identities"]:
        require(set(row) == {"id", "pointer", "expected"}, "IDENTITY_INVALID")
        key = identifier(row["id"])
        require(key not in identities, "IDENTITY_DUPLICATE")
        expected = row["expected"]
        require(isinstance(expected, str) and len(expected) in {40, 64}, "SHA_INVALID")
        identities[key] = digest(select(current, row["pointer"]), len(expected))
        if identities[key] != digest(expected, len(expected)):
            issues.append({"kind": "identity", "id": key, "code": "SHA_MISMATCH"})
    gates: dict[str, str] = {}
    require(isinstance(spec["gates"], list) and 0 < len(spec["gates"]) <= 32,
            "GATE_SET_INVALID")
    for gate in spec["gates"]:
        require(set(gate) == {"id", "pointer", "states", "proofs"}, "GATE_INVALID")
        key = identifier(gate["id"])
        require(key not in gates, "GATE_DUPLICATE")
        proofs = gate["proofs"]
        require(isinstance(proofs, list) and len(proofs) <= 8 and
                all(isinstance(p, str) and p.lower() in hashes for p in proofs),
                "GATE_PROOF_INVALID")
        state = classify(select(current, gate["pointer"]), gate["states"])
        gates[key] = "UNKNOWN" if issues or state == "COMPLETED" and not proofs else state
    conflicts = []
    require(isinstance(spec["history"], list) and len(spec["history"]) <= 16,
            "HISTORY_SET_INVALID")
    for item in spec["history"]:
        require(set(item) == {"id", "path", "pointer", "states", "gate"}, "HISTORY_INVALID")
        key = identifier(item["id"])
        require(item["gate"] in gates, "HISTORY_GATE_INVALID")
        require(isinstance(item["path"], str) and
                (item["path"] == declaration["path"] or item["path"].lower() in hashes),
                "HISTORY_OUTSIDE_EVIDENCE")
        history, _ = inputs.read(item["path"], document=True)
        previous = classify(select(history, item["pointer"]), item["states"])
        latest = gates[item["gate"]]
        if previous != latest:
            conflicts.append({"id": key, "gate": item["gate"], "previous": previous,
                              "current": latest, "code": "SUPERSEDED_CLAIM"})
    candidate = spec["candidate"]
    require(set(candidate) == {"path", "sha256"} and paths.safe_repo_path(candidate["path"]),
            "CANDIDATE_INVALID")
    binding = "UNKNOWN"
    try:
        _, candidate_sha = inputs.read(candidate["path"])
        if candidate["sha256"] is not None:
            if candidate_sha == digest(candidate["sha256"]):
                binding = "BOUND"
            else:
                issues.append({"kind": "candidate", "code": "SHA_MISMATCH"})
    except FileNotFoundError:
        binding = "MISSING"
        if candidate["sha256"] is not None:
            issues.append({"kind": "candidate", "code": "MISSING"})
    counts = {key.lower(): list(gates.values()).count(key)
              for key in ("COMPLETED", "PENDING", "UNKNOWN")}
    if issues:
        next_action = "RESOLVE_EVIDENCE_MISMATCHES"
    elif binding == "MISSING":
        next_action = "TARGET_OWNER_SUPPLY_CANDIDATE"
    elif binding != "BOUND":
        next_action = "TARGET_OWNER_BIND_CANDIDATE"
    elif counts["pending"]:
        next_action = "TARGET_OWNER_COMPLETE_PENDING_GATES"
    elif counts["unknown"]:
        next_action = "TARGET_OWNER_RESOLVE_UNKNOWN_GATES"
    else:
        next_action = "TARGET_OWNER_REVIEW_COMPLETION"
    return {"input_sha256": state_sha, "identities": identities,
            "evidence_consistency": "FAIL" if issues else "PASS",
            "evidence_count": len(hashes), "link_count": len(links), "mismatches": issues,
            "gates": gates, "counts": counts, "superseded_claims": conflicts,
            "candidate_binding": binding,
            "completion": bool(not issues and binding == "BOUND" and
                               counts["completed"] == len(gates)),
            "next_action": next_action}


def timestamp(value: Any) -> datetime:
    require(isinstance(value, str) and len(value) <= 35, "TIMESTAMP_INVALID")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("TIMESTAMP_INVALID") from exc
    require(result.tzinfo is not None and result.utcoffset().total_seconds() == 0,
            "TIMESTAMP_INVALID")
    return result


def tokens(value: Any, *, check_subsets: bool = True) -> tuple[int, ...]:
    require(isinstance(value, dict), "TOKEN_COUNTER_INVALID")
    result = tuple(value.get(k) for k in TOKEN_KEYS)
    require(all(type(n) is int and 0 <= n <= 2**63 - 1 for n in result),
            "TOKEN_COUNTER_INVALID")
    require(result[4] == result[0] + result[2], "TOKEN_TOTAL_INVALID")
    if check_subsets:
        require(result[1] <= result[0] and result[3] <= result[2], "TOKEN_SUBSETS_INVALID")
    return result


def inspect_runtime(root: Path, source: dict[str, Any]) -> dict[str, Any]:
    require(set(source) == {"id", "path", "session_id", "turns", "cutoff"}, "RUNTIME_SOURCE_INVALID")
    source_id = identifier(source["id"])
    require(isinstance(source["session_id"], str) and UUID.fullmatch(source["session_id"]),
            "SESSION_ID_INVALID")
    selected = source["turns"]
    require(isinstance(selected, list) and 0 < len(selected) <= 64 and
            len(set(selected)) == len(selected) and
            all(isinstance(t, str) and UUID.fullmatch(t) for t in selected), "TURN_SET_INVALID")
    cutoff = timestamp(source["cutoff"])
    candidate, info = safe_file(root, source["path"], MAX_RUNTIME)
    reasons: set[str] = set()
    seen: set[str] = set()
    seen_turns: set[str] = set()
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    previous = None
    counter_started = False
    context: tuple[str | None, str, str] = (None, "UNKNOWN", "UNKNOWN")
    events = duplicates = zero = resets = invalid = 0
    session_seen = False
    sha = hashlib.sha256()
    read_bytes = 0
    with candidate.open("rb") as handle:
        before = os.fstat(handle.fileno())
        require(paths._path_descriptor_identity(info) ==
                paths._path_descriptor_identity(before), "RUNTIME_IDENTITY_DRIFT")
        while read_bytes < info.st_size:
            line = handle.readline(min(MAX_LINE + 1, info.st_size - read_bytes))
            if not line:
                break
            read_bytes += len(line)
            sha.update(line)
            oversized = len(line) > MAX_LINE
            if oversized:
                header = re.match(rb'^\s*\{\s*"timestamp"\s*:\s*"[^"\r\n]{1,40}"\s*,\s*"type"\s*:\s*"([a-z_]+)"\s*,', line[:200])
                irrelevant_event = re.match(rb'^\s*\{\s*"timestamp"\s*:\s*"[^"\r\n]{1,40}"\s*,\s*"type"\s*:\s*"event_msg"\s*,\s*"payload"\s*:\s*\{\s*"type"\s*:\s*"(?:agent_message|user_message|agent_reasoning|task_started|task_complete)"\s*,', line[:300])
                while not line.endswith(b"\n") and read_bytes < info.st_size:
                    line = handle.readline(min(MAX_LINE, info.st_size - read_bytes))
                    read_bytes += len(line)
                    sha.update(line)
                if not irrelevant_event and (not header or header.group(1) not in {b"response_item", b"compacted"}):
                    reasons.add("OVERSIZED_LINE_UNINSPECTED")
                    # An uninspected record may change the turn or cumulative
                    # counter. Never carry attribution across that boundary.
                    previous = None
                    counter_started = True
                    context = (None, "UNKNOWN", "UNKNOWN")
                continue
            if not any(marker in line for marker in
                       (b'"session_meta"', b'"turn_context"', b'"token_count"')):
                continue
            kind = None
            try:
                event = parse_json(line)
                require(isinstance(event, dict), "RUNTIME_EVENT_INVALID")
                kind = event.get("type")
                if kind not in {"session_meta", "turn_context", "event_msg"}:
                    continue
                payload = event.get("payload")
                require(isinstance(payload, dict), "RUNTIME_EVENT_INVALID")
                if timestamp(event.get("timestamp")) > cutoff:
                    continue
                if not line.endswith(b"\n"):
                    reasons.add("TRUNCATED_LINE")
                if kind == "session_meta":
                    require(payload.get("id") == source["session_id"], "SESSION_ID_MISMATCH")
                    session_seen = True
                    continue
                if kind == "turn_context":
                    turn = payload.get("turn_id")
                    require(isinstance(turn, str) and UUID.fullmatch(turn), "TURN_ID_INVALID")
                    model = payload.get("model")
                    effort = payload.get("effort")
                    context = (turn, model if model in MODELS else "UNKNOWN",
                               effort if effort in EFFORTS else "UNKNOWN")
                    if turn in selected:
                        seen_turns.add(turn)
                        if "UNKNOWN" in context:
                            reasons.add("ROUTING_UNKNOWN")
                    continue
                if payload.get("type") != "token_count":
                    continue
                active = context[0] in selected
                if active:
                    events += 1
                usage = payload.get("info")
                require(isinstance(usage, dict), "TOKEN_INFO_MISSING")
                current = tokens(usage.get("total_token_usage"))
                key = hashlib.sha256(json.dumps([source["session_id"], event["timestamp"], current],
                                               separators=(",", ":")).encode()).hexdigest()
                if key in seen:
                    if active:
                        duplicates += 1
                    continue
                require(len(seen) < MAX_EVENTS, "EVENT_LIMIT_EXCEEDED")
                seen.add(key)
                if previous == current:
                    if active:
                        zero += 1
                    continue
                try:
                    last = tokens(usage.get("last_token_usage"), check_subsets=False)
                except ValueError:
                    last = None
                    if active:
                        reasons.add("LAST_USAGE_MISSING_OR_INVALID")
                if active and last is not None and (last[1] > last[0] or last[3] > last[2]):
                    reasons.add("LAST_USAGE_SUBSETS_INCONSISTENT")
                if previous is None:
                    delta = current if not counter_started and current == last else None
                    if active and delta is None:
                        reasons.add("INITIAL_BOUNDARY_MISSING")
                elif any(c < p for c, p in zip(current, previous)):
                    delta = None
                    if active:
                        resets += 1
                        reasons.add("COUNTER_RESET_BOUNDARY_MISSING")
                else:
                    delta = tuple(c - p for c, p in zip(current, previous))
                previous = current
                counter_started = True
                if not active or delta is None:
                    continue
                tokens(dict(zip(TOKEN_KEYS, delta)), check_subsets=False)
                if delta[1] > delta[0] or delta[3] > delta[2]:
                    reasons.add("INTERVAL_SUBSETS_INCONSISTENT")
                if delta != last:
                    reasons.add("TOKEN_EVENT_GAP_OR_LAST_DISCREPANCY")
                group = groups.setdefault(context, {"turn_id": context[0], "model": context[1],
                    "effort": context[2], "tokens": dict.fromkeys(TOKEN_KEYS, 0),
                    "positive_token_events": 0, "first_usage_utc": event["timestamp"],
                    "last_usage_utc": event["timestamp"]})
                require(len(groups) <= 128, "ROUTING_GROUP_LIMIT_EXCEEDED")
                for name, amount in zip(TOKEN_KEYS, delta):
                    group["tokens"][name] += amount
                group["positive_token_events"] += 1
                group["last_usage_utc"] = event["timestamp"]
            except (ValueError, TypeError, KeyError) as exc:
                if isinstance(exc, ValueError) and str(exc) == "SESSION_ID_MISMATCH":
                    raise
                invalid += 1
                reasons.add("INVALID_OR_TRUNCATED_METADATA_EVENT")
                # The next valid cumulative observation re-establishes a boundary;
                # never attribute an interval spanning corrupt metadata to a turn.
                previous = None
                counter_started = True
                if kind is None or kind == "turn_context":
                    context = (None, "UNKNOWN", "UNKNOWN")
        # Re-hash the captured prefix: active append is permitted, in-place drift
        # is rejected. No transcript copy or open-ended follow is created.
        handle.seek(0)
        verify_sha = hashlib.sha256()
        remaining = read_bytes
        while remaining:
            chunk = handle.read(min(64 * 1024, remaining))
            require(bool(chunk), "RUNTIME_IDENTITY_DRIFT")
            verify_sha.update(chunk)
            remaining -= len(chunk)
        after = os.fstat(handle.fileno())
    path_after = candidate.lstat()
    paths._physical_package_root(root)
    paths._validate_package_parents(root, PurePosixPath(source["path"]))
    require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino) ==
            (path_after.st_dev, path_after.st_ino) and
            after.st_size >= info.st_size and not paths._is_unsafe_link(path_after) and
            path_after.st_nlink == 1 and sha.digest() == verify_sha.digest(),
            "RUNTIME_IDENTITY_DRIFT")
    if not session_seen:
        reasons.add("SESSION_ID_UNVERIFIED")
    if set(selected) != seen_turns or any(not any(g[0] == turn for g in groups) for turn in selected):
        reasons.add("SELECTED_TURN_COVERAGE_MISSING")
    totals = {name: sum(g["tokens"][name] for g in groups.values()) for name in TOKEN_KEYS}
    return {"id": source_id, "session_id": source["session_id"],
            "prefix_sha256": sha.hexdigest(), "prefix_bytes": read_bytes,
            "bytes_read": read_bytes * 2, "cutoff": source["cutoff"],
            "coverage": "PARTIAL" if reasons else "SELECTED_COUNTER_WINDOW",
            "reason_codes": sorted(reasons), "tokens": totals, "token_events": events,
            "duplicate_events": duplicates, "zero_snapshots": zero,
            "resets": resets, "invalid_events": invalid,
            "positive_token_events": sum(g["positive_token_events"] for g in groups.values()),
            "event_key_basis": "session_id,timestamp,cumulative_token_tuple",
            "model_calls": None, "app_turn_duration_ms": None,
            "time_basis": "USAGE_EVENT_TIMESTAMPS_ONLY",
            "groups": sorted(groups.values(), key=lambda g: (g["turn_id"], g["model"], g["effort"]))}


def inspect_summary(spec_path: str, *, spec_root: Path, input_root: Path,
                    runtime_root: Path | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"schema_version": "1", "checker_id": "task_evidence_summary",
        "status": "FAIL", "authorization_status": "NOT_AUTHENTICATED",
        "reason_codes": [], "performed_actions": [], "savings": "NOT_MEASURED"}
    try:
        config_inputs = Inputs(spec_root)
        spec, spec_sha = config_inputs.read(spec_path, document=True, limit=MAX_SPEC)
        require(isinstance(spec, dict) and set(spec) == {"schema_version", "state", "identities",
                "candidate", "evidence", "links", "gates", "history", "runtime"} and
                spec["schema_version"] == "1", "SPEC_INVALID")
        inputs = Inputs(input_root)
        result["spec_sha256"] = spec_sha
        result["state"] = inspect_state(spec, inputs)
        sources = spec["runtime"]
        require(isinstance(sources, list) and len(sources) <= 8, "RUNTIME_SET_INVALID")
        require(not sources or runtime_root is not None, "RUNTIME_ROOT_REQUIRED")
        require(len({s["session_id"] for s in sources}) == len(sources) and
                len({s["id"] for s in sources}) == len(sources), "RUNTIME_SOURCE_OVERLAP")
        result["usage"] = [] if not sources else [inspect_runtime(
            paths._physical_package_root(runtime_root), source) for source in sources]
        result["usage_totals"] = ({key: sum(s["tokens"][key] for s in result["usage"])
                                    for key in TOKEN_KEYS} if sources and not any(
            "SESSION_ID_UNVERIFIED" in s["reason_codes"] for s in result["usage"]) else None)
        result["input_bytes_read"] = config_inputs.bytes_read + inputs.bytes_read + sum(
            s["bytes_read"] for s in result["usage"])
        result["status"] = result["state"]["evidence_consistency"]
        if result["status"] != "PASS":
            result["reason_codes"] = ["EVIDENCE_MISMATCH"]
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        # Input strings, payloads and exception messages are deliberately absent.
        result = {k: result[k] for k in ("schema_version", "checker_id", "authorization_status",
                                       "performed_actions", "savings")}
        known = str(exc) if isinstance(exc, ValueError) else "INPUT_INSPECTION_FAILED"
        code = known if re.fullmatch(r"[A-Z_]{1,80}", known) else "INPUT_INSPECTION_FAILED"
        result.update(status="FAIL", reason_codes=[code])
    return result


def output_bytes(result: dict[str, Any]) -> bytes:
    payload = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(payload) > MAX_OUTPUT:
        return b'{"checker_id":"task_evidence_summary","status":"FAIL","reason_codes":["OUTPUT_TOO_LARGE"],"performed_actions":[]}\n'
    return payload


def text_summary(result: dict[str, Any]) -> str:
    """Project bounded decision fields from the same fail-closed JSON envelope."""
    emitted = json.loads(output_bytes(result))
    state = emitted.get("state", {})
    counts = state.get("counts", {})
    fields = [f"status={emitted['status']}",
              f"candidate_binding={state.get('candidate_binding', 'UNKNOWN')}",
              f"completion={state.get('completion', False)}",
              "counts=" + ",".join(f"{key}:{counts.get(key, 0)}"
                                    for key in ("completed", "pending", "unknown")),
              f"next_action={state.get('next_action', 'RESOLVE_INPUT_INSPECTION_FAILURE')}"]
    for name in ("pending", "unknown"):
        keys = sorted(key for key, value in state.get("gates", {}).items()
                      if value == name.upper())
        fields.append(f"{name}=" + (",".join(keys[:MAX_TEXT_GATE_IDS]) or "NONE"))
        fields.append(f"{name}_omitted={max(0, len(keys) - MAX_TEXT_GATE_IDS)}")
    fields.append("reasons=" + (",".join(emitted.get("reason_codes", [])) or "NONE"))
    return " ".join(fields)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Exact spec-root-relative JSON")
    parser.add_argument("--spec-root", default=".")
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--runtime-root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = inspect_summary(args.spec, spec_root=Path(args.spec_root),
        input_root=Path(args.input_root), runtime_root=Path(args.runtime_root) if args.runtime_root else None)
    payload = output_bytes(result)
    emitted = json.loads(payload)
    if args.json:
        sys.stdout.buffer.write(payload)
    else:
        print(text_summary(emitted))
    return 0 if emitted["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
