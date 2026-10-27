# Implementation plan

Native configuration comes before Developer Mode. The owner reports the initial native configuration complete; application and protected-function regression checks remain pending. DNS filtering is deferred until native results are measured. Rooting is not in the current plan. Every future state change is gated by the [backup and recovery policy](recovery-policy.md).

## Completed native configuration — owner reported

On 27 October 2026, the owner manually inspected and configured the settings recorded in [hardware.md](hardware.md). The owner observed the LG Channels promotional programme row disappear after Content Recommendation was disabled; TV function shortcuts took its place. The introductory banner remained, as did protected app tiles. These are owner observations, not project-side verification. Application launch/playback and HDMI, CEC, HDR, Game Mode, audio, network, Bluetooth, and Steam Link regression checks remain open.

No machine-readable backup was captured. There is no confirmed device-facing backup or restore interface. The current project slice records results and defines the recovery framework; it does not connect to or modify the TV.

## Native optimisation procedure

Before each change, record the current value and date in [the baseline checklist](hardware.md). Change one setting at a time, then check the listed criteria before continuing.

### 1. Disable Home Promotion

- **Menu path:** `Settings → All Settings → General → System → Additional Settings → Home Settings → Home Promotion → Off` ([LG guide](https://www.lg.com/uk/support/product-support/troubleshoot/help-library/cs-CT00008333-20153529296869/)). Menu labels may vary slightly by update or region.
- **Outcome:** remove the promotional ad at the top of Home; LG says the main image is shown instead.
- **Possible side effects:** changes Home presentation; no app, input, or streaming change is expected.
- **Rollback:** return to Home Promotion and turn it on.
- **Validate:** revisit Home and confirm the top ad is absent; verify protected apps and HDMI inputs still launch.

### 2. Disable Content Recommendation

- **Menu path:** `Settings → All Settings → General → System → Additional Settings → Home Settings → Content Recommendation → Off` ([LG guide](https://www.lg.com/uk/support/product-support/troubleshoot/help-library/cs-CT00008333-20153529296869/)).
- **Outcome:** suppress recommendation content described by LG, including trending shows.
- **Possible side effects:** fewer suggested titles or discovery prompts. This does **not** guarantee removal of the LG Channels row or all promotional content.
- **Rollback:** return to Content Recommendation and turn it on.
- **Validate:** inspect Home after returning to it; record which recommendation sections changed and whether LG Channels remains visible.

### 3. Review privacy and advertising controls

- **Menu path:** not fixed here. Open Settings and review the TV's current User Agreements, privacy, advertising, and any Live Plus / Viewing Information options. LG says optional agreements and controls exist, but exact names vary by model, software, and region. [LG privacy statement](https://www.lg.com/us/newsroom/corporate/statement-understanding-privacy-on-lg-smart-tvs)
- **Outcome:** make an informed choice about ACR/viewing information, interest-based advertising, and other optional collection.
- **Possible side effects:** agreement-dependent voice or recommendation features may be affected; check each on-screen explanation before withdrawing consent.
- **Rollback:** re-enable the relevant setting or re-accept the agreement using the TV's displayed controls, where available.
- **Validate:** record the exact label and state; confirm voice features, app access, and Home behavior that matter to the owner.

### 4. Evaluate Recent Input startup

- **Menu path:** `Settings → All Settings → General → System → Additional Settings → Home Settings → Power On Screen → Home/Recent Input` ([LG guide](https://www.lg.com/uk/support/product-support/troubleshoot/help-library/cs-CT00008333-20153529296869/)).
- **Outcome:** if Recent Input is selected, LG says the TV opens to the last watched external input instead of Home.
- **Possible side effects:** the TV may start on a source different from the preferred app or broadcast.
- **Rollback:** select Home (the guide labels the choice `Home/Recent Input`).
- **Validate:** perform a normal power cycle and confirm the desired startup destination, including the Steam Link HDMI source if that was last used.

### 5. Investigate LG Channels visibility

- **Menu path:** first inspect Home and the app list; record where LG Channels appears. The cited guide does not provide a verified LG Channels row-removal control for this exact set.
- **Outcome:** understand whether it is a channel row, recommendation shelf, app tile, or service shortcut before changing anything.
- **Possible side effects:** hiding or removing the app may affect access to the service; no removal is approved.
- **Rollback:** restore the tile or shortcut using the same Home/app organization controls if available.
- **Validate:** confirm whether the row remains after recommendation changes. Do not infer it will disappear.

### 6. Preserve preferred apps

- **Menu path:** use Home's visible app organization controls if present to reorder or hide shortcuts. Exact controls require manual inspection.
- **Outcome:** keep protected streaming apps easy to reach while reducing visible clutter.
- **Possible side effects:** changing shortcut order affects navigation only; hiding an app may make it less discoverable.
- **Rollback:** restore the recorded order or unhide the shortcut.
- **Validate:** launch BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV; verify Emby server discovery and playback.

## Future Developer Mode preparation

The next implementation slice is preparation and read-only discovery only. Before any TV connection or Developer Mode activation, obtain separate explicit approval and apply the backup-first gate in [recovery-policy.md](recovery-policy.md). The work should:

1. Review LG's [official Developer Mode setup and expiry rules](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app) and document expiration behavior.
2. Prepare a secure Bazzite-to-TV connection using an isolated CLI environment; record credential handling without storing keys or tokens in Git.
3. Identify the device only after approval, then export a read-only application inventory. State that it may be incomplete and does not establish removability.
4. Investigate supported configuration export and restoration mechanisms; document unsupported state rather than implying it is backed up.
5. Document and verify the supported session renewal procedure before any sideloading. Do not assume sideloaded apps persist after session expiry.

No TV connection or Developer Mode activation is authorized in the current slice. No app install or removal is included in the next discovery milestone. Rooting remains deferred. YouTube AdFree remains unverified on this TV.

## Milestone 003, Slice 1 — offline tooling foundation

The offline tooling foundation is implemented on branch `codex/m003-offline-inventory`. It uses the official `@webos-tools/cli` 3.2.6 with Node 24.22.1 in a rootless Ubuntu Distrobox, has a custom home outside the repository, and mounts the repository read-only. Distrobox is not a security boundary. The checked-in inventory utility is offline-only: it parses sanitized fixture output, creates timestamped private manifests, checks SHA-256 integrity, and builds (but never executes) a strict future read-command allowlist.

No TV was contacted and no Developer Mode action was taken. There are no restorable TV-state artifacts. CLI version/help commands were run in the Distrobox under Node 24.22.1; a no-device CLI help smoke test also passed under Node 22.23.4. See [offline environment notes](webos-cli-environment.md) and the [future manual runbook](developer-mode-runbook.md).

## Milestone 003, Slice 2 — pre-activation baseline preparation

- [x] Added a manual baseline for HDMI 1, HDMI 2, and HDMI 3 independently, gaming, input switching, Game Mode/ALLM/HDR/CEC, audio/ARC/eARC, networking, Emby, protected streaming apps, Bluetooth, and Steam Link.
- [x] Added a repeatable result format with every new test initially **Not tested** and no hardware or app result claimed as passing.
- [x] Recorded previously confirmed privacy/advertising values as reference only; the checklist directs the owner to recheck them without changing them.
- [x] Documented manual baseline coverage limits, Developer Mode deactivation, reboot and session-expiry consequences, separate approvals, readiness gates, and post-activation comparison.
- [x] No TV was contacted or changed; no device-facing mutation script was added.

## Milestones and acceptance criteria

| Milestone | Scope | Acceptance criteria |
|---|---|---|
| 001 — Discovery | Baseline, supported controls, compatibility, read-only inventory plan | Model/firmware and manual settings recorded; research sources current; inventory procedure is read-only |
| 002 — Native configuration | Owner-reported promotion, recommendation, privacy, startup and Home results; regression validation | Results and observations recorded; app/function tests explicitly marked pending |
| 003 — Developer Mode discovery | Separately approved setup, secure connection, read-only inventory, configuration export investigation | Expiry/renewal plan documented; inventory coverage limits stated; supportable backup and restore boundaries established; no removability inference |
| 004 — YouTube AdFree | Separately approved app swap and validation | Sign-in, playback, ad blocking, SponsorBlock, and persistence observed; rollback path ready |
| 005 — Application review | Individual removable-app decisions | Protected apps excluded; every proposed package individually identified and approved |
| 006 — Advanced modifications | Reassess rooting only if a substantial need remains | Exact model/firmware support and recovery understood; separate explicit approval obtained |
| 007 — Final validation | Streaming, Emby, inputs, game, picture, audio, network | Every protected function passes and limitations are documented |

## Slice 1 acceptance

- [x] Foundation documents created, with initial facts separated from manual inspection items.
- [x] Native procedure includes menu paths where documented, outcomes, side effects, rollback, and validation.
- [x] Protected apps and system components are protected by default; no removal automation exists.
- [x] Firmware 03.53.46 notes and exact model applicability are recorded with uncertainty stated.
- [x] No TV connection or configuration change is part of this slice.

## Documentation and recovery slice acceptance

- [x] Backup-first approval gate, recovery classifications, protected state, and safety requirements recorded in `AGENTS.md` and `docs/recovery-policy.md`.
- [x] Owner-reported native results, observations, and untested functionality distinguished in `docs/hardware.md` and the change log.
- [x] Backups are excluded from Git by default; only `backups/.gitkeep` is committed.
- [x] Protected-app policy is machine-readable, with no package IDs or removal allowlist.
- [x] No device-facing inventory, backup, restore, verification, or mutation scripts claim unverified capabilities.
- [x] Developer Mode discovery scope and prerequisites are documented; no TV connection or activation is authorized here.
