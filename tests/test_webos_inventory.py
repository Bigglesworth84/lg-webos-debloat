import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from scripts.webos_inventory import (
    InventoryError,
    command_argv,
    create_fixture_snapshot,
    parse_applications,
    parse_device_metadata,
    redact_value,
    validate_snapshot,
)


class InventoryParsingTests(unittest.TestCase):
    def test_parses_documented_metadata_fields(self):
        data, missing = parse_device_metadata(
            "modelName : WEBOS6.0\nsdkVersion : 6.1.0\nfirmwareVersion : 03.53.45\n"
            "boardType : K7LP_EU\notaId : HE_DTV_W21P_EU\n"
        )
        self.assertEqual(data["firmwareVersion"], "03.53.45")
        self.assertEqual(missing, [])

    def test_missing_metadata_is_reported_without_failure(self):
        data, missing = parse_device_metadata("modelName : WEBOS6.0\n")
        self.assertEqual(data, {"modelName": "WEBOS6.0"})
        self.assertIn("firmwareVersion", missing)

    def test_unexpected_metadata_output_has_no_guessed_fields(self):
        self.assertEqual(parse_device_metadata("permission denied\n"), ({}, list(("modelName", "sdkVersion", "firmwareVersion", "boardType", "otaId"))))

    def test_parses_json_application_output(self):
        apps, status = parse_applications('[{"id":"com.example.app","title":"Demo"}]')
        self.assertEqual(status, "parsed")
        self.assertEqual(apps[0]["id"], "com.example.app")

    def test_parses_simple_application_id_rows(self):
        apps, status = parse_applications("ID\n-------------------\ncom.example.app\n")
        self.assertEqual(status, "parsed")
        self.assertEqual(apps, [{"id": "com.example.app"}])

    def test_unrecognized_application_output_is_marked_unexpected(self):
        self.assertEqual(parse_applications("permission denied"), ([], "unexpected"))

    def test_redacts_sensitive_named_fields_and_key_value_text(self):
        clean = redact_value({"modelName": "WEBOS6.0", "serialNumber": "secret-serial", "nested": "token: abc"})
        self.assertEqual(clean["serialNumber"], "[REDACTED]")
        self.assertEqual(clean["nested"], "token: [REDACTED]")


class CommandPolicyTests(unittest.TestCase):
    def test_builds_only_approved_command_vectors(self):
        self.assertEqual(command_argv("metadata", "tv"), ("ares-device", "--system-info", "--device", "tv"))
        self.assertEqual(command_argv("applications", "tv"), ("ares-install", "--device", "tv", "--list"))
        self.assertEqual(command_argv("applications-full", "tv"), ("ares-install", "--device", "tv", "--listfull"))

    def test_rejects_unapproved_mutation_or_arbitrary_command(self):
        for operation in ("install", "remove", "launch", "shell", "renew", "scan", "restore", "firmware"):
            with self.subTest(operation=operation), self.assertRaises(InventoryError):
                command_argv(operation, "tv")
        with self.assertRaises(InventoryError):
            command_argv("metadata", "tv; touch /tmp/nope")


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def make_snapshot(self, apps_text='[{"id":"com.example.app"}]'):
        return create_fixture_snapshot(
            self.root / "backups",
            "tv",
            "modelName : WEBOS6.0\nsdkVersion : 6.1.0\nfirmwareVersion : 03.53.45\nboardType : EU\notaId : EU\n",
            apps_text,
            "3.2.6",
            "v24.11.1",
            "2026-10-27T12:00:00Z",
        )

    def test_creates_timestamped_private_manifest_with_hashes(self):
        snapshot = self.make_snapshot()
        manifest = json.loads((snapshot / "manifest.json").read_text())
        self.assertEqual(manifest["capture_timestamp_utc"], "2026-10-27T12:00:00Z")
        self.assertEqual(manifest["restorable_artifacts"], [])
        self.assertEqual(manifest["artifacts"]["applications.json"]["type"], "read-only observation")
        self.assertEqual(manifest["artifacts"]["device-metadata.json"]["type"], "informational metadata")
        self.assertEqual(validate_snapshot(snapshot), [])
        self.assertEqual(stat.S_IMODE(snapshot.stat().st_mode), 0o700)
        for path in snapshot.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_partial_capture_is_manifested(self):
        snapshot = create_fixture_snapshot(
            self.root / "partial", "tv", "modelName : WEBOS6.0\n", "unexpected output", "3.2.6", "v24.11.1",
            "2026-10-27T12:00:00Z",
        )
        manifest = json.loads((snapshot / "manifest.json").read_text())
        self.assertEqual(manifest["capture_status"], "partial")
        self.assertEqual(manifest["artifacts"]["applications.json"]["capture_status"], "unexpected")

    def test_partial_capture_failure_is_recorded_without_raw_diagnostics(self):
        snapshot = create_fixture_snapshot(
            self.root / "capture-failure", "tv", None, '[{"id":"com.example.app"}]', "3.2.6", "v24.11.1",
            "2026-10-27T12:00:00Z",
        )
        manifest = json.loads((snapshot / "manifest.json").read_text())
        self.assertEqual(manifest["capture_status"], "partial")
        metadata_record = manifest["artifacts"]["device-metadata.json"]
        self.assertEqual(metadata_record["capture_status"], "unavailable")
        self.assertFalse(any("diagnostic" in path.name for path in snapshot.iterdir()))

    def test_checksum_tampering_is_detected(self):
        snapshot = self.make_snapshot()
        (snapshot / "applications.json").write_text("tampered\n")
        self.assertIn("checksum mismatch: applications.json", validate_snapshot(snapshot))

    def test_unexpected_restore_claim_is_rejected(self):
        snapshot = self.make_snapshot()
        manifest_path = snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["restorable_artifacts"] = ["applications.json"]
        manifest_path.write_text(json.dumps(manifest))
        os.chmod(manifest_path, 0o600)
        self.assertTrue(any("unverified restorable" in problem for problem in validate_snapshot(snapshot)))

    def test_timestamp_and_alias_are_validated(self):
        with self.assertRaises(InventoryError):
            create_fixture_snapshot(self.root / "bad-time", "tv", "", "", "3.2.6", "v24", "not-utc")
        with self.assertRaises(InventoryError):
            create_fixture_snapshot(self.root / "bad-alias", "tv;id", "", "", "3.2.6", "v24", "2026-10-27T12:00:00Z")
        with self.assertRaises(InventoryError):
            create_fixture_snapshot(self.root / "bad-date", "tv", "", "", "3.2.6", "v24", "2026-99-27T12:00:00Z")

    def test_symlinked_manifest_is_rejected(self):
        snapshot = self.make_snapshot()
        manifest_path = snapshot / "manifest.json"
        outside = self.root / "outside.json"
        outside.write_text(manifest_path.read_text())
        manifest_path.unlink()
        manifest_path.symlink_to(outside)
        with self.assertRaises(InventoryError):
            validate_snapshot(snapshot)

    def test_non_object_manifest_is_rejected(self):
        snapshot = self.make_snapshot()
        (snapshot / "manifest.json").write_text("[]\n")
        with self.assertRaises(InventoryError):
            validate_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
