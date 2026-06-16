
# Device datasheet — gaps & open part choices

Companion to [Datasheet Stash](Datasheet_Stash.md). Two buckets: docs to grab (parts already chosen), and decisions to make (no datasheet possible yet).

**Why:** Aidas wants to pre-load all reference material before HW arrives, mirroring the Actuator prep pattern that paid off heavily. Surfacing genuine misses and TBD parts here so the schematic session doesn't hit "wait, what's the part number?" blockers mid-flow.

**How to apply:** at the start of any Device schematic / firmware bring-up session, scan this list against the live stash and the [Brief](Brief.md) decision log. Tick off as resolved. When Aidas picks one of the TBD parts, move it into [Datasheet Stash](Datasheet_Stash.md) and remove from here.

## Docs to grab (parts already chosen — just missing from initial download list)

### 01_MCU
- **STM32U5 hardware-design application note** — ST's "getting started with hardware development" AN for U5: power tree, decoupling, BOOT0, oscillator selection. Mandatory before schematic.
- **AN2867** — STM32 crystal selection (HSE + LSE design rules, load-cap math). Cross-family canonical ref.
- **Arm ARMv8-M Architecture Reference Manual** — TrustZone / SAU / MPU architecture-level semantics. ST's PM0264 only covers the Cortex-M33 instruction set, not architecture. Source: developer.arm.com.

### 02_Display_Touch
- **GT911 Programming Guide** — separate from the GT911 datasheet. Touch event protocol, I²C register map, config flashing. Both PDFs needed.

### 03_Sensors
- **BGT60LTR11AIP Programming Guide / Radar Fusion GUI / Configurator docs** — chip datasheet alone is not enough to bring the radar up. Infineon's app docs hold the register init sequences and parameter trade-offs.
- **Sensirion SHT45 Interface Description PDF** — separate from main datasheet. Contains I²C state machine and command timing details.
- **Sensirion SCD41 Interface Description PDF** — same pattern: separate from datasheet, contains the single-shot / periodic-measurement state machine.

## Verify before downloading (controller silicon ambiguity)

- **GDEY042T81-T02 e-paper controller — SSD1683 OR UC8276c.** GoodDisplay's 400×300 family ships both depending on revision; the actual silicon on the T02 variant is not pinned down in [Brief](Brief.md). **Action:** read the GDEY042T81-T02 datasheet first to confirm which controller is bonded, then download THAT controller's datasheet. Do not stash both speculatively.

## TBD by part choice — no datasheet until Aidas picks

These are decisions, not download tasks. Each blocks one section of the schematic.

| Part class | Status | Candidates / notes |
|------------|--------|--------------------|
| LiFePO₄ charger IC (between BQ51013B 5V out and 3.2V LFP cell) | NOT NAMED in brief — brief says BQ51013B "feeds LiFePO₄ charger directly" but doesn't pick one | TI BQ25180 (60–450 mA, tiny), TI BQ25618E, Microchip MCP73123 |
| 3.3 V regulator (from ~3.0–3.6 V LFP rail to MCU/sensors/NC1000) | TBD — class only ("low-Iq LDO") | TI TPS7A02 (25 nA Iq), MAX38640, ADP160 |
| NC1000 antenna part | TBD — chip vs trace not decided | Chip: Johanson 2450AT43A100E. Trace: PCB inverted-F (free but tuning-sensitive) |
| HSE crystal | TBD — frequency + load-cap rating | depends on USB / clocking needs |
| LSE crystal (32.768 kHz for RTC) | TBD — load-cap rating | Abracon ABS07 family typical |
| Low-side NMOS for potential-free outputs | DMG2305UX mentioned in brief as "or similar" — confirm | DMG2305UX or AO3400A |
| Optocoupler for potential-free inputs | LTV-356T / PC817 mentioned as family — confirm specific PN | LTV-356T-A (single-channel) or LTV-846 (quad) |
| Würth Qi receiver coil exact PN | TBD within 760308103xx family | sized to fit inside ~45 mm magnet ring, ≤30 mm OD |
| TVS / ESD protection on screw terminal inputs | NOT in brief — needed for 3–24 V external rail exposure | PESD3V3 family / SMAJ24CA for clamp |
| Sensor-rail load switch (if rails gated for sleep) | NOT in brief — power-budget decision | TPS22910A, SiP32507; only if power profile demands it |

## Closed (already in download plan)
STM32U585 DS, RM0456, ES (errata), Cortex-M33 PM (PM0264), TrustZone AN, Nucleo UM, GDEY042T81-T02 panel DS, SSD1683/UC8276c controller DS (after verify), GT911 DS, SHT45 DS, SCD41 DS, BGT60LTR11AIP DS, BQ51013B DS, BQ25570 DS, LFP143060 spec, NC1000 + AAPI.

## Linked
- [Datasheet Stash](Datasheet_Stash.md) — stash location + folder layout
- [Brief](Brief.md) — authoritative component decisions
- [Schematic placeholder](Schematic_placeholder.md) — schematic file (placeholder until HW exists)
- [Procurement](Procurement.md) — procurement tiers; matches part-choice TBDs above
