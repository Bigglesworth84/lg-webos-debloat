# Pre-activation baseline

Use this manual checklist before any Developer Mode installation, activation, or SSH pairing. It is an observation record, not a device backup. Complete it with the owner and the TV/connected equipment; no computer connection to the TV is needed. Do not change settings while capturing the baseline. Record only necessary descriptions; omit passwords, tokens, serial numbers, account details, public IP addresses, MAC addresses, and network credentials.

Developer Mode activation and SSH pairing have since been completed after separate owner approvals. The owner reports normal overall operation afterward, Wi-Fi and local-network connectivity, Emby access/playback, and protected streaming apps working. These reports do not convert the individual results below to Pass. Keep per-port, HDR, ALLM, HDMI-CEC/Simplink, ARC/eARC, Bluetooth, Steam Link, and per-app checks Not tested unless a dated result is entered. Device identity and activation facts are summarized in [hardware.md](hardware.md).

## Result format

Use one result for every item:

- **Not tested** — no observation has been made yet (the initial result for every new test below).
- **Pass** — the observed behavior matches the owner's expected working behavior.
- **Fail** — the behavior does not match the owner's expected working behavior.
- **Not applicable** — the feature is unsupported or unused for this device/path; explain why in Notes.

For each item, record **Test date**, **Observed result**, **Notes**, and **Known pre-existing issues**. Replace `Not tested` only after the owner observes the item. A failure present before activation is a known pre-existing issue, not a new regression. Do not begin a state-changing operation while any failure remains unexplained.

| Test date | Observed result | Notes | Known pre-existing issues |
|---|---|---|---|
| __________ | Not tested | __________ | __________ |

Copy the result row for each test below, or write its four values beside the test. Use N/A only for unsupported or unused features, never for an untested item.

## Device identity and Developer Mode

| Field | Expected/reference value | Test date | Result | Observed value / notes | Known pre-existing issues |
|---|---|---|---|---|---|
| Physical model | LG 55UP81006LR (reconfirm on TV) | ______ | Not tested | ______ | ______ |
| Firmware | 03.53.45 (subject to reconfirmation) | ______ | Not tested | ______ | ______ |
| webOS version | 6.5.3-47 (subject to reconfirmation) | ______ | Not tested | ______ | ______ |
| Developer Mode before activation | Record current app/status if present; do not enable it | ______ | Not tested | ______ | ______ |
| Baseline inspection date | Enter the actual date the owner observes the baseline | ______ | Not tested | ______ | ______ |

If model, firmware, or webOS differs from the reference, record the observed value and pause readiness review until model-specific documentation is checked. Do not use CLI metadata as proof of physical model identity.

## HDMI and gaming

Record each HDMI port separately. Do not infer or fill in the connected device; have the owner identify it. For unused inputs or unsupported features, select **Not applicable** and state why.

| Port / check | Connected device description (owner supplied) | Test date | Result | Observed output / notes | Known pre-existing issues |
|---|---|---|---|---|---|
| HDMI 1 — connected device | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — picture output | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — audio output | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — input switching | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — Game Mode | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — ALLM, if supported | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — HDR, if supported | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — HDMI-CEC / Simplink, if used | ______ | ______ | Not tested | ______ | ______ |
| HDMI 1 — limitations | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — connected device | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — picture output | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — audio output | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — input switching | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — Game Mode | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — ALLM, if supported | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — HDR, if supported | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — HDMI-CEC / Simplink, if used | ______ | ______ | Not tested | ______ | ______ |
| HDMI 2 — limitations | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — connected device | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — picture output | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — audio output | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — input switching | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — Game Mode | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — ALLM, if supported | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — HDR, if supported | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — HDMI-CEC / Simplink, if used | ______ | ______ | Not tested | ______ | ______ |
| HDMI 3 — limitations | ______ | ______ | Not tested | ______ | ______ |

Also record any shared behavior, such as the existing sound system and ARC/eARC use:

| Shared check | Test date | Result | Observed result / notes | Known pre-existing issues |
|---|---|---|---|---|
| HDMI input switching across all used ports | ______ | Not tested | ______ | ______ |
| Existing audio configuration, including ARC/eARC where used | ______ | Not tested | ______ | ______ |
| HDMI-CEC / Simplink behavior across connected devices, where used | ______ | Not tested | ______ | ______ |
| Raspberry Pi Steam Link connection and gameplay, if used | ______ | Not tested | ______ | ______ |
| Required Bluetooth devices and behavior, if used | ______ | Not tested | ______ | ______ |

## Networking and Emby

Record only connection type and functional outcomes. Do not record addresses, credentials, or network identifiers.

| Check | Test date | Result | Observed result / notes | Known pre-existing issues |
|---|---|---|---|---|
| Current connection type (Wi-Fi or Ethernet) | ______ | Not tested | ______ | ______ |
| Internet connectivity | ______ | Not tested | ______ | ______ |
| Local network connectivity | ______ | Not tested | ______ | ______ |
| Local network device discovery, where used | ______ | Not tested | ______ | ______ |
| Emby server discovery | ______ | Not tested | ______ | ______ |
| Emby media playback | ______ | Not tested | ______ | ______ |
| Streaming application network connectivity | ______ | Not tested | ______ | ______ |

## Protected streaming applications

For each application, verify both launch and playback of suitable content. Do not record account details or content history.

| Application | Launch date / result | Playback date / result | Notes | Known pre-existing issues |
|---|---|---|---|---|
| BBC iPlayer | ______ / Not tested | ______ / Not tested | ______ | ______ |
| Netflix | ______ / Not tested | ______ / Not tested | ______ | ______ |
| Channel 4 | ______ / Not tested | ______ / Not tested | ______ | ______ |
| Disney+ | ______ / Not tested | ______ / Not tested | ______ | ______ |
| Emby | ______ / Not tested | ______ / Not tested | ______ | ______ |
| Prime Video | ______ / Not tested | ______ / Not tested | ______ | ______ |
| Apple TV | ______ / Not tested | ______ / Not tested | ______ | ______ |

## Previously confirmed webOS privacy and advertising settings

These are reference values recorded in [hardware.md](hardware.md) from owner inspection on 27 October 2026. They are not a fresh observation for this baseline. Recheck and record their current state without changing them. If the TV differs, note the difference and leave the setting as found.

| Setting | Previously confirmed reference | Recheck date | Result | Current observed value / notes |
|---|---|---|---|---|
| Power On Screen | Recent Input | ______ | Not tested | ______ |
| Home Promotion | Off | ______ | Not tested | ______ |
| Content Recommendation | Off | ______ | Not tested | ______ |
| Viewing Information Agreement | Disabled | ______ | Not tested | ______ |
| Voice Information Agreement | Disabled | ______ | Not tested | ______ |
| Interest-Based Advertisement Agreement | Declined | ______ | Not tested | ______ |
| Data Partners Agreement | Declined | ______ | Not tested | ______ |
| Marketing Communications Agreement | Declined | ______ | Not tested | ______ |
| CMP advertising consent | Reject All selected and confirmed | ______ | Not tested | ______ |

Previously observed limitations to keep in mind when recording current results: the webOS introductory banner remained visible, and CMP legitimate-interest processing may remain for some vendors. These observations do not prove current behavior or that all tracking stopped.

## Historical readiness gate for Developer Mode activation

This historical checklist did not itself authorize activation. Developer Mode installation, activation, and SSH pairing were subsequently completed after separate owner approvals. It does not authorize any new TV operation.

- [ ] Baseline completed; every failure is understood and recorded, with no unexplained failures.
- [ ] Exact physical model, firmware, and webOS version reconfirmed on the TV.
- [ ] Developer Mode status before activation recorded.
- [ ] Official webOS CLI environment is available and its documented version verified on the computer.
- [ ] Recovery limitations acknowledged: no full-system backup or verified restoration of TV state is established.
- [ ] SSH credential storage location and permissions reviewed; no secret copied into the repository, logs, or report.
- [ ] Proposed read-only inventory command list and its coverage limits verified against the official CLI documentation.
- [ ] Separate approval recorded for Developer Mode app installation, if needed.
- [ ] Separate approval recorded for Developer Mode activation.
- [ ] Separate approval recorded for SSH pairing / key retrieval.

After activation, repeat the same HDMI, gaming, networking, Emby, streaming, and settings checks above. Add the post-activation date and result alongside each baseline result. The owner reports normal overall operation after activation, but individual checks remain Not tested until recorded. Any newly failing established feature is a regression: halt further device changes until it is investigated. Follow [developer-mode-runbook.md](developer-mode-runbook.md) and [rollback.md](rollback.md) for recovery boundaries and deactivation.
