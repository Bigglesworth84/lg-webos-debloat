# Rollback and recovery

The native settings below were configured by the owner. The Milestone 003 Slice 1 change adds offline inventory tooling and a local rootless Distrobox CLI environment; no TV setting, firmware, app, or network configuration was changed by this project. See [recovery policy](recovery-policy.md) for the mandatory backup-first gate and recovery classification.

## Recovery status for the recorded native settings

These settings have documented on-device controls, so the intended rollback is manual restoration through those settings. The procedure has not been independently performed or verified by this project. Before any future change, capture each current value and establish the exact menu path shown by the TV. Reversing consent choices may require accepting an agreement; review its on-screen terms before doing so.

The Home observations (LG Channels promotional row replaced by TV function shortcuts, introductory banner remaining, protected apps visible) are not backup artefacts and have no separately verified restore function. Revisit the relevant Home and agreement settings to restore the desired state; confirm the result manually.

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

No pairing or sideloading is in scope. LG states Developer Mode expires and apps installed through Developer Mode are uninstalled when the session disables. Before a future install, document how to renew the session and reinstall the app. Preserve official app reinstall instructions before replacing an app. Reinstalling does not guarantee restoration of app-local data.

## Application removal

No application removal is approved or implemented. Unknown apps and system components remain protected by default. A future slice must establish the exact package, purpose, supported removal permissions, reinstall route, and app-data consequences before asking for per-app approval.

## Rooting

Rooting is deferred. No verified recovery or downgrade path is established for this exact model and firmware. Do not treat factory reset as guaranteed root recovery.

## Offline workstation tooling

The rootless `webos-cli-m003` Distrobox can be removed with `scripts/webos-cli-env.sh remove`. This removes the container but intentionally keeps its custom home under `${XDG_DATA_HOME:-$HOME/.local/share}/lg-webos-cli-home`; inspect it before deleting it because a future approved pairing would place profiles and SSH keys there. This slice created no real device profile or key. The user-local Distrobox executable was installed under `~/.local/bin` because it was absent on the workstation; removing the box does not remove that host tool. No TV recovery action is relevant to this workstation setup.
