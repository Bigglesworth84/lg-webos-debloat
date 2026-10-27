# Operating rules

This repository supports a controlled LG webOS optimisation project. Use the following rules for all work:

- Prefer supported native webOS settings before Developer Mode or community modifications. Rooting is deferred.
- Treat the baseline in `docs/hardware.md` as user-reported until someone inspects the TV manually. Do not connect to the TV or change settings unless the user explicitly authorises that action for a later slice.
- Preserve BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV. Preserve HDMI, HDMI-CEC, Game Mode, HDR, audio, network, Bluetooth, and Raspberry Pi Steam Link functionality.
- Protect unknown applications and all system components by default. An inventory is not proof that an app is removable.
- Do not create application removal automation in the current project phase. Any future removal plan must use individually reviewed package IDs and an explicit user-approved allowlist; never use a broad blacklist or pattern-based deletion.
- Keep DNS filtering deferred until native settings have been evaluated.
- Do not record credentials, tokens, serial numbers, or unrelated personal data.
- Verify model-specific claims against current LG or project documentation. Label community reports, assumptions, and unverified compatibility clearly.
- Before future sideloading, document Developer Mode expiry and a renewal plan. Do not assume sideloaded apps persist after the session expires.
- Keep each change reversible where possible, document its validation, and update `docs/rollback.md` when a new operation is approved.
