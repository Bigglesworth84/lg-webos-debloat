# LG webOS Debloat

A cautious, documented workflow for reducing promotion and clutter on an LG 55UP81006LR while preserving streaming, Emby, HDMI, and gaming functions.

## Current phase

Milestone 001, Slice 1 establishes the baseline and documents native settings. No TV connection, configuration changes, sideloading, DNS changes, rooting, or application removal are part of this slice.

## Workflow

1. Read [the baseline and native settings checklist](docs/hardware.md).
2. Record observations manually; the TV baseline is not yet independently inspected.
3. Follow [the native optimisation procedure](docs/implementation-plan.md) one setting at a time and record results in the checklist.
4. Use [the rollback notes](docs/rollback.md) if a change causes an unwanted result.

The future Developer Mode inventory is read-only. Application removal is outside this slice and requires a separately approved plan.

## Protected functions

BBC iPlayer, Netflix, Channel 4, Disney+, Emby, Prime Video, and Apple TV are mandatory protected applications. HDMI inputs, HDMI-CEC, Game Mode, HDR, audio, network connectivity, Bluetooth, and Raspberry Pi Steam Link use are also protected. Unknown applications and system components are protected by default. See [the operating rules](AGENTS.md).

## Project documents

- [Hardware and baseline](docs/hardware.md)
- [Research and sources](docs/research.md)
- [Compatibility](docs/compatibility.md)
- [Milestones and acceptance criteria](docs/implementation-plan.md)
- [Rollback](docs/rollback.md)
