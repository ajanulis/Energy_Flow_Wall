
# Device Schematic — Authoritative Reference (PLACEHOLDER)

**Status: hardware not yet designed.** Nothing in this file is ground truth yet.

When the Device PCB + MCU TopDesign exist, this file gets populated the same way `schematic-actuator` (internal note) was — written page-by-page from the actual PDF schematic together with Aidas. Do NOT infer schematic topology from code, synthesis reports, or assumptions — only from the PDF or Aidas confirmation.

Until then, design intent lives in [Brief](Brief.md). Open hardware questions to resolve before this file can be written:

- ~~MCU choice~~ — **decided 2026-06-15**: STMicroelectronics **STM32U585CIU6** (QFN-48, Cortex-M33 @ 160 MHz, 2 MB flash, 786 KB RAM). See `device_brief.md` for rationale. Schematic will document final peripheral pin assignments (SPI for e-paper + radar, I²C for SCD41 + GT911 touch, USART for NC1000 CTS-wake, GPIO for opto-in / MOSFET-out, ADC for battery monitor).
- E-paper panel model + controller + SPI pin map + refresh timing
- CO₂ sensor candidate (SCD41 / SCD30 / SGP41) and its I²C bus sharing with SHT45
- Presence sensor type (PIR binary vs. mmWave continuous)
- Potential-free I/O channel count, isolation, max voltage/current
- Touch button mechanism (cap-touch direct to MCU vs. dedicated controller)
- LiFePO₄ pack: cell count, BMS, charge current, MagSafe coil + receiver IC selection
- Solar input topology (when populated) and its interaction with the wireless-charge path
- Magnet layout for MagSafe alignment + how it coexists with NC1000 antenna routing
