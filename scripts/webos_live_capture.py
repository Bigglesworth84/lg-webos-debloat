#!/usr/bin/env python3
"""Controlled live inventory adapter. Tests must use mocked Distrobox executables."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # Support both `python scripts/webos_live_capture.py` and package imports in tests.
    from .webos_inventory import (
        DEVICE_OPERATIONS, RESTORE_CLASSIFICATION, InventoryError, command_argv,
        parse_applications, parse_device_metadata, prepare_output_root, secure_directory,
        secure_write, serialize_json, sha256_file, validate_alias,
    )
except ImportError:
    from webos_inventory import (
        DEVICE_OPERATIONS, RESTORE_CLASSIFICATION, InventoryError, command_argv,
        parse_applications, parse_device_metadata, prepare_output_root, secure_directory,
        secure_write, serialize_json, sha256_file, validate_alias,
    )

TOOL_NAME = "webos-live-capture"
TOOL_VERSION = "0.2.0"
SCHEMA_VERSION = 2
TIMEOUT_SECONDS = 30
MAX_OUTPUT_BYTES = 1024 * 1024
CLI_VERSION = "3.2.6"
NODE_VERSION = "v24.22.1"
METADATA_ALLOWLIST = frozenset({"modelName", "sdkVersion", "firmwareVersion", "boardType"})
APP_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{1,127}$")
SAFE_METADATA_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]{0,127}$")
IPV4_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
AUTH_FAILURE_RE = re.compile(r"(?:auth(?:entication|orization)?|permission denied|connection refused|connection timed out|unable to connect|could not connect|socket hang up)", re.I)
MISSING_EXECUTABLE_RE = re.compile(r"(?:command not found|no such file or directory|missing executable|cli is missing|not found)", re.I)
OPERATIONS = tuple(DEVICE_OPERATIONS)
EXECUTION_OUTCOMES = {"succeeded", "failed", "timed_out", "output_limit_exceeded", "skipped"}
PARSING_OUTCOMES = {
    "recognized_records", "successful_empty_output", "recognized_empty_json_collection",
    "unrecognized_output", "partial_records", "not_parsed",
}
ARTIFACT_NAMES = {
    "metadata": "device-metadata.json",
    "applications": "applications.json",
    "applications-full": "applications-full.json",
}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _validate_selection(alias: str, operations: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    validate_alias(alias)
    if not operations:
        raise InventoryError("Select at least one operation explicitly.")
    selected: list[str] = []
    for operation in operations:
        if operation not in OPERATIONS:
            raise InventoryError(f"Unsupported operation: {operation}")
        if operation in selected:
            raise InventoryError(f"Operation selected more than once: {operation}")
        selected.append(operation)
    return tuple(selected)


def _safe_metadata_value(value: str) -> bool:
    return bool(SAFE_METADATA_VALUE_RE.fullmatch(value) and not IPV4_RE.fullmatch(value) and not MAC_RE.fullmatch(value))


def _valid_app_id(value: Any) -> bool:
    return isinstance(value, str) and "." in value and bool(APP_ID_RE.fullmatch(value)) and not IPV4_RE.fullmatch(value)


def _process_environment() -> dict[str, str]:
    """Pass only host identity/session variables needed to enter Distrobox."""
    permitted = {
        "HOME", "USER", "LOGNAME", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS",
        "LANG", "LC_ALL", "TERM", "DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY",
    }
    environment = {key: value for key, value in os.environ.items() if key in permitted}
    environment["PATH"] = ":".join(("/usr/bin", "/usr/local/bin", f"{Path.home()}/.local/bin", "/bin"))
    return environment


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            pass


def _run_bounded(argv: tuple[str, ...], timeout_seconds: int, output_limit: int) -> dict[str, Any]:
    started = timestamp()
    try:
        process = subprocess.Popen(
            list(argv),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_process_environment(),
            close_fds=True,
            start_new_session=True,
        )
    except OSError as exc:
        return {
            "execution_outcome": "failed", "failure_classification": "environment_or_cli_unavailable",
            "exit_status": None, "stdout": b"", "stderr": b"", "stdout_size_bytes": 0,
            "stderr_size_bytes": 0, "stdout_truncated": False, "stderr_truncated": False,
            "start_timestamp_utc": started, "end_timestamp_utc": timestamp(),
            "safe_diagnostic": "executable_unavailable" if isinstance(exc, FileNotFoundError) else "process_start_failed",
        }

    assert process.stdout is not None and process.stderr is not None
    stdout_stream, stderr_stream = process.stdout, process.stderr
    output = {stdout_stream: bytearray(), stderr_stream: bytearray()}
    totals = {stdout_stream: 0, stderr_stream: 0}
    truncated = {stdout_stream: False, stderr_stream: False}
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    selector.register(process.stderr, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout_seconds
    result = "succeeded"
    while selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            result = "timed_out"
            _terminate_process(process)
            break
        events = selector.select(min(remaining, 0.1))
        if not events and process.poll() is not None:
            # Drain EOFs after exit; select reports readable descriptors once buffered bytes are exhausted.
            continue
        for key, _ in events:
            stream = key.fileobj
            try:
                block = os.read(stream.fileno(), min(65536, output_limit + 1))
            except OSError:
                block = b""
            if not block:
                selector.unregister(stream)
                stream.close()
                continue
            totals[stream] += len(block)
            room = max(0, output_limit - sum(map(len, output.values())))
            if room:
                output[stream].extend(block[:room])
            if len(block) > room:
                truncated[stream] = True
                result = "output_limit_exceeded"
                _terminate_process(process)
                break
        if result != "succeeded":
            break

    if result != "succeeded":
        for stream in tuple(selector.get_map().values()):
            try:
                selector.unregister(stream.fileobj)
                stream.fileobj.close()
            except (KeyError, OSError):
                pass
        # Ensure a container-side launcher is reaped even if it did not exit on the group signal.
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            _terminate_process(process)
    else:
        try:
            process.wait(timeout=max(0.0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            result = "timed_out"
            _terminate_process(process)
    selector.close()
    exit_status = process.returncode
    stdout_bytes = bytes(output[stdout_stream])
    stderr_bytes = bytes(output[stderr_stream])
    if result == "succeeded" and exit_status != 0:
        result = "failed"
    diagnostic = "none"
    if result == "failed":
        stderr_text = stderr_bytes.decode("utf-8", "replace")
        if AUTH_FAILURE_RE.search(stderr_text):
            diagnostic = "connection_or_authentication_failure"
        elif MISSING_EXECUTABLE_RE.search(stderr_text):
            diagnostic = "environment_or_cli_unavailable"
        else:
            diagnostic = "command_failed"
    return {
        "execution_outcome": result,
        "failure_classification": diagnostic,
        "exit_status": exit_status,
        "stdout": stdout_bytes,
        "stderr": stderr_bytes,
        "stdout_size_bytes": totals[stdout_stream],
        "stderr_size_bytes": totals[stderr_stream],
        "stdout_truncated": truncated[stdout_stream],
        "stderr_truncated": truncated[stderr_stream],
        "start_timestamp_utc": started,
        "end_timestamp_utc": timestamp(),
        "safe_diagnostic": diagnostic if diagnostic != "none" else "none",
    }


def _parse_metadata(data: bytes) -> tuple[dict[str, str], str, dict[str, int]]:
    text = data.decode("utf-8", "replace")
    parsed, _ = parse_device_metadata(text)
    allowed: dict[str, str] = {}
    rejected = 0
    recognized_lines = 0
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$", line)
        if not match:
            if line.strip():
                rejected += 1
            continue
        key, value = match.groups()
        if key not in METADATA_ALLOWLIST:
            rejected += 1
            continue
        recognized_lines += 1
        if key in parsed and parsed[key] == value and _safe_metadata_value(value):
            allowed[key] = value
        else:
            rejected += 1
    if not data:
        status = "successful_empty_output"
    elif not recognized_lines:
        status = "unrecognized_output"
    elif rejected or len(allowed) < len(METADATA_ALLOWLIST):
        status = "partial_records"
    else:
        status = "recognized_records"
    return allowed, status, {"accepted": len(allowed), "rejected": rejected}


def _parse_apps(data: bytes) -> tuple[list[str], str, dict[str, int | None]]:
    if not data:
        return [], "successful_empty_output", {"accepted": 0, "rejected": 0, "total": None}
    text = data.decode("utf-8", "replace")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        decoded = None
    records, parser_status, counts = parse_applications(text)
    if isinstance(decoded, list) and not decoded:
        return [], "recognized_empty_json_collection", counts
    if isinstance(decoded, dict) and any(decoded.get(key) == [] for key in ("applications", "apps")):
        return [], "recognized_empty_json_collection", counts
    ids = [record["id"] for record in records if _valid_app_id(record.get("id"))]
    rejected = (counts.get("rejected") or 0) + (len(records) - len(ids))
    counts = {"accepted": len(ids), "rejected": rejected, "total": counts.get("total")}
    if parser_status == "unexpected":
        status = "unrecognized_output"
    elif parser_status == "partial" or rejected:
        status = "partial_records"
    else:
        status = "recognized_records"
    return ids, status, counts


def _operation_result(operation: str, alias: str, outcome: dict[str, Any] | None) -> tuple[dict[str, Any], bytes]:
    argv = command_argv(operation, alias)
    if outcome is None:
        record = {
            "operation": operation, "command_argv": list(argv), "execution_outcome": "skipped",
            "parsing_outcome": "not_parsed", "exit_status": None,
            "failure_classification": "not_attempted", "start_timestamp_utc": None,
            "end_timestamp_utc": None, "stdout_present": False, "stdout_size_bytes": 0,
            "stderr_present": False, "stderr_size_bytes": 0, "accepted_records": 0,
            "rejected_records": 0, "artifact": ARTIFACT_NAMES[operation],
        }
        content = {"application_ids": [], "capture_status": "not_parsed", "record_counts": {"accepted": 0, "rejected": 0, "total": None}}
        if operation == "metadata":
            content = {"fields": {}, "missing_fields": sorted(METADATA_ALLOWLIST), "capture_status": "not_parsed", "record_counts": {"accepted": 0, "rejected": 0}}
        return record, serialize_json(content)

    execution = outcome["execution_outcome"]
    raw_stdout = outcome["stdout"]
    if execution != "succeeded":
        parsing = "not_parsed"
        data: dict[str, Any]
        if operation == "metadata":
            data = {"fields": {}, "missing_fields": sorted(METADATA_ALLOWLIST), "capture_status": parsing, "record_counts": {"accepted": 0, "rejected": 0}}
        else:
            data = {"application_ids": [], "capture_status": parsing, "record_counts": {"accepted": 0, "rejected": 0, "total": None}}
        counts = {"accepted": 0, "rejected": 0}
    elif operation == "metadata":
        fields, parsing, counts = _parse_metadata(raw_stdout)
        data = {
            "fields": fields,
            "missing_fields": sorted(METADATA_ALLOWLIST - fields.keys()),
            "capture_status": parsing,
            "record_counts": counts,
        }
    else:
        app_ids, parsing, counts = _parse_apps(raw_stdout)
        data = {"application_ids": app_ids, "capture_status": parsing, "record_counts": counts}

    record = {
        "operation": operation,
        "command_argv": list(argv),
        "execution_outcome": execution,
        "parsing_outcome": parsing,
        "exit_status": outcome["exit_status"],
        "failure_classification": outcome["failure_classification"],
        "start_timestamp_utc": outcome["start_timestamp_utc"],
        "end_timestamp_utc": outcome["end_timestamp_utc"],
        "stdout_present": outcome["stdout_size_bytes"] > 0,
        "stdout_size_bytes": outcome["stdout_size_bytes"],
        "stderr_present": outcome["stderr_size_bytes"] > 0,
        "stderr_size_bytes": outcome["stderr_size_bytes"],
        "accepted_records": counts.get("accepted", 0),
        "rejected_records": counts.get("rejected", 0),
        "artifact": ARTIFACT_NAMES[operation],
    }
    return record, serialize_json(data)


def create_live_snapshot(
    output_root: Path,
    device_alias: str,
    operations: list[str] | tuple[str, ...],
) -> Path:
    """Execute each selected approved operation at most once and persist sanitized results."""
    selected = _validate_selection(device_alias, operations)
    prepare_output_root(output_root)
    capture_started = timestamp()
    outcomes: dict[str, dict[str, Any] | None] = {}
    stop = False
    for operation in selected:
        if stop:
            outcomes[operation] = None
            continue
        argv = (str(Path(__file__).with_name("webos-cli-env.sh")), "capture", operation, device_alias, *command_argv(operation, device_alias))
        result = _run_bounded(argv, TIMEOUT_SECONDS, MAX_OUTPUT_BYTES)
        outcomes[operation] = result
        # Any execution failure stops further device communication for this capture.
        if result["execution_outcome"] != "succeeded":
            stop = True

    capture_ended = timestamp()
    stamp = capture_started.replace(":", "-")
    snapshot = output_root / stamp
    secure_directory(snapshot)
    operation_records: list[dict[str, Any]] = []
    artifacts: dict[str, dict[str, Any]] = {}
    for operation in selected:
        record, artifact_bytes = _operation_result(operation, device_alias, outcomes[operation])
        operation_records.append(record)
        name = ARTIFACT_NAMES[operation]
        secure_write(snapshot / name, artifact_bytes)
        artifacts[name] = {
            "type": "informational metadata" if operation == "metadata" else "read-only observation",
            "capture_status": record["parsing_outcome"],
            "size_bytes": len(artifact_bytes),
            "sha256": hashlib.sha256(artifact_bytes).hexdigest(),
            "coverage_limitations": [
                "This artifact is an observation, not a restorable TV backup.",
                "Developer Mode CLI output does not establish complete application catalogue coverage.",
            ],
            "recovery_classification": RESTORE_CLASSIFICATION,
        }

    successful = all(
        item["execution_outcome"] == "succeeded"
        and item["parsing_outcome"] in {"recognized_records", "successful_empty_output", "recognized_empty_json_collection"}
        for item in operation_records
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "capture_mode": "live-read-only",
        "capture_started_at_utc": capture_started,
        "capture_ended_at_utc": capture_ended,
        "device_alias": device_alias,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "python_version": sys.version.split()[0],
        "node_version": NODE_VERSION,
        "cli_version": CLI_VERSION,
        "selected_operations": list(selected),
        "capture_status": "successful_capture" if successful else "partial",
        "inventory_coverage": "unknown_or_incomplete",
        "coverage_limitations": [
            "A successful command does not prove a complete installed-app inventory.",
            "Built-in, LG Store, system and hidden applications may be absent from CLI output.",
            "Application IDs do not establish removability or system-package coverage.",
            "No general TV backup or restore functionality is established.",
        ],
        "operations": operation_records,
        "restorable_artifacts": [],
        "recovery_classification": RESTORE_CLASSIFICATION,
        "artifacts": artifacts,
    }
    secure_write(snapshot / "manifest.json", serialize_json(manifest))
    return snapshot


def validate_live_snapshot(snapshot: Path, manifest: dict[str, Any] | None = None) -> list[str]:
    """Validate a schema 2 live snapshot without interpreting it as a backup."""
    problems: list[str] = []
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise InventoryError("Snapshot path must be a regular directory.")
    manifest_path = snapshot / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InventoryError("Snapshot manifest must be a regular file.")
    if manifest is None:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InventoryError("Cannot read snapshot manifest.") from exc
    if not isinstance(manifest, dict):
        raise InventoryError("Snapshot manifest must be a JSON object.")
    required = {
        "schema_version", "capture_mode", "capture_started_at_utc", "capture_ended_at_utc",
        "device_alias", "tool", "python_version", "node_version", "cli_version",
        "selected_operations", "capture_status", "inventory_coverage", "coverage_limitations",
        "operations", "restorable_artifacts", "recovery_classification", "artifacts",
    }
    if set(manifest) != required:
        problems.append("invalid live manifest fields")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("capture_mode") != "live-read-only":
        problems.append("unsupported live snapshot schema or mode")
    try:
        validate_alias(manifest.get("device_alias"))
    except (InventoryError, TypeError):
        problems.append("invalid device alias")
    for name in ("capture_started_at_utc", "capture_ended_at_utc"):
        value = manifest.get(name)
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?Z", value):
            problems.append(f"invalid {name}")
        else:
            try:
                datetime.fromisoformat(value[:-1] + "+00:00")
            except ValueError:
                problems.append(f"invalid {name}")
    if not isinstance(manifest.get("tool"), dict) or manifest["tool"] != {"name": TOOL_NAME, "version": TOOL_VERSION}:
        problems.append("invalid tool version fields")
    for name in ("python_version", "node_version", "cli_version"):
        if not isinstance(manifest.get(name), str) or not manifest[name]:
            problems.append(f"invalid {name}")
    if manifest.get("node_version") != NODE_VERSION or manifest.get("cli_version") != CLI_VERSION:
        problems.append("unexpected pinned runtime versions")
    if manifest.get("capture_status") not in {"successful_capture", "partial"}:
        problems.append("invalid capture status")
    if manifest.get("inventory_coverage") != "unknown_or_incomplete":
        problems.append("invalid inventory coverage classification")
    if manifest.get("recovery_classification") != RESTORE_CLASSIFICATION or manifest.get("restorable_artifacts") != []:
        problems.append("live snapshots cannot claim restorable artifacts")
    if not isinstance(manifest.get("coverage_limitations"), list) or not all(isinstance(item, str) for item in manifest.get("coverage_limitations", [])):
        problems.append("invalid coverage limitations")

    selected = manifest.get("selected_operations")
    if (
        not isinstance(selected, list) or not selected
        or any(not isinstance(item, str) or item not in OPERATIONS for item in selected)
        or len(selected) != len(set(item for item in selected if isinstance(item, str)))
    ):
        problems.append("invalid selected operations")
        selected = []
    records = manifest.get("operations")
    if not isinstance(records, list) or [r.get("operation") for r in records if isinstance(r, dict)] != selected:
        problems.append("operation records do not match selected operations")
        records = []
    record_fields = {
        "operation", "command_argv", "execution_outcome", "parsing_outcome", "exit_status",
        "failure_classification", "start_timestamp_utc", "end_timestamp_utc", "stdout_present",
        "stdout_size_bytes", "stderr_present", "stderr_size_bytes", "accepted_records",
        "rejected_records", "artifact",
    }
    for record in records:
        if not isinstance(record, dict) or set(record) != record_fields:
            problems.append("invalid operation record fields")
            continue
        operation = record.get("operation")
        if operation not in OPERATIONS:
            problems.append("unsupported operation record")
            continue
        try:
            approved_vector = list(command_argv(operation, manifest.get("device_alias")))
        except (InventoryError, TypeError):
            approved_vector = []
        if record.get("command_argv") != approved_vector:
            problems.append(f"unapproved command vector: {operation}")
        if record.get("execution_outcome") not in EXECUTION_OUTCOMES:
            problems.append(f"invalid execution outcome: {operation}")
        if record.get("parsing_outcome") not in PARSING_OUTCOMES:
            problems.append(f"invalid parsing outcome: {operation}")
        if record.get("failure_classification") not in {
            "not_attempted", "none", "connection_or_authentication_failure",
            "environment_or_cli_unavailable", "command_failed",
        }:
            problems.append(f"invalid failure classification: {operation}")
        if record.get("artifact") != ARTIFACT_NAMES[operation]:
            problems.append(f"invalid artifact association: {operation}")
        if record.get("execution_outcome") == "skipped" and record.get("parsing_outcome") != "not_parsed":
            problems.append(f"skipped operation was parsed: {operation}")
        for size_name in ("stdout_size_bytes", "stderr_size_bytes", "accepted_records", "rejected_records"):
            value = record.get(size_name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                problems.append(f"invalid {size_name}: {operation}")
        for present_name, size_name in (("stdout_present", "stdout_size_bytes"), ("stderr_present", "stderr_size_bytes")):
            size_value = record.get(size_name)
            if (
                not isinstance(record.get(present_name), bool)
                or not isinstance(size_value, int) or isinstance(size_value, bool)
                or record[present_name] != (size_value > 0)
            ):
                problems.append(f"inconsistent output presence: {operation}")
        if record.get("exit_status") is not None and (not isinstance(record["exit_status"], int) or isinstance(record["exit_status"], bool)):
            problems.append(f"invalid exit status: {operation}")
        if record.get("execution_outcome") == "succeeded" and record.get("exit_status") != 0:
            problems.append(f"successful operation has nonzero exit: {operation}")
        if record.get("execution_outcome") == "skipped" and record.get("exit_status") is not None:
            problems.append(f"skipped operation has exit status: {operation}")
        for time_name in ("start_timestamp_utc", "end_timestamp_utc"):
            value = record.get(time_name)
            if record.get("execution_outcome") == "skipped":
                if value is not None:
                    problems.append(f"skipped operation has timestamp: {operation}")
            elif not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?Z", value):
                problems.append(f"invalid operation timestamp: {operation}")
    capture_is_successful = bool(records) and all(
        isinstance(record, dict)
        and record.get("execution_outcome") == "succeeded"
        and record.get("parsing_outcome") in {"recognized_records", "successful_empty_output", "recognized_empty_json_collection"}
        for record in records
    )
    if manifest.get("capture_status") != ("successful_capture" if capture_is_successful else "partial"):
        problems.append("capture status does not match operation outcomes")

    expected = {ARTIFACT_NAMES[operation] for operation in selected}
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != expected:
        problems.append("artifact declarations do not match selected operations")
        artifacts = artifacts if isinstance(artifacts, dict) else {}
    for name, record in artifacts.items():
        if name not in expected or not isinstance(record, dict):
            problems.append(f"invalid artifact declaration: {name}")
            continue
        expected_type = "informational metadata" if name == ARTIFACT_NAMES["metadata"] else "read-only observation"
        artifact_fields = {"type", "capture_status", "size_bytes", "sha256", "coverage_limitations", "recovery_classification"}
        if set(record) != artifact_fields or record.get("type") != expected_type:
            problems.append(f"invalid artifact fields: {name}")
        if record.get("capture_status") not in PARSING_OUTCOMES:
            problems.append(f"invalid artifact capture status: {name}")
        operation_for_artifact = next((op for op, artifact in ARTIFACT_NAMES.items() if artifact == name), None)
        operation_record = next((item for item in records if isinstance(item, dict) and item.get("operation") == operation_for_artifact), None)
        if operation_record and record.get("capture_status") != operation_record.get("parsing_outcome"):
            problems.append(f"artifact status does not match operation: {name}")
        if record.get("recovery_classification") != RESTORE_CLASSIFICATION:
            problems.append(f"invalid artifact recovery classification: {name}")
        if not isinstance(record.get("coverage_limitations"), list) or not all(isinstance(item, str) for item in record.get("coverage_limitations", [])):
            problems.append(f"invalid artifact coverage limitations: {name}")
        if not isinstance(record.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            problems.append(f"invalid checksum declaration: {name}")
        if not isinstance(record.get("size_bytes"), int) or isinstance(record.get("size_bytes"), bool) or record["size_bytes"] < 0:
            problems.append(f"invalid artifact size: {name}")
        path = snapshot / name
        try:
            if path.is_symlink() or not path.is_file():
                problems.append(f"artifact missing or not a regular file: {name}")
                continue
            if path.stat().st_mode & 0o177:
                problems.append(f"artifact permissions are broader than 0600: {name}")
            if path.stat().st_size != record.get("size_bytes"):
                problems.append(f"file size mismatch: {name}")
            if sha256_file(path) != record.get("sha256"):
                problems.append(f"checksum mismatch: {name}")
            content = json.loads(path.read_text(encoding="utf-8"))
            if name == ARTIFACT_NAMES["metadata"]:
                if not isinstance(content, dict) or set(content) != {"fields", "missing_fields", "capture_status", "record_counts"}:
                    problems.append(f"invalid metadata artifact: {name}")
                elif not isinstance(content["fields"], dict) or set(content["fields"]) - METADATA_ALLOWLIST or not all(_safe_metadata_value(value) for value in content["fields"].values()):
                    problems.append(f"metadata artifact contains disallowed fields: {name}")
                if isinstance(content, dict):
                    if not isinstance(content.get("missing_fields"), list) or any(field not in METADATA_ALLOWLIST for field in content["missing_fields"]):
                        problems.append(f"metadata artifact has invalid missing fields: {name}")
                    counts = content.get("record_counts")
                    if not isinstance(counts, dict) or set(counts) != {"accepted", "rejected"} or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts.values()):
                        problems.append(f"metadata artifact has invalid record counts: {name}")
                    if operation_record and content.get("capture_status") != operation_record.get("parsing_outcome"):
                        problems.append(f"metadata artifact status mismatch: {name}")
            else:
                if not isinstance(content, dict) or set(content) != {"application_ids", "capture_status", "record_counts"}:
                    problems.append(f"invalid applications artifact: {name}")
                elif not isinstance(content["application_ids"], list) or any(not _valid_app_id(app_id) for app_id in content["application_ids"]):
                    problems.append(f"application artifact contains disallowed records: {name}")
                if isinstance(content, dict):
                    ids = content.get("application_ids")
                    if isinstance(ids, list) and len(ids) != len(set(item for item in ids if isinstance(item, str))):
                        problems.append(f"application artifact contains duplicate records: {name}")
                    counts = content.get("record_counts")
                    if (
                        not isinstance(counts, dict) or set(counts) != {"accepted", "rejected", "total"}
                        or not isinstance(counts.get("accepted"), int) or isinstance(counts.get("accepted"), bool)
                        or counts.get("accepted") != (len(ids) if isinstance(ids, list) else -1)
                        or not isinstance(counts.get("rejected"), int) or isinstance(counts.get("rejected"), bool)
                        or counts.get("rejected") < 0
                        or (counts.get("total") is not None and (not isinstance(counts.get("total"), int) or isinstance(counts.get("total"), bool) or counts.get("total") < 0))
                    ):
                        problems.append(f"application artifact has invalid record counts: {name}")
                    if operation_record and content.get("capture_status") != operation_record.get("parsing_outcome"):
                        problems.append(f"application artifact status mismatch: {name}")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            problems.append(f"cannot validate artifact {name}: {type(exc).__name__}")
    try:
        present = {entry.name for entry in snapshot.iterdir()}
        allowed_files = expected | {"manifest.json"}
        if present != allowed_files:
            problems.append("snapshot files do not match declared artifacts")
    except OSError:
        problems.append("cannot inspect snapshot directory")
    for path, mask, message in ((manifest_path, 0o177, "manifest permissions are broader than 0600"), (snapshot, 0o077, "snapshot directory permissions are broader than 0700")):
        try:
            if path.stat().st_mode & mask:
                problems.append(message)
        except OSError:
            problems.append("cannot inspect snapshot permissions")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-alias", required=True)
    parser.add_argument("--operation", action="append", choices=OPERATIONS, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        snapshot = create_live_snapshot(args.output_root, args.device_alias, args.operation)
        print(snapshot)
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        return 0 if manifest["capture_status"] == "successful_capture" else 1
    except (InventoryError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
