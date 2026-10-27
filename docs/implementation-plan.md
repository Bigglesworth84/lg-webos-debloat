# Implementation plan

Native configuration comes before Developer Mode. DNS filtering is deferred until native results are measured. Rooting is not in the current plan.

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

After the native settings results are reviewed and a separate TV-connection slice is approved:

1. Review LG's [Developer Mode setup and expiry rules](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app).
2. Prepare webOS CLI in an isolated Bazzite environment or use a current [webOS Dev Manager Linux AppImage](https://github.com/webosbrew/dev-manager-desktop/releases).
3. Pair only on the user's approval, then export an inventory with official read-only CLI list commands. Treat the result as potentially incomplete.
4. Plan session renewal before installing any sideloaded app; LG says Developer Mode apps are removed when the session expires and Developer Mode disables.

No app install or removal is included in this slice. Rooting remains deferred. YouTube AdFree remains unverified on this TV.

## Milestones and acceptance criteria

| Milestone | Scope | Acceptance criteria |
|---|---|---|
| 001 — Discovery | Baseline, supported controls, compatibility, read-only inventory plan | Model/firmware and manual settings recorded; research sources current; inventory procedure is read-only |
| 002 — Native configuration | Promotion, recommendation, privacy, startup, Home organization | Each change recorded and reversible; protected apps and input functions validated |
| 003 — Developer Mode | Approved pairing and inventory | Renewal plan recorded; inventory exported; no removability inference |
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
