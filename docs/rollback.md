# Rollback and recovery

This slice changes repository documentation only. No TV setting, firmware, app, or network configuration has been changed.

## Native settings

Record each original value before changing it. To reverse a native optimization, return to the same menu and restore that value:

- **Home Promotion:** turn it back on if the original state was on.
- **Content Recommendation:** turn it back on if the original state was on.
- **Power On Screen:** restore Home or Recent Input to the recorded original choice.
- **Privacy agreements:** use the TV's agreement/settings screen to re-enable the recorded option where available. Availability and effects depend on the agreement and region.
- **Home shortcuts:** restore recorded application order or make hidden shortcuts visible again.

After rollback, validate the Home screen, each protected streaming app, Emby local server discovery/playback, HDMI switching, CEC, HDR, Game Mode, audio, network, and Steam Link behavior relevant to the changed setting.

## Firmware

No firmware change is in scope. Firmware release notes currently state that 03.53.46 fixes minor bugs and do not document a rollback or downgrade procedure. Treat firmware changes as non-reversible for planning purposes unless LG documents a model-specific recovery path; do not rely on downgrading.

## Developer Mode and sideloaded apps

No pairing or sideloading is in scope. LG states Developer Mode expires and apps installed through Developer Mode are uninstalled when the session disables. Before a future install, document how to renew the session and reinstall the app. Preserve official app reinstall instructions before replacing an app. Reinstalling does not guarantee restoration of app-local data.

## Application removal

No application removal is approved or implemented. Unknown apps and system components remain protected by default. A future slice must establish the exact package, purpose, supported removal permissions, reinstall route, and app-data consequences before asking for per-app approval.

## Rooting

Rooting is deferred. No verified recovery or downgrade path is established for this exact model and firmware. Do not treat factory reset as guaranteed root recovery.
