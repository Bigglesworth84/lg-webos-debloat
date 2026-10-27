# Research notes

Research checked 27 October 2026. Confirm menu names and update applicability on the exact regional set before acting.

## Native home settings

LG documents Home Promotion, Content Recommendation, and Power On Screen controls for updated 2021 webOS 6 / 2022 webOS 22 TVs. The documented paths and effects are in [LG's guide](https://www.lg.com/uk/support/product-support/troubleshoot/help-library/cs-CT00008333-20153529296869/). Recommendation suppression is not documented as a way to remove every content row; specifically, it does not guarantee that the LG Channels row disappears.

## Privacy

LG describes ACR / Viewing Information, voice recognition, and interest-based advertising as optional features controlled by agreement and TV settings. Review the exact agreements shown on the device and record labels and states before opting out. [LG privacy statement](https://www.lg.com/us/newsroom/corporate/statement-understanding-privacy-on-lg-smart-tvs)

DNS filtering remains deferred. DNS blocking is domain-level and can affect unrelated functions sharing a domain. It is not a reliable way to distinguish YouTube ads from video delivery. No DNS changes or domain blocklists are part of this slice.

## Firmware 03.53.46

LG's release notes list 03.53.46 for the 55UP81006LR model ID and state only “Fixing minor bugs in software.” The notes are dated 20 October 2026. They do not name security fixes, individual bug fixes, or known regressions. As of this research, there is no evidence here to recommend indefinite update avoidance or to claim a particular security benefit. The owner should compare the TV's exact regional support page and on-device prompt before deciding. [LG current 03.53.46 applicability list and release history](https://www.lg.com/lv/atbalsts/produkcija/lg-70UP81003LR.AEU)

## Developer Mode and inventory

LG's Developer Mode workflow requires the TV and PC on the same network, an LG Developer account, the Developer Mode app, and key pairing. LG documents a limited session; when the session expires and Developer Mode disables, apps installed through Developer Mode are uninstalled. LG documents session extension while the session remains active. Plan renewal before any future sideloading. [Official setup and expiry guidance](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)

The official CLI documents read-only installed-app listing with `ares-install --device DEVICE --list` and a detailed listing with `--listfull`. Example, after a separately approved setup and TV connection:

```sh
ares-install --device myTV --list
ares-install --device myTV --listfull
```

`myTV` is a placeholder device alias configured by `ares-setup-device`. These commands are documented inventory operations; do not add an install or removal command to an inventory workflow. LG documents `--remove APP_ID` separately, but that does not demonstrate that system components are removable or safe to remove. No removal operation is approved. [LG CLI reference](https://webostv.developer.lge.com/develop/tools/webos-tv-cli-dev-guide)

webOS Dev Manager is a maintained community desktop manager with Linux AppImage downloads for distributions other than Debian/Ubuntu. On Bazzite, prefer an AppImage or isolated environment after checking current release requirements. The CLI remains the reproducible choice for read-only inventory. [Dev Manager releases](https://github.com/webosbrew/dev-manager-desktop/releases), [project README](https://github.com/webosbrew/dev-manager-desktop)

## YouTube AdFree and rooting status

YouTube AdFree advertises YouTube ad blocking and SponsorBlock, and its README requires uninstalling the official YouTube app before installation. Root is not required for a Developer Mode installation. Exact playback and login behavior on this TV remain unverified; see [compatibility](compatibility.md). [Project README](https://github.com/webosbrew/youtube-webos)

Rooting is deferred. webOS Homebrew documents RootMyTV as patched on modern webOS 6 firmware and describes DejaVuln as subject to firmware patching. A community exploit tracker is interactive and has not yielded a verified exact-model result for this project. Do not infer compatibility from the broad webOS version range. [Rooting overview](https://www.webosbrew.org/rooting/), [exploit patch summary](https://www.webosbrew.org/rooting/exploits/), [compatibility tracker](https://cani.rootmy.tv/)
