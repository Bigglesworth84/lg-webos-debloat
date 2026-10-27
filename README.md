# LG webOS Debloat

A cautious, documented workflow for reducing promotion and clutter on an LG 55UP81006LR while preserving streaming, Emby, HDMI, and gaming functions.

## Current phase

The owner has manually completed native configuration on the LG 55UP81006LR. This repository records those reported results and defines backup-first recovery controls. No project-initiated TV connection or modification, sideloading, DNS change, rooting, or application removal is part of this slice. App launch/playback and protected-function regression checks are still pending.

## Workflow

1. Read [the baseline and native settings results](docs/hardware.md).
2. Read the [recovery policy](docs/recovery-policy.md) before planning state changes or tooling.
3. Require a captured baseline, documented supported recovery, and explicit approval before any future operation.
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
- [Recovery policy and tooling design](docs/recovery-policy.md)
- [Change log](docs/change-log.md)
