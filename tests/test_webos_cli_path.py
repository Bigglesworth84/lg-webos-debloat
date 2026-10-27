import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH_HELPER = ROOT / "scripts" / "webos-cli-path.sh"
ENV_SCRIPT = ROOT / "scripts" / "webos-cli-env.sh"


class WebOSCliPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "cli-home"
        self.node_bin = self.home / ".local/opt/node-v24.22.1/bin"
        self.npm_bin = self.home / ".local/npm/bin"
        self.other_bin = self.root / "existing-bin"
        self.node_bin.mkdir(parents=True)
        self.npm_bin.mkdir(parents=True)
        self.other_bin.mkdir()
        for executable in (self.node_bin / "node", self.npm_bin / "ares", self.npm_bin / "ares-setup-device"):
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o700)

    def tearDown(self):
        self.temp.cleanup()

    def activate(self, path):
        result = subprocess.run(
            ["/bin/bash", "-c", 'source "$1" && webos_cli_activate_path && printf "%s\\n" "$PATH" && command -v node && command -v ares && command -v ares-setup-device', "test", str(PATH_HELPER)],
            env={**os.environ, "HOME": str(self.home), "PATH": path},
            text=True,
            capture_output=True,
            check=False,
        )
        return result

    def test_resolves_pinned_node_and_cli_with_expected_path_order(self):
        result = self.activate(str(self.other_bin))
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0].split(":"), [str(self.npm_bin), str(self.node_bin), str(self.other_bin)])
        self.assertEqual(lines[1:], [str(self.node_bin / "node"), str(self.npm_bin / "ares"), str(self.npm_bin / "ares-setup-device")])

    def test_activation_is_idempotent_and_preserves_existing_entries(self):
        start = ":".join([str(self.other_bin), str(self.npm_bin), str(self.other_bin), str(self.node_bin)])
        result = subprocess.run(
            ["/bin/bash", "-c", 'source "$1" && webos_cli_activate_path && before=$PATH && webos_cli_activate_path && [[ "$PATH" == "$before" ]] && printf "%s\\n" "$PATH"', "test", str(PATH_HELPER)],
            env={**os.environ, "HOME": str(self.home), "PATH": start},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        entries = result.stdout.strip().split(":")
        self.assertEqual(entries, [str(self.npm_bin), str(self.node_bin), str(self.other_bin)])

    def test_missing_pinned_executable_fails_clearly(self):
        (self.npm_bin / "ares-setup-device").unlink()
        result = self.activate(str(self.other_bin))
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing executable", result.stderr)
        self.assertIn("ares-setup-device", result.stderr)
        self.assertIn("scripts/webos-cli-env.sh install", result.stderr)

    def test_shell_entry_uses_project_path_activation_without_host_profile_edits(self):
        mock_bin = self.root / "mock-bin"
        mock_bin.mkdir()
        host_home = self.root / "host-home"
        host_home.mkdir()
        record = self.root / "distrobox-args"
        mock_distrobox = mock_bin / "distrobox"
        mock_distrobox.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$@\" > '{record}'\n")
        mock_distrobox.chmod(0o700)
        result = subprocess.run(
            ["bash", str(ENV_SCRIPT), "shell"],
            env={**os.environ, "HOME": str(host_home), "PATH": f"{mock_bin}:{os.environ['PATH']}"},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        args = record.read_text()
        self.assertIn("source /workspace/lg-webos-debloat/scripts/webos-cli-path.sh", args)
        self.assertIn("webos_cli_activate_path", args)
        self.assertIn("bash --noprofile --norc -i", args)
        for profile in (".bashrc", ".profile", ".bash_profile"):
            self.assertFalse((host_home / profile).exists())

    def test_project_run_requires_a_command(self):
        result = subprocess.run(["bash", str(ENV_SCRIPT), "run"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("A command is required", result.stderr)


if __name__ == "__main__":
    unittest.main()
