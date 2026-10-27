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
        self.mock_bin = self.root / "mock-bin"
        self.node_bin.mkdir(parents=True)
        self.npm_bin.mkdir(parents=True)
        self.other_bin.mkdir()
        self.mock_bin.mkdir()
        self.home.mkdir(exist_ok=True)
        for executable in (self.node_bin / "node", self.npm_bin / "ares", self.npm_bin / "ares-setup-device"):
            self.make_executable(executable, "#!/bin/sh\nexit 0\n")

        self.path_helper = self.root / "webos-cli-path.sh"
        self.path_helper.write_text(PATH_HELPER.read_text())
        mock_distrobox = self.mock_bin / "distrobox"
        self.make_executable(
            mock_distrobox,
            "#!/bin/bash\n"
            "[[ \"$1\" == enter ]] || exit 97\n"
            "shift 3\n"
            "[[ \"$1\" == bash ]] || exit 98\n"
            "shift\n"
            "args=()\n"
            "for arg in \"$@\"; do\n"
            "  if [[ \"$arg\" == /workspace/lg-webos-debloat/scripts/webos-cli-path.sh ]]; then arg=$MOCK_WEBOS_CLI_PATH_HELPER; fi\n"
            "  args+=(\"$arg\")\n"
            "done\n"
            "exec /bin/bash \"${args[@]}\"\n",
        )

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def make_executable(path, contents):
        path.write_text(contents)
        path.chmod(0o700)

    def env(self):
        return {
            **os.environ,
            "HOME": str(self.home),
            "PATH": ":".join((str(self.mock_bin), str(self.other_bin), os.environ["PATH"])),
            "MOCK_WEBOS_CLI_PATH_HELPER": str(self.path_helper),
        }

    def run_entrypoint(self, action, *args):
        return subprocess.run(
            ["/bin/bash", str(ENV_SCRIPT), action, *args],
            env=self.env(),
            text=True,
            capture_output=True,
            check=False,
        )

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

    def make_probe(self):
        probe = self.other_bin / "probe"
        self.args_file = self.root / "probe-args"
        self.path_file = self.root / "probe-path"
        self.make_executable(
            probe,
            "#!/bin/bash\n"
            f"printf '%s\\0' \"$@\" > '{self.args_file}'\n"
            f"printf '%s' \"$PATH\" > '{self.path_file}'\n",
        )
        return probe

    def make_shell_probe(self):
        self.shell_args_file = self.root / "shell-args"
        self.shell_path_file = self.root / "shell-path"
        fake_bash = self.other_bin / "bash"
        self.make_executable(
            fake_bash,
            "#!/bin/bash\n"
            f"printf '%s\\0' \"$@\" > '{self.shell_args_file}'\n"
            f"printf '%s' \"$PATH\" > '{self.shell_path_file}'\n",
        )

    def test_entrypoint_fails_for_missing_pinned_node_without_running_target(self):
        (self.node_bin / "node").unlink()
        probe = self.make_probe()
        result = self.run_entrypoint("run", str(probe))
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing executable", result.stderr)
        self.assertIn("node", result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_entrypoint_fails_for_missing_cli_without_running_target(self):
        (self.npm_bin / "ares").unlink()
        probe = self.make_probe()
        result = self.run_entrypoint("run", str(probe))
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing executable", result.stderr)
        self.assertIn("ares", result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_failed_helper_source_preserves_status_and_never_runs_shell_or_command(self):
        self.path_helper.write_text('printf "source failure\\n" >&2\nreturn 23\n')
        for action in ("shell", "run"):
            with self.subTest(action=action):
                self.make_shell_probe()
                probe = self.make_probe()
                args = (str(probe),) if action == "run" else ()
                result = self.run_entrypoint(action, *args)
                self.assertEqual(result.returncode, 23)
                self.assertIn("source failure", result.stderr)
                self.assertFalse(self.shell_args_file.exists())
                self.assertFalse(self.args_file.exists())

    def test_failed_activation_preserves_status_and_never_runs_shell_or_command(self):
        self.path_helper.write_text(
            'webos_cli_activate_path() { printf "activation failure\\n" >&2; return 24; }\n'
        )
        for action in ("shell", "run"):
            with self.subTest(action=action):
                self.make_shell_probe()
                probe = self.make_probe()
                args = (str(probe),) if action == "run" else ()
                result = self.run_entrypoint(action, *args)
                self.assertEqual(result.returncode, 24)
                self.assertIn("activation failure", result.stderr)
                self.assertFalse(self.shell_args_file.exists())
                self.assertFalse(self.args_file.exists())

    def test_shell_entry_runs_interactive_shell_after_successful_activation(self):
        self.make_shell_probe()
        result = self.run_entrypoint("shell")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.shell_args_file.read_bytes().split(b"\0")[:-1], [b"--noprofile", b"--norc", b"-i"])
        entries = self.shell_path_file.read_text().split(":")
        self.assertEqual(entries[:3], [str(self.npm_bin), str(self.node_bin), str(self.mock_bin)])
        for profile in (".bashrc", ".profile", ".bash_profile"):
            self.assertFalse((self.home / profile).exists())

    def test_run_executes_command_and_preserves_arguments_after_activation(self):
        probe = self.make_probe()
        command_args = ("two words", "$literal", "semi;colon")
        result = self.run_entrypoint("run", str(probe), *command_args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.args_file.read_bytes().split(b"\0")[:-1], [item.encode() for item in command_args])
        entries = self.path_file.read_text().split(":")
        self.assertEqual(entries[:3], [str(self.npm_bin), str(self.node_bin), str(self.mock_bin)])

    def test_project_run_requires_a_command(self):
        result = self.run_entrypoint("run")
        self.assertEqual(result.returncode, 2)
        self.assertIn("A command is required", result.stderr)


if __name__ == "__main__":
    unittest.main()
