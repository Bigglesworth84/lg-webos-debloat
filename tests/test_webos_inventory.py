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
        self.assertEqual(set(data), {"modelName", "sdkVersion", "firmwareVersion", "boardType"})
        self.assertNotIn("otaId", data)
        self.assertEqual(missing, [])

    def test_missing_metadata_is_reported_without_failure(self):
        data, missing = parse_device_metadata("modelName : WEBOS6.0\n")
        self.assertEqual(data, {"modelName": "WEBOS6.0"})
        self.assertIn("firmwareVersion", missing)

    def test_unexpected_metadata_output_has_no_guessed_fields(self):
        self.assertEqual(parse_device_metadata("permission denied\n"), ({}, list(("modelName", "sdkVersion", "firmwareVersion", "boardType"))))

    def test_parses_json_application_output(self):
        apps, status, counts = parse_applications('[{"id":"com.example.app","title":"Demo"}]')
        self.assertEqual(status, "parsed")
        self.assertEqual(apps[0]["id"], "com.example.app")
        self.assertEqual(counts, {"accepted": 1, "rejected": 0, "total": 1})

    def test_mixed_valid_and_invalid_json_records_are_partial(self):
        apps, status, counts = parse_applications('[{"id":"com.example.good"},{"title":"missing id"},null]')
        self.assertEqual(status, "partial")
        self.assertEqual([item["id"] for item in apps], ["com.example.good"])
        self.assertEqual(counts, {"accepted": 1, "rejected": 2, "total": 3})

    def test_empty_json_array_is_a_complete_empty_inventory(self):
        self.assertEqual(parse_applications("[]"), ([], "parsed", {"accepted": 0, "rejected": 0, "total": 0}))

    def test_unsupported_json_structure_is_unexpected(self):
        self.assertEqual(parse_applications('{"result":[]}'), ([], "unexpected", {"accepted": 0, "rejected": 0, "total": None}))

    def test_duplicate_json_application_ids_are_rejected(self):
        apps, status, counts = parse_applications('[{"id":"com.example.app"},{"id":"com.example.app"}]')
        self.assertEqual(len(apps), 1)
        self.assertEqual(status, "partial")
        self.assertEqual(counts, {"accepted": 1, "rejected": 1, "total": 2})

    def test_unexpected_text_and_truncated_json_are_not_parsed_as_records(self):
        self.assertEqual(parse_applications("permission denied"), ([], "unexpected", {"accepted": 0, "rejected": 1, "total": 1}))
        self.assertEqual(parse_applications('[{"id":"com.example.app"}'), ([], "unexpected", {"accepted": 0, "rejected": 0, "total": None}))

    def test_parses_simple_application_id_rows(self):
        apps, status, counts = parse_applications("ID\n-------------------\ncom.example.app\n")
        self.assertEqual(status, "parsed")
        self.assertEqual(apps, [{"id": "com.example.app"}])
        self.assertEqual(counts["accepted"], 1)

    def test_duplicate_text_application_ids_are_rejected(self):
        apps, status, counts = parse_applications("com.example.app\ncom.example.app\n")
        self.assertEqual(apps, [{"id": "com.example.app"}])
        self.assertEqual(status, "partial")
        self.assertEqual(counts, {"accepted": 1, "rejected": 1, "total": 2})

    def test_unrecognized_application_output_is_marked_unexpected(self):
        self.assertEqual(parse_applications("permission denied")[1], "unexpected")

    def test_redacts_sensitive_named_fields_and_key_value_text(self):
        clean = redact_value({"modelName": "WEBOS6.0", "serialNumber": "secret-serial", "nested": {"auth": {"accessToken": "abc", "note": "token: xyz"}}})
        self.assertEqual(clean["serialNumber"], "[REDACTED]")
        self.assertEqual(clean["nested"]["auth"]["accessToken"], "[REDACTED]")
        self.assertEqual(clean["nested"]["auth"]["note"], "token: [REDACTED]")


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
        metadata = json.loads((snapshot / "device-metadata.json").read_text())
        self.assertEqual(manifest["capture_timestamp_utc"], "2026-10-27T12:00:00Z")
        self.assertNotIn("otaId", metadata["fields"])
        self.assertEqual(manifest["restorable_artifacts"], [])
        self.assertEqual(manifest["artifacts"]["applications.json"]["type"], "read-only observation")
        self.assertEqual(manifest["artifacts"]["device-metadata.json"]["type"], "informational metadata")
        self.assertEqual(manifest["device_identity"]["cli_model_name"], "WEBOS6.0")
        self.assertNotIn("model", manifest["device_identity"])
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

    def test_size_mismatch_and_missing_required_artifacts_are_detected(self):
        snapshot = self.make_snapshot()
        manifest_path = snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["artifacts"]["applications.json"]["size_bytes"] += 1
        manifest_path.write_text(json.dumps(manifest))
        os.chmod(manifest_path, 0o600)
        self.assertIn("file size mismatch: applications.json", validate_snapshot(snapshot))
        manifest["artifacts"] = {}
        manifest_path.write_text(json.dumps(manifest))
        os.chmod(manifest_path, 0o600)
        issues = validate_snapshot(snapshot)
        self.assertTrue(any("missing required artifact declarations" in issue for issue in issues))

    def test_missing_artifact_and_unexpected_artifact_are_detected(self):
        snapshot = self.make_snapshot()
        (snapshot / "applications.json").unlink()
        self.assertTrue(any("artifact missing" in issue for issue in validate_snapshot(snapshot)))
        (snapshot / "applications.json").write_text("{}\n")
        os.chmod(snapshot / "applications.json", 0o600)
        (snapshot / "surprise.txt").write_text("x")
        self.assertTrue(any("unexpected snapshot files" in issue for issue in validate_snapshot(snapshot)))

    def test_unsupported_schema_fails_closed(self):
        snapshot = self.make_snapshot()
        path = snapshot / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["schema_version"] = 99
        path.write_text(json.dumps(manifest))
        os.chmod(path, 0o600)
        self.assertEqual(validate_snapshot(snapshot), ["unsupported manifest schema"])

    def test_artifact_cannot_claim_restorable_state(self):
        snapshot = self.make_snapshot()
        path = snapshot / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["artifacts"]["applications.json"]["type"] = "supported restorable backup"
        path.write_text(json.dumps(manifest))
        os.chmod(path, 0o600)
        self.assertTrue(any("unsupported artifact type" in issue for issue in validate_snapshot(snapshot)))

    def test_unknown_manifest_fields_fail_closed(self):
        snapshot = self.make_snapshot()
        path = snapshot / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["restore_state"] = True
        path.write_text(json.dumps(manifest))
        os.chmod(path, 0o600)
        self.assertTrue(any("unsupported manifest fields" in issue for issue in validate_snapshot(snapshot)))

    def test_unknown_raw_application_output_is_not_included_in_snapshot(self):
        secret_text = "permission denied: password=do-not-publish"
        snapshot = create_fixture_snapshot(
            self.root / "unknown", "tv", "", secret_text, "3.2.6", "v24.11.1", "2026-10-27T12:00:00Z"
        )
        self.assertNotIn("do-not-publish", "".join(path.read_text() for path in snapshot.iterdir()))

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

    def test_output_root_permissions_are_preserved_and_unsafe_roots_rejected(self):
        private_root = self.root / "private-root"
        private_root.mkdir(mode=0o750)
        os.chmod(private_root, 0o750)
        with self.assertRaises(InventoryError):
            create_fixture_snapshot(private_root, "tv", "", "[]", "3.2.6", "v24", "2026-10-27T12:00:00Z")
        self.assertEqual(stat.S_IMODE(private_root.stat().st_mode), 0o750)
        safe_root = self.root / "safe-root"
        safe_root.mkdir(mode=0o700)
        os.chmod(safe_root, 0o700)
        create_fixture_snapshot(safe_root, "tv", "", "[]", "3.2.6", "v24", "2026-10-27T12:00:00Z")
        self.assertEqual(stat.S_IMODE(safe_root.stat().st_mode), 0o700)

    def test_symlinked_output_root_and_parent_are_rejected(self):
        real = self.root / "real"
        real.mkdir(mode=0o700)
        link = self.root / "link"
        link.symlink_to(real, target_is_directory=True)
        with self.assertRaises(InventoryError):
            create_fixture_snapshot(link, "tv", "", "[]", "3.2.6", "v24", "2026-10-27T12:00:00Z")
        nested = self.root / "link" / "nested"
        with self.assertRaises(InventoryError):
            create_fixture_snapshot(nested, "tv", "", "[]", "3.2.6", "v24", "2026-10-27T12:00:00Z")

    def test_non_object_manifest_is_rejected(self):
        snapshot = self.make_snapshot()
        (snapshot / "manifest.json").write_text("[]\n")
        with self.assertRaises(InventoryError):
            validate_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
