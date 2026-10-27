#!/usr/bin/env python3
"""Offline-only webOS inventory fixture and snapshot utility.

This module deliberately has no device command executor. It can document the
approved future command vectors, ingest sanitized fixtures, and validate
local snapshot manifests without opening a network connection.
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


def parse_applications(text: str) -> tuple[list[dict[str, Any]], str]:
    """Parse JSON or a conservative line/table representation; preserve unknown output as opaque."""
    stripped = text.strip()
    if not stripped:
        return [], "unexpected"
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
        for item in items:
            if isinstance(item, str):
                clean.append({"id": redact_text(item)})
            elif isinstance(item, dict):
                sanitized = redact_value(item)
                if any(k in sanitized for k in ("id", "appId", "app_id")):
                    clean.append(sanitized)
        return clean, "parsed" if clean or not items else "partial"

    rows: list[dict[str, Any]] = []
    for line in stripped.splitlines():
        row = line.strip()
        if not row or set(row) <= set("-+| "):
            continue
        if re.search(r"\b(?:id|app.?id|application)\b", row, re.IGNORECASE) and not re.search(r"\.[a-z0-9_.-]+", row):
            continue
        candidate = re.split(r"\s{2,}|\|", row)[0].strip()
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,127}", candidate) and "." in candidate:
            rows.append({"id": candidate})
    return rows, "parsed" if rows else "unexpected"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def secure_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    path.chmod(0o700)


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
    path.chmod(0o600)


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
    if output_root.is_symlink():
        raise InventoryError("Snapshot output root must not be a symbolic link.")
    output_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not output_root.is_dir():
        raise InventoryError("Snapshot output root must be a directory.")
    output_root.chmod(0o700)
    snapshot = output_root / stamp.replace(":", "-")
    secure_directory(snapshot)

    metadata, missing_fields = parse_device_metadata(metadata_text or "")
    applications, app_status = parse_applications(apps_text or "")
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

    apps_bytes = serialize_json({"applications": applications, "parse_status": app_status})
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
        "device_identity": {"model": metadata.get("modelName"), "firmware": metadata.get("firmwareVersion")},
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
    if manifest.get("schema_version") != 1:
        problems.append("unsupported manifest schema")
    if manifest.get("restorable_artifacts") != []:
        problems.append("manifest claims unverified restorable artifacts")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise InventoryError("Manifest artifacts must be an object.")
    for name, record in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name or name in ("", ".", ".."):
            problems.append(f"unsafe artifact path: {name!r}")
            continue
        if not isinstance(record, dict):
            problems.append(f"invalid artifact record: {name}")
            continue
        if record.get("type") not in {"read-only observation", "informational metadata", "supported restorable backup"}:
            problems.append(f"unsupported artifact type: {name}")
        if record.get("type") == "supported restorable backup":
            problems.append(f"unsupported restore request/artifact claim: {name}")
        path = snapshot / name
        try:
            if path.is_symlink() or not path.is_file():
                problems.append(f"artifact missing or not a regular file: {name}")
                continue
            actual = sha256_file(path)
            if actual != record.get("sha256"):
                problems.append(f"checksum mismatch: {name}")
            if path.stat().st_mode & 0o077:
                problems.append(f"artifact permissions are broader than 0600: {name}")
        except OSError as exc:
            problems.append(f"cannot inspect artifact {name}: {exc}")
    try:
        if manifest_path.stat().st_mode & 0o077:
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
