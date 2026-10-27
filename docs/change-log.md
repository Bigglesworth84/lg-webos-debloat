# Change log

Record approved device operations here only after they occur. Include date, device/firmware source, operation, captured baseline reference (without secrets), recovery classification, approval, validation, and any limitations. Put actionable undo steps in [rollback notes](rollback.md).

## 2026-10-27 — Native settings reported by owner

- **Device/firmware:** LG 55UP81006LR; webOS 6.5.3-47; firmware 03.53.45; owner manually inspected and confirmed these values.
- **Operation:** Owner configured startup, Home promotion/recommendations, viewing and voice agreements, advertising/data-partner/marketing choices, and CMP advertising consent. Exact final values and Home observations are recorded in [hardware and baseline](hardware.md).
- **Approval/source:** Reported as completed by the owner; the project did not connect to or change the TV.
- **Recovery classification:** Manually reversible through documented settings is the intended classification. Restoration has not been independently verified by this project; review each on-screen control and agreement before restoring consent.
- **Validation:** Owner observed that the LG Channels promotional programme row disappeared and TV function shortcuts replaced it. The introductory banner remains and protected apps remain visible. App launch/playback and protected-function regression checks are pending.
- **Backup:** No machine-readable baseline or device backup was created. No supported device-state export or restore interface is established.

## 2026-10-27 — Recovery framework documentation

- **Operation:** Repository documentation and policy only; no device-facing action.
- **Validation:** Documentation and policy consistency reviewed; no device backup, restore, or inventory capability is claimed.
