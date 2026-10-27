# Hardware and baseline

## Device facts

The device and activation facts below were confirmed by the owner on 27 October 2026. The project connected using the official webOS CLI after separate owner approval. CLI values are recorded separately from the owner's physical-device observations. This does not mean the project independently tested every TV function.

| Field | Initial value | Status |
|---|---|---|
| Model | LG 55UP81006LR, UP81 series | Owner-confirmed by manual inspection, 27 October 2026 |
| Model year / platform | 2021 / webOS 6 | Owner-reported; LG identifies the product as a webOS smart TV |
| webOS TV version | 6.5.3-47 | Owner-confirmed by manual inspection, 27 October 2026 |
| webOS release codename | kisscurl-koli | Owner-confirmed, 27 October 2026 |
| Firmware | 03.53.45 | Owner-confirmed by manual inspection, 27 October 2026 |
| Developer Mode | Enabled using the official Developer Mode app; TV rebooted successfully | Owner-confirmed after separate approval, 27 October 2026 |
| Developer Mode Key Server | Off after SSH pairing | Owner-confirmed, 27 October 2026 |
| Network | Wi-Fi; local-network connectivity confirmed | Owner-confirmed, 27 October 2026 |
| Available update | 03.53.46 | Owner-confirmed as displayed, 27 October 2026; automatic updates disabled |
| Storage | 2.04 GB total; approximately 0.99 GB available | Owner-reported; manual confirmation pending |
| Automatic firmware updates | Disabled | Owner-reported; manual confirmation pending |
| External device | Raspberry Pi 5 running Steam Link, HDMI; Bluetooth controller paired to Pi | Owner-reported; connectivity validation pending |

## Developer Mode discovery observations

The owner reports that SSH pairing completed and that `ares-device --system-info --device lounge-tv` succeeded. The CLI returned `modelName: 55UP81006LR`, `sdkVersion: 6.5.3`, `firmwareVersion: 03.53.45`, and `boardType: K7LP_DVB_EU`. These are CLI observations; they supplement but do not replace the owner's manual confirmation of the physical set and firmware.

The owner reports that `ares-install --device lounge-tv --list` and `--listfull` returned no application records; `--listfull` exited with status 0. Record this as **successful CLI execution; zero application records returned; full installed-app catalogue coverage unknown**. The precise cause is not established. It does not show that no apps are installed or that built-in or LG Store apps are absent. No application was sideloaded, replaced, or removed through this project, and no complete system backup was captured.

LG's public consumer-TV Application Manager reference documents launching an app by known ID and checking a known ID's installation status, not enumerating all installed apps. LG staff stated that a general public installed-app listing API was unavailable and app IDs were generally not public. The similarly named webOS OSE `listApps` API is not evidence of consumer-TV support; OSE warns that its APIs are not guaranteed compatible with LG TVs. Community SSAP libraries may report launch points, but they are not a supported or complete system-package inventory. See [recovery policy](recovery-policy.md) and [LG's Application Manager reference](https://webostv.developer.lge.com/develop/references/application-manager), [LG's forum response](https://forum.webostv.developer.lge.com/t/how-to-get-applist/8616), and [webOS OSE compatibility note](https://www.webosose.org/docs/reference/).

## Owner-confirmed connections and operation after activation

| Connection | Owner-confirmed configuration | Validation status |
|---|---|---|
| HDMI 1 | Nintendo Switch or Xbox, manually swapped | Overall normal operation reported after activation; individual picture, audio, switching, Game Mode, ALLM, HDR, and CEC checks not independently recorded |
| HDMI 2 | PlayStation 5 | Overall normal operation reported after activation; individual feature checks not independently recorded |
| HDMI 3 | Raspberry Pi 5 running Steam Link; TV input labelled PC | Overall normal operation reported after activation; Steam Link, Bluetooth, and individual feature checks not independently recorded |
| Network and Emby | Wi-Fi; local network confirmed; Emby server access and playback confirmed | Owner-confirmed; timing relative to activation is not separately documented |
| Protected streaming apps | Reported working | Owner-confirmed overall report; per-app launch/playback test results are not individually recorded |

The owner reports that everything continued working normally after Developer Mode activation. This is an overall owner observation, not a pass for every item in the detailed baseline. In particular, HDR, ALLM, HDMI-CEC/Simplink, ARC/eARC, Bluetooth, and per-port feature checks remain unverified unless separately recorded.

## Native optimisation results

These settings were manually inspected and configured by the owner on 27 October 2026. The table records reported final states; this project has not independently read them from the TV.

| Setting | Manually confirmed final state |
|---|---|
| Power On Screen | Recent Input |
| Home Promotion | Off |
| Content Recommendation | Off |
| Viewing Information Agreement | Disabled |
| Voice Information Agreement | Disabled |
| Interest-Based Advertisement Agreement | Declined |
| Data Partners Agreement | Declined |
| Marketing Communications Agreement | Declined |
| CMP advertising consent | Reject All selected and confirmed |

### Observed Home changes

- Disabling Content Recommendation removed the LG Channels promotional programme row; TV function shortcuts appeared in its place.
- The large webOS introductory banner remains visible.
- Protected streaming applications remain visible on Home.
- CMP legitimate-interest processing may remain for some vendors; this is an observation/limitation, not a claim that all tracking stopped.

### Validation status

Application launch and playback have not been formally regression-tested after these settings. HDMI, HDMI-CEC, HDR, Game Mode, audio, network, Bluetooth, and Raspberry Pi Steam Link functions also remain pending explicit validation. The protected-app list is a preservation requirement, not evidence that each app was tested.

LG's product page lists HDR, Simplink (HDMI-CEC), three HDMI inputs, eARC on HDMI 2, Wi-Fi, LAN, and Bluetooth 5.0 for this model. Verify regional hardware options on the TV and its manual. [LG 55UP81006LR specifications](https://www.lg.com/uk/tvs-soundbars/smart-tvs/55up81006lr/)

Firmware 03.53.46 release history says “Fixing minor bugs in software.” The LG applicability list includes 55UP81006LR. The published note does not identify specific security fixes or regressions. [LG UP81 support and firmware notes](https://www.lg.com/lv/atbalsts/produkcija/lg-70UP81003LR.AEU)

## Manual baseline checklist

For the complete pre-Developer-Mode checklist, per-test result format, networking/Emby checks, and readiness gate, use [pre-activation-baseline.md](pre-activation-baseline.md). The checklist below is the earlier native-configuration record and does not replace that per-port baseline.

Record the date and observed value. Do not include account identifiers, credentials, authentication tokens, serial numbers, or network secrets.

### Device and settings

- [ ] Firmware version: **owner-reported 03.53.45**; inspect TV to confirm: __________
- [ ] webOS version: **owner-reported 6.5.3-47**; inspect TV to confirm: __________
- [ ] Available update displayed: **owner-reported 03.53.46**; confirm the on-device offer: __________
- [ ] Automatic firmware updates: **owner-reported disabled**; confirm: __________
- [ ] Available storage: **owner-reported 2.04 GB total / ~0.99 GB free**; confirm: __________
- [ ] Home Promotion: inspect and record: __________
- [ ] Content Recommendation: inspect and record: __________
- [ ] Power On Screen: inspect and record: __________
- [ ] LG Channels visibility and location: inspect and record: __________
- [ ] Optional privacy agreements and tracking controls: inspect names and current states: __________
- [ ] Existing application order: record visible order without account or usage details: __________

### Protected functions

- [ ] BBC iPlayer launches and plays content
- [ ] Netflix launches and plays content
- [ ] Channel 4 launches and plays content
- [ ] Disney+ launches and plays content
- [ ] Emby launches; local server discovery and authentication work; media plays
- [ ] Prime Video launches and plays content
- [ ] Apple TV launches and plays content
- [ ] HDMI inputs switch correctly; Raspberry Pi Steam Link connects
- [ ] HDMI-CEC, HDR, Game Mode / low-latency mode, audio output, and ARC/eARC behave as expected
- [ ] Wi-Fi or Ethernet and Bluetooth functions needed by the setup work

The owner-provided list of protected apps is policy, not a claim that each app has been tested on this TV. Record failures as baseline findings before changing settings.
