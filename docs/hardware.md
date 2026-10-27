# Hardware and baseline

## Device facts

The values in the native optimisation results below were manually inspected and configured by the owner on 27 October 2026. This project did not connect to the television. Other starting values remain owner-reported until manually confirmed.

| Field | Initial value | Status |
|---|---|---|
| Model | LG 55UP81006LR, UP81 series | Owner-confirmed by manual inspection, 27 October 2026 |
| Model year / platform | 2021 / webOS 6 | Owner-reported; LG identifies the product as a webOS smart TV |
| webOS TV version | 6.5.3-47 | Owner-confirmed by manual inspection, 27 October 2026 |
| Firmware | 03.53.45 | Owner-confirmed by manual inspection, 27 October 2026 |
| Available update | 03.53.46 | Owner-confirmed as displayed, 27 October 2026; automatic updates disabled |
| Storage | 2.04 GB total; approximately 0.99 GB available | Owner-reported; manual confirmation pending |
| Automatic firmware updates | Disabled | Owner-reported; manual confirmation pending |
| External device | Raspberry Pi 5 running Steam Link, HDMI; Bluetooth controller paired to Pi | Owner-reported; connectivity validation pending |

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
