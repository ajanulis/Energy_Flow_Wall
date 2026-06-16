
# Device — Pre-Hardware Prep (while the kit ships)

Kit ordered from Element14 NZ 2026-06-15: NUCLEO-U575ZI-Q + Nordic PPK2 + BGT60LTR11AIP Shield2Go + Sensirion SCD41 SEK + STLINK-V3MINIE. Plus parallel orders to GoodDisplay (touch e-paper) and lithium-lifepo4-battery.com (LFP143060 samples). Estimated arrival: 1–3 weeks depending on customs.

This memo captures the productive work that can happen *before* anything physical is on the bench.

## Where the docs live

```
/Users/Shared/Projects/EFW/Device/Docs/
├── 01_MCU/             STM32U585 datasheet, RM0456, PM0264, ES0499, NUCLEO + STLINK manuals
├── 02_Display_Touch/   GDEY042T81-T02 spec, SSD1683 controller, GT911 touch, TPS65186 PMIC
├── 03_Sensors/         SCD4x datasheet + LP app note, SHT4x, BGT60LTR11AIP datasheet + autonomous AN
├── 04_Power/           BQ51013B + design considerations, BQ25570, LFP143060 spec
├── 05_Mesh/            NC1000 datasheet, NeoCortec AAPI specification
├── 06_Misc/            Nordic PPK2 user guide, LTV-356T opto, DMG2305UX MOSFET
└── DOWNLOADS_TODO.md   list of files still to manually download (ST, Infineon, Goodix, etc.)
```

Re-runnable downloader: `/tmp/efw_device_grab_datasheets.py` (idempotent, skips files already present).

## Suggested reading order

### Priority 1 — read before the kit arrives (~4 hours total)

The four documents whose foundational knowledge unlocks everything else.

1. **STM32U585 datasheet** — chip overview, pin map, package, electrical specs. ~150 pages. **Focus on:** block diagram, pin allocation table, power supply rails, the section on Standby + WKUP-pin selection (critical for NC1000 CTS-wake).
2. **RM0456 reference manual** — peripheral register-level reference. ~2600 pages, *don't read end-to-end*. **Focus on:** TOC, Chapter 6 (clock tree), Chapter 9 (low-power modes — Standby, Stop3, Shutdown), Chapter on EXTI (external interrupts — for the WKUP pin).
3. **UM2861 — NUCLEO-U575ZI-Q user manual** — board pinout, headers (Arduino + Zio + ST morpho), KitProg3 wiring, jumper map.
4. **PM0264 Cortex-M33 programming manual** — read the sleep/wake chapter and the interrupt priority chapter. ~30 pages of relevant material out of ~280 total.

### Priority 2 — read as the kit arrives (~3 hours total)

Peripheral-specific docs for the bring-up work.

5. **GDEY042T81-T02 spec** — display init sequence, refresh-mode commands (full, partial, fast, 4-grayscale). Critical for the display driver.
6. **SSD1683 controller datasheet** — register map for the on-glass controller. Where the SPI bytes actually go.
7. **FT6336U (FocalTech) touch controller datasheet** — I²C protocol (default address 0x38), register map, touch-event format. *Note: confirmed 2026-06-15 that GDEY042T81-T02 uses FT6336U, NOT GT911 as previously assumed. GoodDisplay's product-page Downloads tab supplies STM32 reference code for the FT02/T02 panel + touch — start there rather than writing the driver from scratch.*
8. **SCD4x datasheet** — I²C command set, single-shot vs periodic mode comparison.
9. **SCD4x low-power application note** — exactly the duty-cycling pattern we want for the 5-min cadence.
10. **BGT60LTR11AIP datasheet** — autonomous mode pin descriptions (motion-detect output, direction output, sensitivity potentiometers on the Shield2Go).
11. **BGT60LTR11AIP autonomous mode app note** — the *only* radar mode we plan to use; SPI mode is for tuning only.

### Priority 3 — read when actually implementing that subsystem

12. **TPS65186** — only if going bare-panel route, skip if using DESPI-M02 driver board.
13. **BQ51013B + design considerations** — coil selection + layout when designing Device PCB.
14. **BQ25570** — defer until the PV-module accessory work begins (weeks 4–6).
15. **NC1000 + AAPI spec** — you already know these from the Actuator; quick refresher when wiring the USART driver.

## macOS toolchain setup (can complete without HW)

Verify the development environment works end-to-end against an empty STM32U585 project. Don't need the NUCLEO board for any of this until step 8.

1. Install **STM32CubeIDE** from st.com → free, native macOS, Eclipse-based. *Or* install **VSCode** + the **STM32 for VSCode** extension + **PlatformIO**. PlatformIO is lighter and more modern; CubeIDE is the path-of-least-resistance.
2. Install **STM32CubeMX** (separate app, pin allocation + clock-tree configurator that generates init code). Often bundled with CubeIDE.
3. Install ARM toolchain: `brew install --cask gcc-arm-embedded` (gets `arm-none-eabi-gcc`). CubeIDE bundles its own copy too.
4. Install OpenOCD: `brew install open-ocd` (needed if using VSCode/PlatformIO; CubeIDE bundles its own programmer).
5. Install **nRF Connect for Desktop** from nordicsemi.com → enables the **Power Profiler** app for the PPK2 when it arrives.
6. In CubeMX, create a new project for `STM32U585CIU6` package (QFN-48). Generate code.
7. In CubeIDE / PlatformIO, build the empty project. **Success = toolchain is working.** No flashing yet.
8. (When the NUCLEO board arrives) plug USB-C, run "Program" — confirms ST-LINK is recognised on macOS.

## Firmware scaffolding (skeleton-only, no HW needed)

When ready to commit to the project structure:

1. Create `Energy_Flow_Wall_Code/firmware/device/` (alongside `firmware/actuator/` — if the latter doesn't exist yet, do the restructure as part of this).
2. CubeMX project file with anticipated pin assignments:
   - **SPI1** → e-paper + radar (separate CS lines: PA4 for e-paper, PB6 for radar)
   - **I²C1** → shared SCD41 (0x62) + GT911 touch (0x5D), pull-ups on board
   - **USART2** → NC1000 (TX, RX, CTS) — **CTS must route to a WKUP pin** (PA0 / PC13 / PE6 are the candidates; choose based on rest of pinmux)
   - **GPIO**: BGT60LTR11AIP IRQ, GT911 IRQ + RST, opto-in ×2, MOSFET-out ×2, e-paper BUSY + RST + DC
   - **ADC1** → battery voltage divider
3. CMakeLists.txt or use CubeIDE's Makefile output — either fine.
4. Clone / vendor open-source libraries we'll pull in:
   - **LVGL** (graphics library): https://github.com/lvgl/lvgl
   - **GxEPD2** (e-paper, has STM32 ports): https://github.com/ZinggJM/GxEPD2 — adapter pattern, easy to lift the SSD1683 backend.
   - **Sensirion SCD4x driver** (official C library): https://github.com/Sensirion/embedded-i2c-scd4x
   - **Infineon RDK-TR11 SDK** for the radar: search "BGT60LTR11AIP driver github" — Infineon publishes example code.
5. Draft a top-level state machine sketch: idle/sleep → wake-on-touch / wake-on-CTS / wake-on-radar / wake-on-RTC-tick → service event → return to sleep.
6. Sketch the power-state diagram (Standby / Stop3 / Sleep / Run) and which wake-sources trigger which.

## Three things to do today (no HW needed)

If you want concrete tasks for an hour or two right now:

- [ ] Click through `DOWNLOADS_TODO.md` and grab the 6 ST PDFs into `01_MCU/`. They're the highest-value reading material and the easiest manual download.
- [ ] Install STM32CubeIDE (or VSCode + PlatformIO) and confirm an empty STM32U585 project compiles.
- [ ] Open the STM32U585 datasheet to the WKUP-pin section and decide which pin NC1000 CTS will route to. Note the choice for the PCB design.

## Linked

- [Brief](Brief.md) — the architectural locks this is preparing to implement
- [Procurement](Procurement.md) — what's being shipped that this prep is for
- [Schematic placeholder](Schematic_placeholder.md) — the file this prep eventually produces (PSoC reference replaced by STM32U585)
- `reference-psoc-flash-workflow` (internal note) — Actuator's flash workflow; the STM32 equivalent (just CubeIDE's "Program" button on macOS, no VM dance) is much simpler
