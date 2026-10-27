# Rollback and recovery

The native settings below were configured by the owner. Milestone 003 Slice 1 added offline inventory tooling and a local rootless Distrobox CLI environment; that slice made no TV setting, firmware, app, or network change. The owner later reports Developer Mode activation, SSH pairing, and read-only CLI discovery after separate approvals. No app was sideloaded, replaced, or removed, and no restorable device backup exists. See [recovery policy](recovery-policy.md) for the mandatory backup-first gate and recovery classification.

## Recovery status for the recorded native settings

These settings have documented on-device controls, so the intended rollback is manual restoration through those settings. The procedure has not been independently performed or verified by this project. Before any future change, capture each current value and establish the exact menu path shown by the TV. Reversing consent choices may require accepting an agreement; review its on-screen terms before doing so.

The Home observations (LG Channels promotional row replaced by TV function shortcuts, introductory banner remaining, protected apps visible) are not backup artefacts and have no separately verified restore function. Revisit the relevant Home and agreement settings to restore the desired state; confirm the result manually.

## Pre-activation baseline and recovery limits

The [manual baseline](pre-activation-baseline.md) is an observation record, not a backup or restore point. It captures behavior for HDMI 1, HDMI 2, HDMI 3, gaming, audio, network, Emby, protected apps, and privacy/advertising settings. It cannot recover settings, app-private data, account state, or a complete system image. No supported general TV restore interface is established, and the CLI's zero-record app-list response is not a full-system backup or proof of an empty catalogue.

An activation or pairing regression must halt further device changes. Compare each post-activation result with the dated baseline and investigate before doing anything else. Keep baseline notes free of passwords, tokens, serial numbers, account details, public IP addresses, MAC addresses, and network credentials.

## Native settings

Record each original value before changing it. To reverse a native optimization, return to the same menu and restore that value:

- **Home Promotion:** turn it back on if the original state was on.
- **Content Recommendation:** turn it back on if the original state was on.
- **Power On Screen:** restore Home or Recent Input to the recorded original choice.
- **Privacy agreements:** use the TV's agreement/settings screen to re-enable the recorded option where available. Availability and effects depend on the agreement and region.
- **Home shortcuts:** restore recorded application order or make hidden shortcuts visible again.

After rollback, validate the Home screen, each protected streaming app, Emby local server discovery/playback, HDMI switching, CEC, HDR, Game Mode, audio, network, and Steam Link behavior relevant to the changed setting.

## Firmware

No firmware change is in scope. Current firmware 03.53.45 and the displayed 03.53.46 offer are owner-confirmed. Release notes state that 03.53.46 fixes minor bugs and do not document a rollback or downgrade procedure. Treat firmware changes as recovery-unverified for planning purposes unless LG documents and supports a model-specific recovery path; do not rely on downgrading or factory reset.

## Developer Mode and sideloaded apps

Developer Mode activation and SSH pairing are reported completed after separate approval. Installing the Developer Mode app changes installed-app state; its removal/reinstall recovery is unverified for this exact model. Enabling Developer Mode reboots the TV and is **partially reversible** through the Developer Mode app's status control, but deactivation or expiry can uninstall sideloaded apps. Recovery of sideloaded app-local data is **recovery unverified / irreversible** absent evidence. SSH pairing writes local profile/key material and may persist TV-side authorization; until a supported revocation route is established, classify that effect as **recovery unverified / irreversible**. Any future renewal, deactivation, pairing change, or sideload requires separate explicit approval after current state and consequences are presented.

For an approved deactivation, first record Developer Mode status and session time. On the TV, open the Developer Mode app, read its current warning, and use its Dev Mode Status control only after explicit approval of any stated app/data loss. Confirm ordinary startup and disabled status, then repeat all applicable checks in [pre-activation-baseline.md](pre-activation-baseline.md): each used HDMI port, gaming, picture/audio, switching, Game Mode/ALLM/HDR/CEC where supported, ARC/eARC where used, network, Emby, and all protected streaming apps. Record the result and stop further device changes if an established feature fails. LG documents expiry/disable behavior; verify the exact consequences shown by the TV before intentional deactivation. No known route restores sideloaded app-local data after Developer Mode disables.

Before any future sideloading, document and validate the Developer Mode renewal procedure and potential app reinstall requirements. Reinstallation does not guarantee restoration of app-local data. Do not rely on factory reset or firmware downgrade as recovery.

## Application removal

No application removal is approved or implemented. Unknown apps and system components remain protected by default. A future slice must establish the exact package, purpose, supported removal permissions, reinstall route, and app-data consequences before asking for per-app approval.

## Rooting

Rooting is deferred. No verified recovery or downgrade path is established for this exact model and firmware. Do not treat factory reset as guaranteed root recovery.

## Offline workstation tooling

The rootless `webos-cli-m003` Distrobox can be removed with `scripts/webos-cli-env.sh remove`. This removes the container but intentionally keeps its custom home under `${XDG_DATA_HOME:-$HOME/.local/share}/lg-webos-cli-home`; inspect it before deleting it because a future approved pairing would place profiles and SSH keys there. This slice created no real device profile or key. The user-local Distrobox executable was installed under `~/.local/bin` because it was absent on the workstation; removing the box does not remove that host tool. No TV recovery action is relevant to this workstation setup.
