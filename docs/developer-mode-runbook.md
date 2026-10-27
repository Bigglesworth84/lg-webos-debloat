# Developer Mode and read-only inventory runbook

**Status: Developer Mode and SSH pairing completed (owner-confirmed).** The owner reports the official Developer Mode app was installed, Developer Mode enabled after explicit approval, the TV rebooted successfully, SSH pairing completed after separate approval, and the Key Server was then turned off. These completed approvals do not authorize new device operations. Any future device-facing slice needs separate explicit approval after the backup-first gate in [recovery-policy.md](recovery-policy.md) is complete.

## Baseline and recovery gate for future state changes

1. For any future state change, inspect the current set and firmware on the TV first. The owner-confirmed values in [hardware.md](hardware.md) are dated observations, not confirmation that the state has not changed. CLI metadata supplements but does not replace physical-device confirmation.
2. Complete or update [the manual baseline](pre-activation-baseline.md) with the owner before changing state. It records behavior but cannot restore settings, app-private data, account state, or a complete system image. No supported machine-readable TV backup or general restore interface is established.
3. Present the operation-specific recovery classification, accessible-state capture, coverage gaps, exact recovery steps and consequences, and verify the recovery route as far as possible without changing the TV. Developer Mode expiry/deactivation can uninstall Developer Mode apps; no complete backup or guaranteed factory-reset/downgrade recovery exists.
4. Obtain and record separate explicit approval for each proposed operation. Past approvals for installation, activation, pairing, or read-only discovery do not approve future operations.
5. Leave unexplained baseline failures unresolved before proceeding. Keep unsupported or unobserved functionality marked Not applicable with a reason or Not tested, respectively.

## Operation recovery boundaries

| Operation | State change and recovery status |
|---|---|
| Install Developer Mode app | Changes installed-app state. This exact model's removal/reinstall route and any app data consequences have not been verified; classify **recovery unverified / irreversible** until documented. |
| Enable Developer Mode | Reboots the TV and enables a time-limited developer session. Manual status control is the intended deactivation route; classify **partially reversible** because deactivation can remove Developer Mode apps and local app data may be lost. |
| SSH pairing / key retrieval | Writes a local device profile and private key. LG documents the key retrieval flow, but the guide does not establish whether TV-side authorization persists or document a supported revocation route. Treat any persistent TV-side authorization as **recovery unverified / irreversible** until verified. |
| Extend session | Changes the remaining Developer Mode session time. Use only the TV's **EXTEND** control after separate approval; inventory must not renew it. |

Before each operation, record the original state, capture what is accessible, state coverage gaps, explain what cannot be restored, document and safely validate the recovery route, then obtain approval for that specific operation. Do not classify any operation as fully reversible based on these notes alone.

## Completed setup (owner-reported)

The owner reports that the CLI environment uses a private Distrobox home outside the repository, and that the official Developer Mode app was installed and enabled after separate approval. The TV rebooted successfully. SSH pairing/key retrieval completed after separate approval; the Key Server was later turned off. The owner reports no app has been sideloaded, replaced, or removed. Do not repeat setup or pairing steps unless a future, separately approved slice requires them. Never record credentials, passphrases, keys, or actual network addresses.

## SSH pairing and read-only inventory

1. Have the owner open the Developer Mode app's Key Server control. Use a manually verified TV address from the TV's network status; do not scan the LAN.
2. Add the target with an explicit alias, correct observed address, port `9922`, and user `prisoner`, for example `ares-setup-device --add <alias> --info "host=<observed-address>" --info "port=9922" --info "username=prisoner"`. This changes the workstation-side profile only. Keep the profile under the isolated custom home.
3. After separate pairing approval, retrieve the key with `ares-novacom --getkey --device <alias>` while the owner is present to enter the short-lived passphrase at the interactive prompt. Never put the passphrase in shell history, command arguments, fixtures or logs. Verify that the CLI key is `0600` and profile data is `0600` within owner-only `0700` directories. Treat persistent TV-side key authorization and its revocation as unverified unless LG documents the lifecycle.
4. The owner reports that `ares-device --system-info --device lounge-tv` succeeded. The owner also reports that `ares-install --device lounge-tv --list` and `--listfull` returned no application records, with `--listfull` exit status 0. Classify this as **successful CLI execution; zero application records returned; full installed-app catalogue coverage unknown**. Its precise cause has not been established; do not interpret it as an empty catalogue.
5. Store raw diagnostics in a private local directory separate from any redacted report. Redact serials, IP/MAC addresses, account values, passphrases, tokens, key material, and unrelated personal data before review or sharing.
6. No live-capture adapter or machine-readable device snapshot was created. A future approved capture must include UTC timestamps, exact tool/runtime versions, coverage gaps, artifact classifications and SHA-256 hashes; label metadata informational and app output read-only; record no restorable TV-state artifacts. Inventory does not establish removability or complete system coverage.

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
