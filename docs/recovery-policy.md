# Backup and recovery policy

This policy governs future state-changing work on the LG webOS device. It is a design and approval gate, not evidence that a device backup exists. The owner reports a successful official CLI connection and system-information capture, plus app-list attempts that returned no records. No complete app catalogue, configuration export, or machine-readable restorable TV backup has been captured.

## Change gate

Before any state change, the proposal must identify the exact device and firmware, capture accessible current state, create a timestamped baseline, state coverage gaps, document supported restoration steps and possible data loss, and verify the recovery route as far as safely possible. Present this information and obtain explicit approval for the specific operation before acting. If no supported recovery route is established, classify recovery as unverified or irreversible and require separate explicit approval; exclude the operation from routine automation.

Use one operation-level recovery classification:

| Classification | Meaning |
|---|---|
| Fully reversible through a verified supported interface | The documented supported restore operation was performed or otherwise verified to restore the selected state. |
| Manually reversible through documented settings | The owner can restore the prior state through documented on-device controls; automated restoration is not established. |
| Recoverable through application reinstallation, potentially with data loss | A supported reinstall route is known, but app-local data or configuration may not return. |
| Partially reversible | Some state can be restored, with known limits recorded. |
| Recovery unverified / irreversible | No supported restoration is established, or recovery may be impossible. |

Firmware downgrade, factory reset, rooting, and root removal are not guaranteed recovery methods. No operation is “fully reversible” merely because a backup file exists.

## Data and local storage

Future local snapshots belong under `backups/`, which is ignored by Git. Keep only the committed `.gitkeep` scaffold in the repository. Create a private snapshot directory with restrictive permissions (for example, mode `0700`) and files (for example, mode `0600`). Do not sync or publish snapshots unless separately reviewed and approved.

Snapshot creation accepts only an output root owned by the current user, with owner write/search access and no group/other access. Existing roots are never chmodded: unsuitable permissions, ownership, non-directories, or symlinked path components are rejected. Newly created snapshot directories use mode `0700`; files use mode `0600` subject to a more restrictive umask. Keep the root and snapshots on storage with appropriate owner access and encryption at rest where available. Path checks reduce symlink risk but cannot eliminate races from a concurrently modified filesystem.

Collect only fields required to identify compatibility and restore supported state. Do not collect serial numbers, credentials, tokens, account identifiers, network secrets, or app authentication data. Exclude app-private data unless a supported, necessary mechanism is established and separately reviewed.

A future snapshot manifest should describe:

- Capture timestamp and tool/version.
- Model and firmware as observed, with source and confidence.
- Each artifact's path, type, capture status, coverage limitations, and checksum.
- Whether the artifact is a supported restorable backup, a read-only observation, or informational metadata only.
- Compatibility requirements and an explicit recovery classification per operation or state category.

Checksums establish artifact integrity only. They do not establish completeness, authenticity, device compatibility, or restorability.

Parser redaction is best-effort and is not proof that arbitrary input contains no sensitive information. Unknown raw output is never automatically safe to publish. The offline snapshot writer omits raw output and emits parsed records after best-effort redaction, but record fields can still contain unrecognized sensitive values; review the report before sharing. If private diagnostics are added in a later slice, keep them in a separate owner-only location; never mix them with reviewed reports or commit them. Review and redact a copy explicitly before publication.

The `modelName` value from CLI metadata is recorded only as `cli_model_name`; it must not be treated as the physical product model. The target LG 55UP81006LR identification in [hardware.md](hardware.md) is owner-observed. Independent hardware identity verification has not been established by CLI metadata or this offline tooling.

## Framework design

The current tooling foundation is deliberately offline-only: it builds the documented read-command argument vectors but has no device command executor. It parses sanitized fixture output, creates private fixture snapshots, and verifies their manifests. Device-facing execution must wait until supported APIs, permissions, field coverage, restoration behavior, and a separately approved TV slice are established. The intended future interfaces are:

| Capability | Intended behavior | Current status |
|---|---|---|
| Inventory | Read-only device metadata and installed-app listing using explicit commands; export structured data and state incomplete coverage. | Offline parser/snapshot foundation only. Owner reports the CLI system-info command succeeded, while `--list` and `--listfull` returned zero records (`--listfull` exit status 0). Coverage is unknown/incomplete and the reason for empty results is unestablished. No live-capture adapter is implemented. |
| Backup | Timestamped snapshot, metadata, inventory, supported configuration exports, manifest, and checksums; distinguish observations from restorable artifacts. | Fixture snapshot creation only. No confirmed device backup interface or restorable TV state. |
| Restore | Dry-run by default; explicit item selection; verify checksums, device identity, and firmware compatibility; restore only state supported by documented management interfaces; refuse unsupported items. | Not implemented. Restore requests are rejected; no restore interface has been established. |
| Verify | Compare current read-only state with a selected baseline, report changes and gaps, and flag apps/functions needing manual checks. | Not implemented. App inventory completeness and configuration coverage are unknown. |

The current `scripts/webos_inventory.py` has only `capture-fixtures` and `validate` actions. Application parse results include accepted, rejected and total counts when determinable; dropped or malformed records mark the inventory partial, and a valid empty fixture array is distinct from missing or malformed fixture output. That parser distinction does not prove that a live CLI zero-record response is a complete catalogue. `scripts/webos-cli-env.sh` and `scripts/install_webos_cli.sh` manage workstation tooling; they do not execute TV discovery. The allowlist argument builder is not an executor. Do not add a live capture wrapper until exact supported operations, permissions, coverage, and safe failure behavior are established and separately approved. Never hide mutations in inventory, backup, or verification. Do not provide generic bulk restore or removal; app inventory never establishes removability.

LG's public consumer webOS TV Application Manager reference documents launch by a known app ID and checking whether a known app ID exists; it does not document a general installed-app enumeration method. LG staff stated that no general public installed-app listing API was available and that third-party app IDs generally were not public. LG's CLI guide describes `ares-install --list` and `--listfull` as listing installed apps but does not define complete consumer-TV coverage. Therefore the owner-reported empty result is recorded as **successful CLI execution; zero application records returned; full installed-app catalogue coverage unknown**. Its precise cause remains unestablished. Do not infer an empty catalogue or that built-in/LG Store apps are absent.

The webOS OSE Application Manager documents a `listApps` method under the `application.operation` access-control group, but OSE explicitly warns that its APIs are not guaranteed compatible with LG TVs. It is not a supported consumer-TV inventory route. Community SSAP clients may retrieve launch points over a paired local protocol; this is community tooling, not a documented complete or supported inventory interface, and is not approved for routine discovery in this project. A manual owner-confirmed Apps/Home screen list can supplement observations of visible launch points only. See [LG Application Manager](https://webostv.developer.lge.com/develop/references/application-manager), [LG CLI guide](https://webostv.developer.lge.com/develop/tools/cli-dev-guide), [LG forum response](https://forum.webostv.developer.lge.com/t/how-to-get-applist/8616), and [OSE compatibility note](https://www.webosose.org/docs/reference/).

## Current known recovery boundaries

- The recorded native settings have on-device controls and are intended to be manually reversible; this project has not independently exercised restoration. See [rollback notes](rollback.md).
- App installation/removal and app-private data backup/restore support are unverified for this exact model and firmware. Reinstallation may lose local state.
- Firmware downgrade support is unverified. Factory reset is not a guaranteed recovery route.
- Developer Mode inventory will not be assumed to include every system package, configuration value, or user-data item. Developer Mode does not imply a system-level backup. Session expiry removes Developer Mode apps; document and validate renewal before future sideloading.
- Owner reports that all functions continued normally after Developer Mode activation, but no per-feature pass is inferred from that overall observation. The HDMI, network, Emby, and protected-app details and remaining untested checks are recorded in [hardware.md](hardware.md).
- Rooting is deferred; no verified root recovery or removal path is established.

## Security and preservation

`config/protected-apps.json` is the machine-readable preservation policy. No package IDs have been identified or approved for removal. Preserve BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV. Protect unknown apps and all system components by default. YouTube is the only proposed replacement and requires separate explicit approval. Preserve HDMI, HDR, HDMI-CEC, audio, network, DRM, Bluetooth, and Raspberry Pi Steam Link functionality.

Keep backups out of Git. Do not store secrets in source, manifests, or logs. Never use wildcard removal, automatic system-file deletion, undocumented TV shell commands, automatic firmware updates, or automated firmware/root recovery. Prefer supported native settings and read-only discovery.
