# Hardware and baseline

## Device facts

The following starting values were supplied by the owner and have not been read from the television by this project:

| Field | Initial value | Status |
|---|---|---|
| Model | LG 55UP81006LR, UP81 series | Owner-reported; LG product page confirms model family |
| Model year / platform | 2021 / webOS 6 | Owner-reported; LG identifies the product as a webOS smart TV |
| webOS TV version | 6.5.3-47 | Owner-reported; manual confirmation pending |
| Firmware | 03.53.45 | Owner-reported; manual confirmation pending |
| Available update | 03.53.46 | Owner-reported; LG's current release notes list 03.53.46 for 55UP81006LR |
| Storage | 2.04 GB total; approximately 0.99 GB available | Owner-reported; manual confirmation pending |
| Automatic firmware updates | Disabled | Owner-reported; manual confirmation pending |
| External device | Raspberry Pi 5 running Steam Link, HDMI; Bluetooth controller paired to Pi | Owner-reported; connectivity validation pending |

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
