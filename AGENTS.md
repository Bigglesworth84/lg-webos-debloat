# Operating rules

This repository supports a controlled LG webOS optimisation project. Use the following rules for all work:

- Prefer supported native webOS settings before Developer Mode or community modifications. Rooting is deferred.
- Treat the baseline in `docs/hardware.md` as user-reported until someone inspects the TV manually. Do not connect to the TV or change settings unless the user explicitly authorises that action for a later slice.
- Preserve BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV. Preserve HDMI 1, HDMI 2, and HDMI 3 independently, including each connected gaming device, input switching, Game Mode, ALLM, HDR where supported, and HDMI-CEC / Simplink. Preserve the existing audio configuration, including ARC/eARC where used; Wi-Fi and Ethernet; internet and local-network connectivity and discovery; Emby server discovery and media playback; Bluetooth; and Raspberry Pi Steam Link functionality.
- Protect unknown applications and all system components by default. An inventory is not proof that an app is removable.
- Do not create application removal automation in the current project phase. Any future removal plan must use individually reviewed package IDs and an explicit user-approved allowlist; never use a broad blacklist or pattern-based deletion.
- Keep DNS filtering deferred until native settings have been evaluated.
- Do not record credentials, tokens, serial numbers, or unrelated personal data.
- Verify model-specific claims against current LG or project documentation. Label community reports, assumptions, and unverified compatibility clearly.
- Before future sideloading, document Developer Mode expiry and a renewal plan. Do not assume sideloaded apps persist after the session expires.
- Keep each change reversible where possible, document its validation, and update `docs/rollback.md` when a new operation is approved.

## Backup-first change control

Before proposing or performing any state-changing operation, complete all of these steps:

1. Identify the exact device and firmware from an owner-confirmed or directly observed source. Treat older baseline notes as unverified until checked.
2. Capture the accessible current state and state what the capture cannot see.
3. Create a timestamped baseline or backup before changing anything.
4. Establish whether restoration is technically supported for each captured item.
5. Document exact recovery steps and the consequences, including possible data loss.
6. Verify the recovery route as far as safely possible without changing the TV.
7. Obtain explicit user approval for the specific change after presenting the backup and recovery information.

Classify each operation as one of: **fully reversible through a verified supported interface**, **manually reversible through documented settings**, **recoverable through application reinstallation, potentially with data loss**, **partially reversible**, or **recovery unverified / irreversible**. Never claim full reversibility without a verified restoration. Firmware downgrade, factory reset, and root removal are not guaranteed recovery methods. Operations with unverified or irreversible recovery require separate explicit approval and are excluded from routine automation.

## Protected state and operational safety

- Never remove BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, or Apple TV through generic automation. YouTube is the only proposed replacement and still needs separate explicit approval.
- Protect unknown applications and all webOS system components by default. Inventory results do not prove that an item is safe or supported to remove.
- Preserve HDMI, HDR, HDMI-CEC, audio, network, DRM, Bluetooth, and Raspberry Pi Steam Link functionality.
- Prefer read-only discovery and supported native configuration. Do not use wildcard package removal, automatically delete system files, or run undocumented shell commands against the TV.
- Do not automatically update firmware or perform recovery involving firmware flashing or rooting. Do not assume Developer Mode provides a system-level backup.
- Keep backups out of Git by default and restrict local permissions. Do not collect credentials, tokens, serial numbers, account details, or unrelated personal data.
- Device-facing inventory, backup, restore, or verification commands may be added only after the relevant supported interfaces, permissions, coverage, and restore behavior are established. Dry-run is the default for any future restore tooling; each operation must be selected explicitly.
- If an operation breaks an established working feature, stop further device changes until the regression is investigated and the recovery status is reassessed.

Read [`docs/recovery-policy.md`](docs/recovery-policy.md) before designing or approving backup, restore, inventory, or verification tooling. Record each approved operation and its recovery status in [`docs/change-log.md`](docs/change-log.md), and maintain concrete undo steps in [`docs/rollback.md`](docs/rollback.md).
