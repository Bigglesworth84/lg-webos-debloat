# Developer Mode and read-only inventory runbook

**Status: preparation only.** This runbook does not grant approval to connect to or change the LG 55UP81006LR. Any future device-facing slice needs a separate explicit approval after the backup-first gate in [recovery-policy.md](recovery-policy.md) is complete.

## Before activation

1. Ask the owner to manually inspect and confirm the exact model and current firmware/webOS version. Existing values in [hardware.md](hardware.md) are owner-confirmed, but must be rechecked immediately before a future state change.
2. Record accessible native settings and app/function baseline; state what cannot be captured. No machine-readable TV backup or supported restore interface is currently established.
3. Capture a timestamped pre-activation inventory only if already-authorized supported read access exists. Otherwise state plainly that no pre-activation device inventory exists and do not imply Developer Mode itself makes a backup.
4. Present recovery limits: enabling Developer Mode reboots the TV; expiry or deactivation can remove sideloaded Developer Mode apps, and their local state may be lost. Classify activation as **partially reversible**; app-local state recovery is **recovery unverified / irreversible** absent evidence.
5. Obtain explicit approval for Developer Mode app installation, activation, and SSH pairing as separate actions. Approval for this offline tooling slice is not approval to do any of them.

## Operation recovery boundaries

| Operation | State change and recovery status |
|---|---|
| Install Developer Mode app | Changes installed-app state. This exact model's removal/reinstall route and any app data consequences have not been verified; classify **recovery unverified / irreversible** until documented. |
| Enable Developer Mode | Reboots the TV and enables a time-limited developer session. Manual status control is the intended deactivation route; classify **partially reversible** because deactivation can remove Developer Mode apps and local app data may be lost. |
| SSH pairing / key retrieval | Writes a local device profile and private key. LG documents the key retrieval flow, but the guide does not establish whether TV-side authorization persists or document a supported revocation route. Treat any persistent TV-side authorization as **recovery unverified / irreversible** until verified. |
| Extend session | Changes the remaining Developer Mode session time. Use only the TV's **EXTEND** control after separate approval; inventory must not renew it. |

Before each operation, record the original state, capture what is accessible, state coverage gaps, explain what cannot be restored, document and safely validate the recovery route, then obtain approval for that specific operation. Do not classify any operation as fully reversible based on these notes alone.

## Install and activate Developer Mode

1. Confirm the private Distrobox CLI home is outside the repository, mode `0700`; verify its profile/key paths and permissions as described in [webOS CLI environment](webos-cli-environment.md).
2. With the owner at the TV, install the official Developer Mode app from LG Apps if it is not already installed. This changes the TV's installed app state and requires the separate approval above.
3. Sign in to the Developer Mode app using the owner's LG Developer account directly on the TV. Never collect or record the account password.
4. Record the app's current Dev Mode status and remaining session time, then enable Dev Mode only after specific approval. LG documents that this reboots the TV; wait for it to return and confirm normal Home/input operation.
5. Do not install, launch, or remove any other app in this slice.

## SSH pairing and read-only inventory

1. Have the owner open the Developer Mode app's Key Server control. Use a manually verified TV address from the TV's network status; do not scan the LAN.
2. Add the target with an explicit alias, correct observed address, port `9922`, and user `prisoner`, for example `ares-setup-device --add <alias> --info "host=<observed-address>" --info "port=9922" --info "username=prisoner"`. This changes the workstation-side profile only. Keep the profile under the isolated custom home.
3. After separate pairing approval, retrieve the key with `ares-novacom --getkey --device <alias>` while the owner is present to enter the short-lived passphrase at the interactive prompt. Never put the passphrase in shell history, command arguments, fixtures or logs. Verify that the CLI key is `0600` and profile data is `0600` within owner-only `0700` directories. Treat persistent TV-side key authorization and its revocation as unverified unless LG documents the lifecycle.
4. For the approved capture only, run `ares-device --system-info --device <alias>`, `ares-install --device <alias> --list`; use `--listfull` only if its added fields are needed and approved. The alias is a required explicit value, not a scan target.
5. Store raw diagnostics in a private local directory separate from any redacted report. Redact serials, IP/MAC addresses, account values, passphrases, tokens, key material, and unrelated personal data before review or sharing.
6. Create the local manifest with UTC timestamp, exact tool/runtime versions, coverage gaps, artifact classifications and SHA-256 hashes. Label metadata informational and app inventory read-only; record no restorable TV-state artifacts. Inventory does not establish removability or complete system coverage.

## Session expiry, renewal, and deactivation

- LG documents that Developer Mode disables when the remaining session expires or after ten TV reboots while offline. It also states sideloaded Developer Mode apps are uninstalled when the mode disables.
- Check remaining time in the Developer Mode app. Renewal changes TV state and requires separate approval; if approved, use the TV's documented **EXTEND** control manually. Inventory tooling must not renew the session.
- To deactivate, use the Developer Mode app's Dev Mode Status control after recording current status and completing the capture. Confirm the TV returns to ordinary operation and recheck status. LG documentation describes expiry/disable behavior; exact effects of an intentional user deactivation must be checked against the current on-screen confirmation before proceeding.
- Removing the Developer Mode app itself is a separate TV mutation; do not do so as cleanup without separate approval and a recovery review.

No known route restores sideloaded app-local data after Dev Mode disables. Do not rely on factory reset, firmware downgrade, or a generic TV backup as recovery.

## Post-activation checks

Without changing app/settings state, manually verify and record:

- BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV launch and play content.
- Emby local server discovery, authentication and playback.
- HDMI switching and Raspberry Pi Steam Link connection.
- HDMI-CEC, HDR, Game Mode/low-latency mode, audio, network, and required Bluetooth behavior.
- Developer Mode state, session display, normal startup, and normal operation after deactivation.

Treat a failed check as a baseline finding. Do not proceed to application mutation or firmware change.

Sources: [LG Developer Mode setup, connection and session rules](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app), [LG CLI guide and command references](https://webostv.developer.lge.com/develop/tools/cli-dev-guide), [project backup and recovery policy](recovery-policy.md).
