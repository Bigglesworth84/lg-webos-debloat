# Developer Mode and read-only inventory runbook

**Status: preparation only.** This runbook does not grant approval to connect to or change the LG 55UP81006LR. Any future device-facing slice needs a separate explicit approval after the backup-first gate in [recovery-policy.md](recovery-policy.md) is complete.

## Before activation

1. With the owner, complete [the pre-activation baseline](pre-activation-baseline.md) manually on the TV and connected equipment. This requires no computer connection to the TV. Record each used HDMI port separately, including its owner-identified device, picture and audio, switching, Game Mode, ALLM/HDR/CEC where supported or used, and limitations. Record Wi-Fi or Ethernet, internet and local-network behavior, Emby discovery/playback, and launch/playback for every protected app. Recheck the privacy and advertising settings without changing them. Mark unused or unsupported checks Not applicable with a reason; leave unobserved checks Not tested.
2. Reconfirm the physical model and current firmware/webOS version on the TV immediately before any future state change. The values in [hardware.md](hardware.md) are prior owner-confirmed observations, not confirmation of current state. Do not treat CLI metadata as physical model proof.
3. Identify what the manual baseline cannot recover: it records observations only. It does not export TV configuration, app-private data, account state, or a complete system image. No supported machine-readable TV backup or general restore interface is established. An offline application inventory is not a full-system backup.
4. Before activation, present the recovery classification and consequences: installing the Developer Mode app changes installed-app state (**recovery unverified / irreversible** for this exact model until its removal/reinstall route is established); enabling Developer Mode changes TV state and reboots it (**partially reversible** through the app's status control, with sideloaded apps and local state at risk); app-local state after expiry/deactivation is **recovery unverified / irreversible**; SSH pairing stores local credentials and may leave TV-side authorization (**recovery unverified / irreversible** until revocation is documented). Expiry or deactivation can uninstall sideloaded apps. No complete backup or guaranteed factory-reset/downgrade recovery exists.
5. Obtain and record separate explicit approval for Developer Mode app installation, activation, and SSH pairing/key retrieval. Approval for this offline preparation slice is not approval for any of these actions.
6. Confirm every item in the readiness checklist at the end of [pre-activation-baseline.md](pre-activation-baseline.md). Do not proceed with unexplained baseline failures or an unverified CLI/credential setup.

## Operation recovery boundaries

| Operation | State change and recovery status |
|---|---|
| Install Developer Mode app | Changes installed-app state. This exact model's removal/reinstall route and any app data consequences have not been verified; classify **recovery unverified / irreversible** until documented. |
| Enable Developer Mode | Reboots the TV and enables a time-limited developer session. Manual status control is the intended deactivation route; classify **partially reversible** because deactivation can remove Developer Mode apps and local app data may be lost. |
| SSH pairing / key retrieval | Writes a local device profile and private key. LG documents the key retrieval flow, but the guide does not establish whether TV-side authorization persists or document a supported revocation route. Treat any persistent TV-side authorization as **recovery unverified / irreversible** until verified. |
| Extend session | Changes the remaining Developer Mode session time. Use only the TV's **EXTEND** control after separate approval; inventory must not renew it. |

Before each operation, record the original state, capture what is accessible, state coverage gaps, explain what cannot be restored, document and safely validate the recovery route, then obtain approval for that specific operation. Do not classify any operation as fully reversible based on these notes alone.

## Install and activate Developer Mode

1. Confirm the private Distrobox CLI home is outside the repository, mode `0700`; verify its profile/key paths and permissions as described in [webOS CLI environment](webos-cli-environment.md). This workstation preparation does not connect to the TV.
2. With the owner present, install the official Developer Mode app from LG Apps only if needed and only after its separate approval. Do not assume installation is reversible; see operation boundaries above.
3. Sign in to the Developer Mode app using the owner's LG Developer account directly on the TV. Never collect or record the account password.
4. Record the app's current Dev Mode status and remaining session time. Activate only after separate approval. Activation changes device state and LG documents that it reboots the TV. Wait for it to return, confirm ordinary startup and input operation, then repeat the same baseline tests from [pre-activation-baseline.md](pre-activation-baseline.md) and record a new date/result beside each original result.
5. If any previously passing protected function now fails, stop further device changes. Record the failure, compare with the baseline, and investigate recovery before proceeding.
6. Do not install, launch, or remove any other app in this slice.

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
- To deactivate, first record session status and complete any separately approved capture. On the TV, open the Developer Mode app, review the current on-screen warning and consequences, then use its Dev Mode Status control to disable the mode only with separate approval. Confirm the TV returns to ordinary operation, verify the displayed status, and repeat the baseline regression checks. If the screen warns of app removal or other data loss, stop unless that consequence was explicitly approved. LG documentation describes expiry/disable behavior; exact effects of intentional deactivation must be checked against the current on-screen confirmation before proceeding.
- Removing the Developer Mode app itself is a separate TV mutation; do not do so as cleanup without separate approval and a recovery review.

No known route restores sideloaded app-local data after Dev Mode disables. Do not rely on factory reset, firmware downgrade, or a generic TV backup as recovery.

## Post-activation checks

Without changing app/settings state, repeat every applicable check in [pre-activation-baseline.md](pre-activation-baseline.md), using the original expected behavior for comparison. This includes:

- Each used port, HDMI 1, HDMI 2, and HDMI 3 independently; its connected gaming device, picture/audio output, input switching, Game Mode, ALLM, HDR, and HDMI-CEC / Simplink where supported or used.
- Existing audio configuration including ARC/eARC where used; Wi-Fi/Ethernet, internet, local network/discovery, Emby server discovery and playback; Raspberry Pi Steam Link and required Bluetooth behavior where used.
- BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV launch and playback.
- Current privacy and advertising settings, without changing them, plus Developer Mode status/session display, normal startup, and normal operation after deactivation.

Treat a failed check as a baseline finding. Do not proceed to application mutation or firmware change.

Sources: [LG Developer Mode setup, connection and session rules](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app), [LG CLI guide and command references](https://webostv.developer.lge.com/develop/tools/cli-dev-guide), [project backup and recovery policy](recovery-policy.md).
