import json
import os
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.webos_inventory import InventoryError, create_fixture_snapshot, validate_snapshot
from scripts.webos_live_capture import create_live_snapshot


ROOT = Path(__file__).resolve().parents[1]


class LiveCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "cli-home"
        self.mock_bin = self.root / "mock-bin"
        self.home.mkdir(mode=0o700)
        self.mock_bin.mkdir()
        npm_bin = self.home / ".local/npm/bin"
        node_bin = self.home / ".local/opt/node-v24.22.1/bin"
        npm_bin.mkdir(parents=True)
        node_bin.mkdir(parents=True)
        for path in (npm_bin / "ares", npm_bin / "ares-setup-device", node_bin / "node"):
            self.make_executable(path, "#!/bin/sh\nexit 0\n")
        for path in (npm_bin / "ares-device", npm_bin / "ares-install"):
            self.make_executable(path, "#!/bin/sh\nexit 0\n")
        self.calls = self.root / "calls.txt"
        distrobox = self.mock_bin / "distrobox"
        self.make_executable(
            distrobox,
            "#!/bin/bash\n"
            "[[ \"$1\" == enter ]] || exit 90\n"
            "shift 3\n"
            "[[ \"$1\" == bash ]] || exit 91\n"
            "shift\n"
            "args=()\n"
            "for arg in \"$@\"; do\n"
            "  [[ \"$arg\" == /workspace/lg-webos-debloat/scripts/webos-cli-path.sh ]] && arg=$MOCK_PATH_HELPER\n"
            "  args+=(\"$arg\")\n"
            "done\n"
            "exec /bin/bash \"${args[@]}\"\n",
        )
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.mock_bin}:/usr/bin:/bin",
            "MOCK_PATH_HELPER": str(ROOT / "scripts/webos-cli-path.sh"),
            "MOCK_CALLS": str(self.calls),
        }

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def make_executable(path, source):
        path.write_text(source)
        path.chmod(0o700)

    def write_cli(self, name, stdout="", stderr="", status=0, source=None):
        out = self.root / f"{name}.out"
        err = self.root / f"{name}.err"
        out.write_bytes(stdout.encode())
        err.write_bytes(stderr.encode())
        script = source or (
            "#!/bin/bash\n"
            f"printf '%s\\0' '{name}' \"$@\" >> \"$MOCK_CALLS\"\n"
            f"cat '{out}'\ncat '{err}' >&2\nexit {status}\n"
        )
        self.make_executable(self.home / ".local/npm/bin" / name, script)

    def capture(self, operations=("metadata",), **kwargs):
        timeout_seconds = kwargs.pop("timeout_seconds", None)
        output_limit = kwargs.pop("output_limit", None)
        if kwargs:
            raise AssertionError(f"Unsupported test arguments: {sorted(kwargs)}")
        with (
            patch("scripts.webos_live_capture._process_environment", return_value=self.env),
            patch("scripts.webos_live_capture.TIMEOUT_SECONDS", timeout_seconds or 30),
            patch("scripts.webos_live_capture.MAX_OUTPUT_BYTES", output_limit or 1024 * 1024),
        ):
            return create_live_snapshot(self.root / "backups", "lounge-tv", list(operations))

    def manifest(self, snapshot):
        return json.loads((snapshot / "manifest.json").read_text())

    def test_successful_metadata_capture_persists_only_allowlisted_fields(self):
        self.write_cli(
            "ares-device",
            "[Info] Set target device : fixture-tv\n"
            "modelName : SYNTHETIC.MODEL\n"
            "sdkVersion : 0.0.0\n"
            "firmwareVersion : 00.00.00\n"
            "boardType : SYNTHETIC_BOARD\n"
            "otaId : [REDACTED]\n",
        )
        snapshot = self.capture()
        content = json.loads((snapshot / "device-metadata.json").read_text())
        self.assertEqual(content["fields"], {
            "modelName": "SYNTHETIC.MODEL", "sdkVersion": "0.0.0",
            "firmwareVersion": "00.00.00", "boardType": "SYNTHETIC_BOARD",
        })
        self.assertNotIn("otaId", (snapshot / "device-metadata.json").read_text())
        manifest = self.manifest(snapshot)
        self.assertEqual(manifest["operations"][0]["parsing_outcome"], "recognized_records")
        self.assertEqual(manifest["capture_status"], "successful_capture")
        self.assertEqual(manifest["inventory_coverage"], "unknown_or_incomplete")
        self.assertEqual(validate_snapshot(snapshot), [])

    def test_metadata_missing_field_and_malformed_output_are_not_complete(self):
        self.write_cli(
            "ares-device",
            "[Info] Set target device : fixture-tv\n"
            "modelName : SYNTHETIC.MODEL\nsdkVersion : 0.0.0\n"
            "firmwareVersion : 00.00.00\nmalformed metadata\notaId : [REDACTED]\n",
        )
        snapshot = self.capture()
        manifest = self.manifest(snapshot)
        self.assertEqual(manifest["operations"][0]["parsing_outcome"], "partial_records")
        self.assertEqual(manifest["capture_status"], "partial")
        metadata = json.loads((snapshot / "device-metadata.json").read_text())
        self.assertNotIn("boardType", metadata["fields"])
        self.assertIn("boardType", metadata["missing_fields"])
        self.assertNotIn("[REDACTED]", "".join(path.read_text() for path in snapshot.iterdir()))

    def test_other_unrecognised_metadata_fields_are_discarded_and_partial(self):
        self.write_cli(
            "ares-device",
            "modelName : SYNTHETIC.MODEL\nsdkVersion : 0.0.0\n"
            "firmwareVersion : 00.00.00\nboardType : SYNTHETIC_BOARD\n"
            "serialNumber : [REDACTED]\n",
        )
        snapshot = self.capture()
        manifest = self.manifest(snapshot)
        self.assertEqual(manifest["operations"][0]["parsing_outcome"], "partial_records")
        self.assertNotIn("serialNumber", (snapshot / "device-metadata.json").read_text())
        self.assertNotIn("[REDACTED]", "".join(path.read_text() for path in snapshot.iterdir()))

    def test_duplicate_allowed_metadata_field_is_not_silently_accepted(self):
        self.write_cli(
            "ares-device",
            "modelName : SYNTHETIC.MODEL\nsdkVersion : 0.0.0\n"
            "firmwareVersion : 00.00.00\nboardType : SYNTHETIC_BOARD\n"
            "boardType : SYNTHETIC_BOARD\n",
        )
        snapshot = self.capture()
        metadata = json.loads((snapshot / "device-metadata.json").read_text())
        record = self.manifest(snapshot)["operations"][0]
        self.assertNotIn("boardType", metadata["fields"])
        self.assertEqual(record["parsing_outcome"], "partial_records")

    def test_successful_application_capture_persists_ids_only(self):
        self.write_cli("ares-install", '[{"id":"com.example.good","title":"private title","token":"secret"}]')
        snapshot = self.capture(("applications",))
        artifact = json.loads((snapshot / "applications.json").read_text())
        self.assertEqual(artifact["application_ids"], ["com.example.good"])
        self.assertNotIn("private title", (snapshot / "applications.json").read_text())
        self.assertNotIn("secret", (snapshot / "applications.json").read_text())
        self.assertEqual(self.manifest(snapshot)["capture_status"], "successful_capture")

    def test_network_address_shaped_metadata_and_application_ids_are_discarded(self):
        self.write_cli(
            "ares-device",
            "modelName : WEBOS6.0\nsdkVersion : 6.1.0\nfirmwareVersion : 03.53.45\nboardType : AA:BB:CC:DD:EE:FF\n",
        )
        self.write_cli("ares-install", '[{"id":"192.168.1.4"},{"id":"com.example.good"}]')
        snapshot = self.capture(("metadata", "applications"))
        metadata = json.loads((snapshot / "device-metadata.json").read_text())
        applications = json.loads((snapshot / "applications.json").read_text())
        self.assertNotIn("boardType", metadata["fields"])
        self.assertEqual(applications["application_ids"], ["com.example.good"])
        self.assertNotIn("192.168.1.4", "".join(path.read_text() for path in snapshot.iterdir()))

    def test_sensitive_duplicate_metadata_field_cannot_overwrite_safe_value(self):
        self.write_cli(
            "ares-device",
            "modelName : WEBOS6.0\nsdkVersion : 6.1.0\nfirmwareVersion : 03.53.45\n"
            "boardType : K7LP_EU\nfirmwareVersion : 192.168.1.4\n",
        )
        snapshot = self.capture()
        content = json.loads((snapshot / "device-metadata.json").read_text())
        self.assertNotIn("firmwareVersion", content["fields"])
        self.assertNotIn("192.168.1.4", "".join(path.read_text() for path in snapshot.iterdir()))

    def test_zero_byte_application_output_is_successful_empty_not_complete_inventory(self):
        self.write_cli("ares-install")
        snapshot = self.capture(("applications",))
        manifest = self.manifest(snapshot)
        self.assertEqual(manifest["operations"][0]["execution_outcome"], "succeeded")
        self.assertEqual(manifest["operations"][0]["parsing_outcome"], "successful_empty_output")
        self.assertEqual(manifest["capture_status"], "successful_capture")
        self.assertEqual(manifest["inventory_coverage"], "unknown_or_incomplete")
        self.assertEqual(json.loads((snapshot / "applications.json").read_text())["application_ids"], [])

    def test_empty_json_array_is_recognized_but_not_complete_inventory(self):
        self.write_cli("ares-install", "[]")
        snapshot = self.capture(("applications",))
        manifest = self.manifest(snapshot)
        self.assertEqual(manifest["operations"][0]["parsing_outcome"], "recognized_empty_json_collection")
        self.assertEqual(manifest["inventory_coverage"], "unknown_or_incomplete")

    def test_unrecognized_and_malformed_responses_are_partial(self):
        for index, response in enumerate(("permission denied", '[{"id":"com.example.app"}')):
            with self.subTest(response=response):
                original_root = self.root
                self.root = original_root / str(index)
                self.root.mkdir()
                self.write_cli("ares-install", response)
                snapshot = self.capture(("applications",))
                self.assertEqual(self.manifest(snapshot)["operations"][0]["parsing_outcome"], "unrecognized_output")
                self.root = original_root

    def test_nonzero_authentication_failure_stops_selected_following_operation(self):
        self.write_cli("ares-device", stderr="Authentication failed: password=hunter2", status=8)
        self.write_cli("ares-install", '[{"id":"com.example.app"}]')
        snapshot = self.capture(("metadata", "applications"))
        manifest = self.manifest(snapshot)
        self.assertEqual([item["execution_outcome"] for item in manifest["operations"]], ["failed", "skipped"])
        self.assertEqual(manifest["operations"][0]["failure_classification"], "connection_or_authentication_failure")
        self.assertNotIn("hunter2", "".join(path.read_text() for path in snapshot.iterdir()))
        self.assertEqual(self.calls.read_bytes().count(b"\0"), 4)

    def test_missing_executable_fails_without_raw_diagnostic_or_fallback(self):
        (self.home / ".local/npm/bin/ares-device").unlink()
        snapshot = self.capture(("metadata", "applications"))
        manifest = self.manifest(snapshot)
        self.assertEqual(manifest["operations"][0]["execution_outcome"], "failed")
        self.assertEqual(manifest["operations"][0]["failure_classification"], "environment_or_cli_unavailable")
        self.assertEqual(manifest["operations"][1]["execution_outcome"], "skipped")

    def test_timeout_terminates_and_reaps_mocked_container_descendant(self):
        pidfile = self.root / "child.pid"
        self.write_cli(
            "ares-install",
            source=f"#!/bin/bash\nsleep 60 & child=$!\nprintf '%s' \"$child\" > '{pidfile}'\nwait $child\n",
        )
        snapshot = self.capture(("applications",), timeout_seconds=1)
        record = self.manifest(snapshot)["operations"][0]
        self.assertEqual(record["execution_outcome"], "timed_out")
        self.assertTrue(pidfile.exists())
        pid = int(pidfile.read_text())
        time.sleep(0.05)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pass
        else:
            with open(f"/proc/{pid}/stat") as process_stat:
                self.assertEqual(process_stat.read().split()[2], "Z")

    def test_output_limit_kills_process_and_skips_following_operation(self):
        self.write_cli("ares-install", "x" * 1000)
        self.write_cli("ares-device", "modelName : WEBOS6.0\n")
        snapshot = self.capture(("applications", "metadata"), output_limit=64)
        records = self.manifest(snapshot)["operations"]
        self.assertEqual([record["execution_outcome"] for record in records], ["output_limit_exceeded", "skipped"])

    def test_no_raw_stdout_or_stderr_is_persisted(self):
        self.write_cli("ares-install", "password=raw-output-secret", stderr="token=raw-error-secret", status=1)
        snapshot = self.capture(("applications",))
        content = "".join(path.read_text() for path in snapshot.iterdir())
        self.assertNotIn("raw-output-secret", content)
        self.assertNotIn("raw-error-secret", content)

    def test_argument_injection_and_unsupported_selection_are_rejected(self):
        with self.assertRaises(InventoryError):
            create_live_snapshot(self.root / "bad-alias", "tv;touch", ["metadata"])
        for operation in ([], ["shell"], ["metadata;id"]):
            with self.subTest(operation=operation), self.assertRaises(InventoryError):
                create_live_snapshot(self.root / "bad-operation", "tv", operation)
        with self.assertRaises(InventoryError):
            create_live_snapshot(self.root / "duplicate", "tv", ["metadata", "metadata"])

    def test_container_capture_action_rejects_unapproved_flags_before_distrobox(self):
        result = subprocess.run(
            [str(ROOT / "scripts/webos-cli-env.sh"), "capture", "metadata", "tv",
             "ares-device", "--system-info", "--device", "tv", "--extra"],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.calls.exists())

    def test_version_1_fixture_snapshot_still_validates(self):
        snapshot = create_fixture_snapshot(
            self.root / "fixture-backups", "tv",
            "modelName : WEBOS6.0\nsdkVersion : 6.1.0\nfirmwareVersion : 03.53.45\nboardType : EU\notaId : EU\n",
            '[{"id":"com.example.fixture"}]', "3.2.6", "v24.22.1", "2026-10-27T12:00:00Z",
        )
        manifest = json.loads((snapshot / "manifest.json").read_text())
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(validate_snapshot(snapshot), [])

    def test_private_storage_checksums_tampering_and_permissions(self):
        self.write_cli("ares-device", "modelName : WEBOS6.0\n")
        snapshot = self.capture()
        self.assertEqual(validate_snapshot(snapshot), [])
        self.assertEqual(stat.S_IMODE(snapshot.stat().st_mode), 0o700)
        for path in snapshot.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        artifact = snapshot / "device-metadata.json"
        artifact.write_text("{}")
        artifact.chmod(0o600)
        self.assertTrue(any("checksum mismatch" in issue for issue in validate_snapshot(snapshot)))

    def test_manifest_command_vector_tampering_is_rejected(self):
        self.write_cli("ares-install", "[]")
        snapshot = self.capture(("applications",))
        manifest_path = snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["operations"][0]["command_argv"].append("--remove")
        manifest_path.write_text(json.dumps(manifest))
        manifest_path.chmod(0o600)
        self.assertTrue(any("unapproved command vector" in issue for issue in validate_snapshot(snapshot)))

    def test_symlinked_output_root_is_rejected(self):
        target = self.root / "real"
        target.mkdir(mode=0o700)
        link = self.root / "link"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaises(InventoryError):
            create_live_snapshot(link, "tv", ["metadata"])

    def test_selected_command_executes_once_and_manifest_has_explicit_vector(self):
        self.write_cli("ares-install", "[]")
        snapshot = self.capture(("applications",))
        record = self.manifest(snapshot)["operations"][0]
        self.assertEqual(record["command_argv"], ["ares-install", "--device", "lounge-tv", "--list"])
        self.assertEqual(self.calls.read_bytes().count(b"\0"), 4)


if __name__ == "__main__":
    unittest.main()
