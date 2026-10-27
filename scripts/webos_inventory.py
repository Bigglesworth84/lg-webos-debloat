#!/usr/bin/env python3
"""Offline fixture snapshot and local validation utilities for webOS inventory.

The separate webos_live_capture.py adapter supervises a tightly allowlisted
read-only capture. This module retains the offline fixture interface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_NAME = "webos-inventory-foundation"
TOOL_VERSION = "0.1.0"
DEVICE_OPERATIONS = {
    "metadata": ("ares-device", "--system-info", "--device"),
    "applications": ("ares-install", "--device", "--list"),
    "applications-full": ("ares-install", "--device", "--listfull"),
}
RESTORE_CLASSIFICATION = "recovery unverified / irreversible"
SENSITIVE_KEY = re.compile(
    r"(?:serial|token|password|passphrase|secret|credential|authorization|"
    r"private.?key|account|email|mac(?:address)?|ip(?:address)?|hostname)",
    re.IGNORECASE,
)
SENSITIVE_TEXT = re.compile(
    r"(?im)(\b(?:serial(?:number)?|token|password|passphrase|secret|"
    r"authorization|private.?key|account|email|mac(?:address)?|"
    r"ip(?:address)?|hostname)\b\s*[:=]\s*)([^\r\n,;]+)"
)
METADATA_FIELDS = ("modelName", "sdkVersion", "firmwareVersion", "boardType", "otaId")
ALIAS_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")


class InventoryError(ValueError):
    """Invalid input, output, or snapshot data."""


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def validate_alias(alias: str) -> str:
    if not ALIAS_RE.fullmatch(alias):
        raise InventoryError("Device alias must be an explicit simple name (letters, digits, '_' or '-').")
    return alias


def command_argv(operation: str, device_alias: str) -> tuple[str, ...]:
    """Build an approved argv vector; never executes it or accepts a command string."""
    alias = validate_alias(device_alias)
    try:
        template = DEVICE_OPERATIONS[operation]
    except KeyError as exc:
        raise InventoryError(f"Unsupported operation: {operation}") from exc
    if operation == "metadata":
        return (*template, alias)
    return (template[0], template[1], alias, template[2])


def redact_text(text: str) -> str:
    return SENSITIVE_TEXT.sub(r"\1[REDACTED]", text)


def redact_value(value: Any, key: str = "") -> Any:
    if SENSITIVE_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): redact_value(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(item, key) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def parse_device_metadata(text: str) -> tuple[dict[str, str], list[str]]:
    """Parse the key/value format documented by LG's ares-device output."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if key in METADATA_FIELDS and value:
            found[key] = redact_text(value)
    missing = [key for key in METADATA_FIELDS if key not in found]
    return found, missing


def parse_applications(text: str) -> tuple[list[dict[str, Any]], str, dict[str, int | None]]:
    """Parse app records and return their status and determinable record counts.

    Returned records are observations only; this parser never infers removability.
    """
    stripped = text.strip()
    if not stripped:
        return [], "unexpected", {"accepted": 0, "rejected": 0, "total": None}
    try:
        decoded = json.loads(stripped)
    except json.JSONDecodeError:
        decoded = None
    if isinstance(decoded, list):
        items = decoded
    elif isinstance(decoded, dict) and isinstance(decoded.get("applications"), list):
        items = decoded["applications"]
    elif isinstance(decoded, dict) and isinstance(decoded.get("apps"), list):
        items = decoded["apps"]
    else:
        items = None
    if items is not None:
        clean: list[dict[str, Any]] = []
        seen: set[str] = set()
        rejected = 0
        for item in items:
            if isinstance(item, str):
                app_id = item.strip()
                sanitized = {"id": redact_text(app_id)}
            elif isinstance(item, dict):
                sanitized = redact_value(item)
                sanitized = {k: v for k, v in sanitized.items() if not re.search(r"remove|uninstall", str(k), re.IGNORECASE)}
                app_id = next((sanitized.get(k) for k in ("id", "appId", "app_id") if k in sanitized), None)
            else:
                rejected += 1
                continue
            if not isinstance(app_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,127}", app_id):
                rejected += 1
                continue
            if app_id in seen:
                rejected += 1
                continue
            seen.add(app_id)
            clean.append(sanitized)
        return clean, "partial" if rejected else "parsed", {
            "accepted": len(clean), "rejected": rejected, "total": len(items)
        }

    # A JSON-looking response that failed to decode must not be reinterpreted as
    # a loose table; malformed/truncated JSON has no trustworthy record count.
    if stripped.startswith(("[", "{")):
        return [], "unexpected", {"accepted": 0, "rejected": 0, "total": None}

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    rejected = 0
    for line in stripped.splitlines():
        row = line.strip()
        if not row or set(row) <= set("-+| "):
            continue
        if re.search(r"\b(?:id|app.?id|application)\b", row, re.IGNORECASE) and not re.search(r"\.[a-z0-9_.-]+", row):
            continue
        candidate = re.split(r"\s{2,}|\|", row)[0].strip()
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,127}", candidate) and "." in candidate:
            if candidate in seen:
                rejected += 1
            else:
                seen.add(candidate)
                rows.append({"id": candidate})
        else:
            rejected += 1
    # Text tables have no reliable declared total; count only record-like lines.
    total = len(rows) + rejected
    return rows, ("partial" if rows and rejected else "parsed" if rows else "unexpected"), {
        "accepted": len(rows), "rejected": rejected, "total": total if total else None
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def secure_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=False)


def prepare_output_root(path: Path) -> None:
    """Create or validate a private, owner-controlled root without chmodding it."""
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise InventoryError("Snapshot output path must not contain symbolic links.")
    if not absolute.exists():
        absolute.mkdir(mode=0o700, parents=True, exist_ok=False)
    if absolute.is_symlink() or not absolute.is_dir():
        raise InventoryError("Snapshot output root must be a regular directory.")
    info = absolute.stat()
    mode = info.st_mode & 0o777
    if info.st_uid != os.getuid() or mode & 0o077 or mode & 0o300 != 0o300:
        raise InventoryError("Snapshot output root must be owned by the current user, owner-writable, and private (no group/other access).")


def secure_write(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def serialize_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def create_fixture_snapshot(
    output_root: Path,
    device_alias: str,
    metadata_text: str | None,
    apps_text: str | None,
    cli_version: str,
    runtime_version: str,
    captured_at: str | None = None,
) -> Path:
    alias = validate_alias(device_alias)
    stamp = captured_at or utc_timestamp()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", stamp):
        raise InventoryError("Capture timestamp must be UTC in YYYY-MM-DDTHH:MM:SSZ form.")
    try:
        datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise InventoryError("Capture timestamp is not a valid UTC date/time.") from exc
    if not cli_version.strip() or not runtime_version.strip():
        raise InventoryError("CLI and runtime versions are required.")
    prepare_output_root(output_root)
    snapshot = output_root / stamp.replace(":", "-")
    secure_directory(snapshot)

    metadata, missing_fields = parse_device_metadata(metadata_text or "")
    applications, app_status, app_counts = parse_applications(apps_text or "")
    artifacts: dict[str, dict[str, Any]] = {}

    metadata_bytes = serialize_json({"fields": metadata, "missing_fields": missing_fields})
    secure_write(snapshot / "device-metadata.json", metadata_bytes)
    artifacts["device-metadata.json"] = {
        "type": "informational metadata",
        "capture_status": "unavailable" if metadata_text is None else ("partial" if missing_fields else "complete"),
        "coverage_limitations": ["Only documented CLI metadata fields are represented."]
        + (["Metadata capture failed or was unavailable; no raw diagnostic was included."] if metadata_text is None else []),
        "recovery_classification": RESTORE_CLASSIFICATION,
        "sha256": hashlib.sha256(metadata_bytes).hexdigest(),
        "size_bytes": len(metadata_bytes),
    }

    apps_bytes = serialize_json({"applications": applications, "parse_status": app_status, "record_counts": app_counts})
    secure_write(snapshot / "applications.json", apps_bytes)
    artifacts["applications.json"] = {
        "type": "read-only observation",
        "capture_status": "unavailable" if apps_text is None else app_status,
        "coverage_limitations": [
            "The installed-app listing may omit system components or other device state.",
            "Application inventory is not a restorable backup and does not establish removability.",
        ] + (["Application capture failed or was unavailable; no raw diagnostic was included."] if apps_text is None else []),
        "recovery_classification": RESTORE_CLASSIFICATION,
        "sha256": hashlib.sha256(apps_bytes).hexdigest(),
        "size_bytes": len(apps_bytes),
    }

    partial = metadata_text is None or apps_text is None or bool(missing_fields) or app_status != "parsed"
    manifest = {
        "schema_version": 1,
        "capture_timestamp_utc": stamp,
        "capture_mode": "offline-fixture",
        "device_alias": alias,
        "device_identity": {"cli_model_name": metadata.get("modelName"), "cli_firmware_version": metadata.get("firmwareVersion")},
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "cli_version": cli_version.strip()},
        "runtime": {"node_version": runtime_version.strip()},
        "capture_status": "partial" if partial else "complete",
        "coverage_limitations": [
            "No television was contacted by this offline fixture capture.",
            "No restorable TV-state artifact is currently verified.",
            "Developer Mode inventory does not constitute a complete system backup.",
        ],
        "restorable_artifacts": [],
        "recovery_classification": RESTORE_CLASSIFICATION,
        "artifacts": artifacts,
    }
    secure_write(snapshot / "manifest.json", serialize_json(manifest))
    return snapshot


def validate_snapshot(snapshot: Path) -> list[str]:
    problems: list[str] = []
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise InventoryError("Snapshot path must be a regular directory.")
    manifest_path = snapshot / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InventoryError("Snapshot manifest must be a regular file.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InventoryError(f"Cannot read snapshot manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise InventoryError("Snapshot manifest must be a JSON object.")
    if manifest.get("schema_version") == 2:
        try:
            from .webos_live_capture import validate_live_snapshot
        except ImportError:
            from webos_live_capture import validate_live_snapshot

        return validate_live_snapshot(snapshot, manifest)
    if manifest.get("schema_version") != 1:
        return ["unsupported manifest schema"]
    required_fields = {
        "schema_version", "capture_timestamp_utc", "capture_mode", "device_alias",
        "device_identity", "tool", "runtime", "capture_status", "coverage_limitations",
        "restorable_artifacts", "recovery_classification", "artifacts",
    }
    missing_fields = required_fields - manifest.keys()
    if missing_fields:
        problems.append(f"missing required manifest fields: {', '.join(sorted(missing_fields))}")
    unexpected_fields = manifest.keys() - required_fields
    if unexpected_fields:
        problems.append(f"unsupported manifest fields: {', '.join(sorted(unexpected_fields))}")
    if manifest.get("capture_mode") != "offline-fixture":
        problems.append("unsupported capture mode")
    if manifest.get("capture_status") not in {"complete", "partial"}:
        problems.append("invalid capture status")
    stamp = manifest.get("capture_timestamp_utc")
    if not isinstance(stamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", stamp):
        problems.append("invalid capture timestamp")
    else:
        try:
            datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            problems.append("invalid capture timestamp")
    try:
        validate_alias(manifest.get("device_alias"))
    except (InventoryError, TypeError):
        problems.append("invalid device alias")
    if manifest.get("device_identity") is not None and (
        not isinstance(manifest.get("device_identity"), dict)
        or set(manifest["device_identity"]) != {"cli_model_name", "cli_firmware_version"}
        or not all(value is None or isinstance(value, str) for value in manifest["device_identity"].values())
    ):
        problems.append("invalid device identity fields")
    tool = manifest.get("tool")
    runtime = manifest.get("runtime")
    if not isinstance(tool, dict) or set(tool) != {"name", "version", "cli_version"} or not all(isinstance(value, str) and value for value in tool.values()):
        problems.append("invalid tool fields")
    if not isinstance(runtime, dict) or set(runtime) != {"node_version"} or not isinstance(runtime.get("node_version"), str) or not runtime["node_version"]:
        problems.append("invalid runtime fields")
    if not isinstance(manifest.get("device_identity"), dict):
        problems.append("invalid device identity, tool, or runtime fields")
    if not isinstance(manifest.get("coverage_limitations"), list) or not all(isinstance(x, str) for x in manifest.get("coverage_limitations", [])):
        problems.append("invalid coverage limitations")
    if manifest.get("recovery_classification") != RESTORE_CLASSIFICATION:
        problems.append("unsupported recovery classification")
    if manifest.get("restorable_artifacts") != []:
        problems.append("manifest claims unverified restorable artifacts")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        return problems + ["manifest artifacts must be an object"]
    required_artifacts = {"device-metadata.json", "applications.json"}
    declared = set(artifacts)
    if not required_artifacts <= declared:
        problems.append(f"missing required artifact declarations: {', '.join(sorted(required_artifacts - declared))}")
    if declared - required_artifacts:
        problems.append(f"unexpected artifact declarations: {', '.join(sorted(str(x) for x in declared - required_artifacts))}")
    expected_types = {"device-metadata.json": "informational metadata", "applications.json": "read-only observation"}
    expected_capture_statuses = {
        "device-metadata.json": {"complete", "partial", "unavailable"},
        "applications.json": {"parsed", "partial", "unexpected", "unavailable"},
    }
    artifact_statuses: dict[str, Any] = {}
    for name, record in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name or name in ("", ".", ".."):
            problems.append(f"unsafe artifact path: {name!r}")
            continue
        if not isinstance(record, dict):
            problems.append(f"invalid artifact record: {name}")
            continue
        if record.get("type") != expected_types.get(name):
            problems.append(f"unsupported artifact type: {name}")
        record_fields = {"type", "capture_status", "coverage_limitations", "recovery_classification", "sha256", "size_bytes"}
        if set(record) != record_fields:
            problems.append(f"invalid artifact fields: {name}")
        if record.get("recovery_classification") != RESTORE_CLASSIFICATION:
            problems.append(f"unsupported artifact recovery classification: {name}")
        if record.get("capture_status") not in {"complete", "partial", "unexpected", "unavailable", "parsed"}:
            problems.append(f"invalid artifact capture status: {name}")
        if record.get("capture_status") not in expected_capture_statuses.get(name, set()):
            problems.append(f"unsupported artifact capture status: {name}")
        artifact_statuses[name] = record.get("capture_status")
        if not isinstance(record.get("coverage_limitations"), list) or not all(isinstance(x, str) for x in record.get("coverage_limitations", [])):
            problems.append(f"invalid artifact coverage limitations: {name}")
        checksum = record.get("sha256")
        size_bytes = record.get("size_bytes")
        if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            problems.append(f"invalid checksum declaration: {name}")
        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes < 0:
            problems.append(f"invalid file size declaration: {name}")
        path = snapshot / name
        try:
            if path.is_symlink() or not path.is_file():
                problems.append(f"artifact missing or not a regular file: {name}")
                continue
            actual = sha256_file(path)
            if isinstance(checksum, str) and actual != checksum:
                problems.append(f"checksum mismatch: {name}")
            if isinstance(size_bytes, int) and path.stat().st_size != size_bytes:
                problems.append(f"file size mismatch: {name}")
            if path.stat().st_mode & 0o177:
                problems.append(f"artifact permissions are broader than 0600: {name}")
        except OSError as exc:
            problems.append(f"cannot inspect artifact {name}: {exc}")
    if manifest.get("capture_status") == "complete" and artifact_statuses != {
        "device-metadata.json": "complete", "applications.json": "parsed"
    }:
        problems.append("complete manifest has incomplete or unavailable artifacts")
    expected_files = required_artifacts | {"manifest.json"}
    try:
        present = {entry.name for entry in snapshot.iterdir()}
        if present - expected_files:
            problems.append(f"unexpected snapshot files: {', '.join(sorted(present - expected_files))}")
        if expected_files - present:
            problems.append(f"missing snapshot files: {', '.join(sorted(expected_files - present))}")
    except OSError as exc:
        problems.append(f"cannot inspect snapshot directory: {exc}")
    try:
        if manifest_path.stat().st_mode & 0o177:
            problems.append("manifest permissions are broader than 0600")
    except OSError as exc:
        problems.append(f"cannot inspect manifest permissions: {exc}")
    try:
        if snapshot.stat().st_mode & 0o077:
            problems.append("snapshot directory permissions are broader than 0700")
    except OSError as exc:
        problems.append(f"cannot inspect snapshot directory permissions: {exc}")
    return problems


def _read_fixture(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise InventoryError(f"Fixture must be a regular file: {path}")
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    capture = subparsers.add_parser("capture-fixtures", help="Create an offline fixture snapshot; never contacts a device.")
    capture.add_argument("--device-alias", required=True)
    capture.add_argument("--metadata-fixture", type=Path)
    capture.add_argument("--apps-fixture", type=Path)
    capture.add_argument("--metadata-unavailable", action="store_true")
    capture.add_argument("--apps-unavailable", action="store_true")
    capture.add_argument("--cli-version", required=True)
    capture.add_argument("--runtime-version", required=True)
    capture.add_argument("--output-root", type=Path, required=True)
    validate = subparsers.add_parser("validate", help="Validate a local snapshot and checksums.")
    validate.add_argument("snapshot", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "capture-fixtures":
            if args.metadata_unavailable == (args.metadata_fixture is not None):
                raise InventoryError("Provide exactly one of --metadata-fixture or --metadata-unavailable.")
            if args.apps_unavailable == (args.apps_fixture is not None):
                raise InventoryError("Provide exactly one of --apps-fixture or --apps-unavailable.")
            snapshot = create_fixture_snapshot(
                args.output_root,
                args.device_alias,
                None if args.metadata_unavailable else _read_fixture(args.metadata_fixture),
                None if args.apps_unavailable else _read_fixture(args.apps_fixture),
                args.cli_version,
                args.runtime_version,
            )
            print(snapshot)
            return 0
        problems = validate_snapshot(args.snapshot)
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            return 1
        print("snapshot integrity valid")
        return 0
    except (InventoryError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
