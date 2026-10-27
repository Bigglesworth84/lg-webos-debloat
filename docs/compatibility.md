# Compatibility

Status is specific to the evidence found; broad support for a webOS generation is not proof for this model and firmware.

| Capability | Status | Evidence / limitation |
|---|---|---|
| Home Promotion and Content Recommendation controls | Documented for 2021 webOS 6 TVs; exact menu state uninspected | [LG guide](https://www.lg.com/uk/support/product-support/troubleshoot/help-library/cs-CT00008333-20153529296869/) |
| Recent Input startup | Documented as Power On Screen option on the applicable home settings guide; exact set uninspected | Test manually; may start at the last broadcast or external input rather than Home |
| Removing the LG Channels row by disabling recommendations | Unverified; do not assume it | LG documents recommendations control but does not guarantee every home row disappears |
| Firmware 03.53.46 | Official release note lists 55UP81006LR; says only “Fixing minor bugs in software” | No specific security fix or regression information in the cited release history; verify regional support page and on-device offer |
| webOS CLI app inventory | Officially documented read-only list commands; owner reports successful execution with zero records | Full catalogue coverage unknown and reason for empty output unestablished; does not establish removability |
| webOS Dev Manager on Bazzite | Linux AppImage is published for non-Debian/Ubuntu distributions | Community tool; check current release and runtime before future use |
| YouTube AdFree install | Root not required; official YouTube app must first be uninstalled | [Project README](https://github.com/webosbrew/youtube-webos); a later install is not approved in this slice |
| YouTube AdFree on webOS 6.5.3-47 / 03.53.45 | Unverified on this exact TV | Project targets Chromium 79 for webOS 6, but reports on some webOS 6 sets describe playback stalls; test before relying on it |
| Google sign-in and sustained playback in YouTube AdFree | Unverified | Project documentation and community reports do not establish exact-model behavior |
| Root access on 55UP81006LR / 03.53.45 | Unverified; not pursued | Do not infer exact compatibility from general webOS 6 support; [tracker](https://cani.rootmy.tv/) is interactive |
| HDMI, CEC, HDR, gaming, audio, Emby, and protected apps after Developer Mode activation | Owner reports normal overall operation; detailed per-feature and per-port tests remain unrecorded | See dated owner observations and open checks in [hardware.md](hardware.md) |

## Protected application policy

The following applications are protected: BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV. Unknown applications and system components are protected by default. No package IDs have been inspected or approved for removal. This repository contains no removal script or removal command workflow.
