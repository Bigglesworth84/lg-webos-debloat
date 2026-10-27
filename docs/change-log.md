# Change log

Record approved device operations here only after they occur. Include date, device/firmware source, operation, captured baseline reference (without secrets), recovery classification, approval, validation, and any limitations. Put actionable undo steps in [rollback notes](rollback.md).

## 2026-10-27 — Native settings reported by owner

- **Device/firmware:** LG 55UP81006LR; webOS 6.5.3-47; firmware 03.53.45; owner manually inspected and confirmed these values.
- **Operation:** Owner configured startup, Home promotion/recommendations, viewing and voice agreements, advertising/data-partner/marketing choices, and CMP advertising consent. Exact final values and Home observations are recorded in [hardware and baseline](hardware.md).
- **Approval/source:** Reported as completed by the owner; the project did not connect to or change the TV.
- **Recovery classification:** Manually reversible through documented settings is the intended classification. Restoration has not been independently verified by this project; review each on-screen control and agreement before restoring consent.
- **Validation:** Owner observed that the LG Channels promotional programme row disappeared and TV function shortcuts replaced it. The introductory banner remains and protected apps remain visible. App launch/playback and protected-function regression checks are pending.
- **Backup:** No machine-readable baseline or device backup was created. No supported device-state export or restore interface is established.

## 2026-10-27 — Recovery framework documentation

- **Operation:** Repository documentation and policy only; no device-facing action.
- **Validation:** Documentation and policy consistency reviewed; no device backup, restore, or inventory capability is claimed.

## 2026-10-27 — Developer Mode connection and CLI discovery (owner-confirmed)

- **Device/source:** Owner manually confirmed LG 55UP81006LR, webOS TV 6.5.3-47 (kisscurl-koli), firmware 03.53.45, and Wi-Fi. The owner reports CLI `modelName` 55UP81006LR, SDK 6.5.3, firmware 03.53.45, and board K7LP_DVB_EU.
- **Operations:** After separate owner approval, the official Developer Mode app was installed and enabled, the TV rebooted successfully, and SSH pairing completed. The owner reports the Key Server is now off. The read-only CLI system-information request succeeded. App listing was attempted using `ares-install --device lounge-tv --list` and `--listfull`.
- **Inventory result:** Both listing commands returned zero application records; `--listfull` exited with status 0. Classify as **successful CLI execution; zero application records returned; full installed-app catalogue coverage unknown**. The reason for the empty output is not established. This is not evidence of an empty catalogue, a complete inventory, or absence of LG Store/built-in apps.
- **Validation:** The owner reports normal overall operation after activation, Wi-Fi and local-network connectivity, Emby server access/playback, and protected streaming applications working. Detailed individual checks remain unrecorded unless listed in [hardware and baseline](hardware.md). No app was sideloaded, replaced, or removed.
- **Recovery classification:** Developer Mode activation is partially reversible through its on-device status control, with sideloaded apps at risk on expiry/deactivation. SSH pairing's TV-side authorization revocation remains unverified. The read-only system information and app listing are observations, not restorable backups.
- **Backup:** No machine-readable device backup, complete installed-app catalogue, configuration export, or restorable TV-state artifact was created.
- **Approval/source:** These are owner-reported completed actions that had separate explicit approval. No TV action was taken as part of the current documentation/PATH implementation slice.

## 2026-10-27 — M003 Slice 3A documentation and workstation tooling

- **Operation:** Reconciled the project documentation with the owner-reported Developer Mode, pairing, system-information, and zero-record app-list observations. Added an idempotent project-managed PATH activation helper and Distrobox `shell`/`run` entry behavior for the pinned Node and webOS CLI environment.
- **Device/firmware:** No device command or connection was made in this slice; no TV state changed.
- **Recovery classification:** Workstation environment change only. `scripts/webos-cli-env.sh remove` continues to remove the container while retaining the private CLI home. No TV backup or restore capability is claimed.
- **Validation:** All 36 offline unit tests passed. Bash syntax, Python compilation, relative Markdown links, and `git diff --check` passed.
