# Offline webOS CLI environment

This document describes an isolated workstation environment and offline inventory foundation. Developer Mode activation and SSH pairing have since been completed after separate owner approvals. This tooling documentation does not authorize a new TV connection or operation, app installation/removal, or restoration.

## Compatibility evidence

The official npm package page lists `@webos-tools/cli` **3.2.6** as the latest published version at the time of this work and says the package was tested on Node.js 24. The v3.2.6 package metadata declares Node `>=20.0.0`; its release notes say v3.2.6 raised the requirement to `>=20`, and v3.2.4 updated `ssh2` for Node 24 compatibility. The old LG installation page still recommends Node 14.15.1–16.20.2, which is stale relative to the current package and those Node releases are EOL. Use an actively supported Node 24 LTS runtime.

The current workstation had Node `v24.11.1`. The published CLI package was first installed under a disposable `/tmp` prefix and its version/help commands ran under that runtime. The pinned environment was then created as a rootless Ubuntu 24.04 Distrobox; Distrobox `1.8.2.5`, Node `v24.22.1`, and CLI `3.2.6` were installed inside its custom home. Actual `ares-device --help`, `ares-install --help`, `ares-setup-device --help`, `ares-novacom --help`, and `ares --version` output was checked in the container without a TV connection. It confirms the current CLI exposes `--system-info`, `--list`, and `--listfull`, and also exposes mutation-capable commands that the offline inventory tool does not call. This does not validate an SSH session or TV response.

Node 22 LTS also passed a no-device smoke test with the CLI's `ares --version`, `ares-device --help`, and `ares-install --help` commands using the official Node `v22.23.4` binary. It is a suitable fallback if the pinned Node 24 runtime becomes unavailable; Node 24 remains preferred because the package page specifically reports testing Node 24.

Sources: [npm package and Node 24 test statement](https://www.npmjs.com/package/@webos-tools/cli), [v3.2.6 release notes](https://github.com/webos-tools/cli/releases), [package.json](https://github.com/webos-tools/cli/blob/main/package.json), [LG CLI installation page](https://webostv.developer.lge.com/develop/tools/cli-installation), [Node.js release schedule](https://nodejs.org/en/about/previous-releases).

## Create and manage the Bazzite environment

Prerequisites on the host: Bazzite's rootless Podman and Distrobox. The provided environment script does not install host packages or use rootful Podman. It pins the container family to Ubuntu 24.04, the Node runtime to 24.22.1, and the webOS CLI package to 3.2.6. The Ubuntu image tag can move to later 24.04 point releases; record the resolved image digest when creating the box if bit-for-bit base-image reproducibility is required.

```sh
scripts/webos-cli-env.sh create
scripts/webos-cli-env.sh install
scripts/webos-cli-env.sh shell
scripts/webos-cli-env.sh run ares --version
```

The custom container home defaults to `${XDG_DATA_HOME:-$HOME/.local/share}/lg-webos-cli-home` on the host and is created with mode `0700`. Override it with `WEBOS_CLI_HOME` if needed, keeping it outside the repository. The project is mounted at `/workspace/lg-webos-debloat` read-only. The setup script downloads the official Node binary, verifies it against the matching `SHASUMS256.txt` entry, and installs the exact CLI version in that private home. Package installation and tests do not need a TV.

### Pinned runtime PATH

The installer exports PATH only for its own process. A later login shell can reset it, which caused `node`, `ares`, and `ares-setup-device` to be missing from PATH after entering a fresh Distrobox shell. `scripts/webos-cli-path.sh` now provides a project-managed, idempotent activation function. It checks for the pinned Node 24.22.1 binary and CLI executables, prepends `$HOME/.local/npm/bin` followed by `$HOME/.local/opt/node-v24.22.1/bin`, removes duplicate PATH entries, and preserves other non-empty entries. It fails with an install instruction if an expected executable is absent.

Use `scripts/webos-cli-env.sh shell` for an interactive shell with the environment activated. The project starts a clean interactive Bash without host or container login/profile files, avoiding PATH resets and avoiding profile edits. Use `scripts/webos-cli-env.sh run <command> [args...]` for a project-managed noninteractive workstation command; arguments are passed separately without shell evaluation. **`run` is a general command runner, not a TV read-only command allowlist or an authorization mechanism.** It can invoke any command available in the container. Any future automated TV capture must have a separate explicit command allowlist, safe output handling, and approval gate; this runner does not provide those controls. Both entry points retain the restrictive umask and tighten existing credential directory permissions. They do not add credentials or modify the host user's shell configuration. The helper requires the pinned runtime and CLI to be installed first.

To remove the container, run `scripts/webos-cli-env.sh remove`. This leaves the private home in place so the owner can inspect or securely delete device credentials separately. The command never deletes the private home automatically.

## Distrobox and project access limits

Distrobox is a convenience and compatibility layer, **not a security boundary**. Its custom `--home` keeps configuration and dotfiles out of the ordinary host home layout but does not prevent host filesystem access. Inspection of this container showed additional host home aliases and `/run/host` are mounted. Therefore the project bind at `/workspace/lg-webos-debloat` is read-only, but the same repository may also be reachable through an ordinary writable host-home path. That bind alone does not enforce write isolation against compromised or untrusted container code. Keep snapshots and credentials in the custom home, never in the repository. Do not treat the container as safe for untrusted code or as isolation from the host.

## Actual webOS CLI credential paths

Inspection of the installed v3.2.6 package and its local help behavior established these paths under the CLI process's `HOME`:

- Device profiles: `~/.webos/tv/novacom-devices.json`. The file can include target host/IP, username, key reference and the Developer Mode passphrase. `ares-setup-device --listfull` can expose sensitive profile fields; do not share or log it.
- Retrieved Developer Mode key: `~/.ssh/<device-name>_webos`. CLI source downloads the key to this path and sets it to mode `0600` after retrieval.
- `~/.webos` and its profile file were created as `0755` and `0644` by the CLI under the workstation's default umask during the offline help check. The install script and environment shell set `umask 077` and tighten existing profile/key directories and files to owner-only access. Check modes after any CLI setup operation; do not assume the CLI protects all local profile files by default.

These paths were verified by inspecting the official package source and observing CLI-created files in a disposable home. No pairing data or real credentials were used. Keep the entire custom home private, encrypted at rest where available, and outside Git. Never paste profile output, keys, passphrases, or unredacted diagnostics into issues or commits.

## Approved future command vectors

The offline foundation builds but never executes these vectors:

```text
ares-device --system-info --device <explicit-alias>
ares-install --device <explicit-alias> --list
ares-install --device <explicit-alias> --listfull
```

`--listfull` is supported by v3.2.6 CLI help. Prefer `--list` unless a documented inventory need requires additional app details. The owner reports that both list commands returned zero app records on the TV, with `--listfull` exit status 0. This is **successful CLI execution; zero application records returned; full installed-app catalogue coverage unknown**; the reason for the empty results is not established. The offline utility has no live-device mode and no arbitrary command argument. App install/removal, launch/termination, shell, session extension, scanning, and TV file transfer are not allowlisted. No restoration operation is implemented.

The installed v3.2.6 package does not ship an `ares-extend-dev` executable in its published command map; local help and package metadata showed no such command. Do not use or document it for this environment. Future manual session renewal uses the Developer Mode app's **EXTEND** control as described in LG's guide.

## Offline fixture and snapshot use

The snapshot output root must already be suitable if it exists: owned by the current user, writable/searchable by its owner, and inaccessible to group/other users. The tool rejects permissive roots and symlinked path components without changing existing modes. Create new roots in a trusted local location; snapshot directories are timestamped and private (`0700`) and files are owner-only (`0600`, or stricter under the active umask). The path checks are best-effort against symlink races, so do not let another user or process modify the output path during capture.

The checked-in fixtures contain synthetic app IDs and sample metadata, not data from this TV:

```sh
python3 scripts/webos_inventory.py capture-fixtures \
  --device-alias tv \
  --metadata-fixture tests/fixtures/ares-device-system-info.txt \
  --apps-fixture tests/fixtures/ares-install-list.json \
  --cli-version 3.2.6 --runtime-version v24.11.1 \
  --output-root backups
```

Validate the resulting snapshot with:

```sh
python3 scripts/webos_inventory.py validate backups/<timestamp>
```

Fixture snapshots are explicitly labeled `offline-fixture`; they prove only parser and manifest behavior. Snapshots require metadata and application artifact declarations, validate their types, sizes, checksums and files, report incomplete fields/output, and claim no restorable artifacts. Application parsing records accepted, rejected and total counts when determinable; malformed or dropped records make the result partial, while an empty JSON array is a complete empty list. A valid checksum proves byte integrity only, not completeness, authenticity, device compatibility, or restorability.

Redaction is best-effort, not a guarantee that arbitrary input is free of sensitive information. Unknown raw output is not automatically safe to publish and is not saved by fixture capture. Any future raw diagnostics must remain separate in a private owner-only location; only a separately reviewed redacted copy may be considered for sharing. The parser does not infer removability and drops removal/uninstall-related fields if they appear in input.

CLI `modelName` is recorded as a CLI-reported metadata value (`cli_model_name`), not as the exact physical LG product model. The target LG 55UP81006LR is identified in project hardware notes from owner observation. Independent hardware identity verification is not provided by the CLI field or this offline tool.
