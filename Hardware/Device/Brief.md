
# Device — EFW Third Node Type

**Role:** in-room user-facing node. Long-term **replacement** for the test-only 0x0033 (Outside) and 0x0044 (Car) NC1000-only T/H sniffers — those were proof-of-concept, not production. Production EFW mesh: **Gateway** (RP5 + NeoGW) + **Actuator** (flap motors) + **Device** (this).

Still part of the same EFW project. Same GitHub repos (`Energy_Flow_Wall` for hardware, `Energy_Flow_Wall_Code` for firmware/scripts).

## Display
- ✅ **GoodDisplay GDEY042T81-T02** — 4.2" monochrome e-paper, **400 × 300 px**, SPI, SSD1683 controller, **with bonded PET capacitive touch overlay** driven by **FT6336U (FocalTech)** controller — I²C address 0x38, with IRQ + RST lines. The touch overlay replaces the originally planned MCU-native CapSense — UI elements are rendered on the e-paper and respond to direct touch, freeing the front face of physical control area and giving firmware the flexibility to evolve the UI over OTA without hardware changes. **GoodDisplay supplies STM32 reference code for both panel and touch driver** (good-display.com/product/473.html → Downloads → "GDEY042T81-FT02/GDEY042T81-T02 STM32 Sample Code") — significant bring-up shortcut.
- Chosen for lowest power of the modern partial-refresh-capable family: full refresh ~2 s / partial refresh ~0.3 s, deep-sleep current <5 µA, refresh energy small enough that even a 1-minute time-chip update path is essentially free in the battery budget. 4.2" is "decent size" — 137 PPI, comfortable at arm's length.
- Square 480×480 was the original aim (a colour TFT mock was prototyped at that resolution, NSPanel Pro-class) but **true 4" 480×480 SPI e-paper isn't a stock part in 2026** — the square e-paper market only exists at sub-2" sizes and at ≥5.83" (and the closest 5.83" candidate is going EOL). 400×300 lands the same physical size without custom-panel MOQ pain.
- **UI consequence**: the colour TFT prototype mock needs to be re-rendered at 400×300 (landscape 4:3) before it represents what the Device will actually show in monochrome e-paper. The two-card top + chart-below layout still fits; fonts and chart height shrink. Easy port. (An e-paper preview mock has also been prototyped at the same physical size.)
- Refresh strategy: partial refresh for time-chip + setpoint changes (sub-second, no full-screen flicker); full refresh once an hour or on full-screen state changes to clear ghosting.

## Power
- **LiFePO₄ battery.** Chemistry chosen for long cycle life + safe nominal voltage near the load rail.
- **Wireless charging via MagSafe** — receiver coil + magnets embedded in the Device. End-user lifts the Device off the wall every 6–12 months, drops on any MagSafe pad, returns it.
- **Room-side fixture:** **3D-printed plastic holder** with a **second AliExpress 18-magnet adhesive ring** stuck face-out — symmetric two-ring magnet pairing roughly doubles the pull-force vs. a magnet-to-steel configuration, and the N-S alternating polarity pattern on both rings auto-aligns rotationally when faces oppose. A **shallow perimeter lip** on the fixture provides redundant translational location so the Device snaps into a defined position. No steel parts in the wall fixture — RF-clear everywhere except the small magnet footprints.
- **Display orientation**: landscape (native 4:3 e-paper, no firmware rotation cost).
- ✅ **Battery cell**: **LFP143060** — stock LFP pouch, 1800 mAh, 3.2 V nominal, **14 × 30 × 60 mm**, integrated protection PCB, 2000+ cycles. Source: [lithium-lifepo4-battery.com](https://www.lithium-lifepo4-battery.com/lifepo4-battery-lfp143060-1800mah-3-2v/), sample MOQ 5–10 pcs / 3–5 day lead. The capacity is encoded in the PN (LFP / 14 mm thick / 30 mm wide / 60 mm long). Backup suppliers if that vendor is unreachable: **Grepow** (grepow.com/lifepo4-battery.html — well-established Shenzhen maker, full LFP pouch range), **Misen Power** (misenpower.com — explicit LFP pouch line).
- **Mechanical envelope** (working assumption): Device front face ~100 × 80 mm, total depth ~19–22 mm (e-paper 1.2 + PCB 1.6 + LFP pouch 14 + Qi coil/magnet ring stacked beside the pouch + enclosure back 1.5). Comparable to a chunky light-switch plate. Adjust when first 3D draft exists.
- **Sleep budget is very tight.** Whatever the NC1000 1/sec ALT-mode wake mystery turns out to be on Actuator (open FRD item), it likely matters more here. Solving it is a prerequisite for shipping the Device.
- **Optional small solar panel — separate "PV module" SKU.** PV cell + **TI BQ25570** harvester (MPPT + boost + LiFePO₄ charge management, integrated single-chip solution) + support passives all live on the PV module, not the Device PCB. Two-wire output (regulated ~3.45 V at BQ25570 termination) plugs into the Device via a small connector; on the Device side it's just one connector, a Schottky reverse-protection diode, and a filter cap — feeds the same LiFePO₄ charge node as the BQ51013B MagSafe path. Either source (MagSafe or PV) can charge concurrently; higher-voltage source wins, no fight. Extends charge interval; in bright-room installs may eliminate manual MagSafe charging entirely. Same PV module potentially reusable for a future [Sniffer Concept](Sniffer_Concept.md) product.

## Sensors / I/O — modular, populate per install
Single board family, single firmware family — each unit assembled only with the modules the room actually needs:
- **Temperature + Humidity** — always populated. **Sensirion SHT45** wired **directly to NC1000 I²C** — same topology as Actuator. NC1000 reads SHT45 and reports to Gateway autonomously in Normal mode without ever waking the MCU. Display T/H is pulled from the Gateway store via the STM32 ↔ NC1000 UART when the screen refreshes (not on every NC1000 read).
- **CO₂** — optional. **Sensirion SCD41** (photoacoustic NDIR, I²C, single-shot ~50 µJ mode compatible with hibernate). Premium air-quality variant with SEN6x + Bosch BMV080 spun off as a separate mains-powered product — see `sniffer_brief.md`.
- **Presence / occupancy** — optional. **Infineon BGT60LTR11AIP** — 60 GHz low-power radar (single-target presence/motion). µW-range sleep, much better than mmWave dev boards and far richer than a PIR. SPI control + interrupt output.
- **Potential-free I/O** — optional. **2 inputs + 2 outputs.** Inputs: optocoupler-isolated (LTV-356T / PC817 family), accept 3–24 V dry-contact or low-voltage logic from external systems. Outputs: low-side N-MOSFET (e.g. DMG2305UX or similar), open-drain to GND, customer's load wired between external rail and the output pin; rated for ≤24 V external rail, ≤500 mA. Targets thermostat-style dry-contact inputs on underfloor-heating zone controllers, whole-house extraction-fan starters, and HVAC AHU thermostat inputs — not direct mains switching (a separate external relay block handles that 5% of cases). Connector: 4-pole 3.5 mm-pitch screw terminal block at PCB bottom edge.
- **Touch input** — **integral to the e-paper display** (no separate PCB area). **FT6336U (FocalTech)** capacitive touch controller bonded on top of GDEY042T81-T02, communicating with MCU over I²C (shared bus with SCD41 — addresses don't conflict: **0x38** vs 0x62) + IRQ + RST pins. Wakes the MCU on touch from deep sleep; on-screen tap targets are drawn in firmware and can evolve over OTA. GoodDisplay supplies an STM32 reference driver — start there rather than writing the FT6336U I²C driver from scratch.

The "populate only what's needed" approach keeps SKU count low without ecosystem fragmentation: same PCB, same firmware, modules absent → corresponding features simply unavailable in that unit.

## Mesh integration
- Same NC1000 radio as Actuator and as the legacy test devices.
- Same AAPI protocol on the same gateway.
- **New node IDs** to be assigned. Do NOT reuse 0x33 / 0x44 — they were ad-hoc test IDs, retired.
- Operates in **Normal mode** for T/H reporting (like 0x55 Actuator does) and in **ALT mode** to receive commands (display update, output toggle, etc.) and to send local user input (touch button events, presence changes).

## Decisions made (2026-06-14, MCU revised 2026-06-15)
- ✅ **MCU**: **STMicroelectronics STM32U585CIU6** (QFN-48, Cortex-M33 + TrustZone @ 160 MHz, **2 MB flash, 786 KB RAM**, OctoSPI for future external flash if ever needed). Chosen after walking away from PSoC6:
  - PSoC Creator tooling is in maintenance mode at Infineon and ModusToolbox is the forced successor — uncertain long-term investment in the PSoC line post-acquisition.
  - The PSoC6 features that originally justified it (native CapSense block) became irrelevant once we moved to **GT911 touch overlay on the e-paper**; the touch is in the panel, not in the MCU.
  - STM32U5 is ST's current strategic ultra-low-power line — multi-decade roadmap, native macOS tooling (STM32CubeIDE + VSCode + STM32-PlatformIO), much larger community, no vendor account required.
  - **2 MB flash is the right size**, not overkill: realistic firmware budget once LVGL + 3 fonts + room icons + multi-room data + daily/weekly schedule + safe OTA double-bank is included is ~900 KB minimum, comfortable target ~1.4 MB. 256 KB-class chips would force feature compromises within ~12 months.
  - Hand-solderable QFN-48 package — no BGA respin step.
- ✅ **T/H sensor**: SHT45 (same as Actuator).
- ✅ **CO₂ sensor**: Sensirion **SCD41**. (Full air-quality coverage is the future Sniffer product, not the Device.)
- ✅ **Presence sensor**: Infineon **BGT60LTR11AIP** 60 GHz LP radar.
- ✅ **Touch input**: **FT6336U (FocalTech) capacitive touch controller** bonded on the e-paper (GDEY042T81-T02 variant). I²C address 0x38 (no conflict with SCD41 at 0x62). Replaces the originally planned MCU-native CapSense. Frees the front face of physical control area and lets UI evolve in firmware over OTA. **GoodDisplay supplies STM32 reference code** for both panel + touch — meaningful bring-up shortcut.
- ✅ **SHT45 bus topology**: SHT45 → NC1000 I²C (autonomous). STM32 has no electrical path to SHT45; pulls T/H from Gateway via UART only when display refreshes.
- ✅ **Battery target**: **LiFePO₄ 3.2 V / 1800 mAh**. SHT45-only mesh beacon should run for years on this; full-load (CO₂ + radar + touch + e-paper) should comfortably exceed the 6–12 month MagSafe charge interval. See **Power budget** section below.
- ✅ **CO₂ measurement cadence — presence-gated state machine**:
  - **5 min** baseline when room is **occupied** (presence detected by BGT60LTR11AIP radar within the last *N* minutes — tune *N* during bring-up, start with 10 min).
  - **30 min** (or longer) when room is **unoccupied AND CO₂ already at baseline** (e.g. below 500–600 ppm or within ±100 ppm of the last unoccupied minimum). No new CO₂ source is in the room — nothing meaningful is changing.
  - **5 min** stays active when room is **unoccupied AND CO₂ still elevated** — we want to watch the decay curve as ventilation clears the room.
  - **Snap back to 5 min the instant** the radar reports new presence — don't wait for the next scheduled tick.
  - **10 s** during development / bench validation only.
  - **Why this matters for battery**: SCD41 single-shot is the dominant active-power draw in a fully-populated Device (~250 µA averaged at 5 min cadence). Stretching to 30 min in unoccupied + baseline state cuts that contribution by ~6×, materially extending the MagSafe-charge interval for installations like storage rooms, roof cavities, garages, and any other "Actuator integrated but no human" rooms Aidas described.
  - **Falls back gracefully**: in a Device populated *without* the radar module, the firmware simply uses the 5-min cadence unconditionally — no special-case code, just a "presence reported?" check that defaults to "yes, unknown".
- ✅ **Wireless charging**: **MagSafe-compatible** (not MFi-licensed). Use **pre-assembled adhesive 18-magnet ring** from AliExpress (search "Strong Magnetic Ring Wireless Charging Magnet Circle Sticker MagSafe iPhone") — ~NZ$1.10 per ring in qty 10. **No PCB-level magnets** — PCB designer just leaves the back-of-board area behind the ring clear. **Two rings per Device + wall-fixture set**: one stuck to back of Device enclosure, one stuck to wall fixture facing outward. Symmetric ring-to-ring pairing roughly doubles the hold force vs. magnet-to-steel and auto-aligns rotationally. Pull-strength + long-term adhesive (typically 3M VHB) need a one-off bench test before committing.
- ✅ **Qi receiver IC**: **TI BQ51013B** — 5 W Qi Rx, integrated rectifier + LDO, ~5 V output → feeds LiFePO₄ charger directly. Well-trodden part, ~$3 single qty. Pair with a stock flat receiver coil (Würth 760308103xx-series or equivalent), sized to fit inside the magnet ring (~30 mm coil OD inside ~45 mm magnet ring).
- ✅ **NC1000 antenna ↔ magnet clearance**: **≥10 mm minimum** between the antenna trace/element and the nearest magnet. Antenna on a small carrier stub off the top edge of the PCB; magnets + Qi coil + LiFePO₄ on the back face; ground plane between layers. E-paper is RF-transparent, so radiating "through" the display is OK.

## Still to decide before drafting [Schematic placeholder](Schematic_placeholder.md)
1. **PV module design** (separate SKU, downstream of Device) — exact panel choice (amorphous-Si vs mono-Si, size, aesthetic), BQ25570 programming values, connector pinout standardisation, enclosure. Can be designed after the Device PCB is taped out.

## Bench tests to do before committing to production hardware
- **Magnet ring pull test**: confirm AliExpress 18-magnet adhesive ring holds a Device-weight dummy (~250 g) against gravity reliably; verify long-term adhesive on the chosen enclosure material.
- **LFP143060 sample order**: order 5–10 pieces; verify dimensions, integrated protection PCB behavior, and charge curve from the BQ51013B output.

## Ready to draft [Schematic placeholder](Schematic_placeholder.md) now
All architectural decisions are locked. A first sketch / 3D draft of the Device enclosure should accompany schematic drafting so PCB outline + connector positions stay coherent with the enclosure.

## Linked
- [Schematic placeholder](Schematic_placeholder.md) — authoritative schematic (placeholder)
- `schematic-actuator` (internal note) — sibling node, useful as a reference for what "authoritative schematic file" looks like
- `neocortec-project` (internal note) — mesh-level context shared with Actuator and Gateway
- [Sniffer Concept](Sniffer_Concept.md) — future premium air-quality variant (SEN6x + possibly Bosch BMV080), mains-powered, separate product
