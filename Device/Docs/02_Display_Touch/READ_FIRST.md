# Display + Touch — reading priority

**Touch controller is confirmed FT6336U (FocalTech), NOT GT911 (Goodix).**
Verified 2026-06-15 from good-display.com/product/473.html → Downloads tab.

## Files in priority order

1. **`GDEY042T81-T02.pdf`** — panel spec from GoodDisplay. Init sequence + refresh modes.
2. **`FT6336U-DataSheet-V1.0.pdf`** — touch controller. I²C address 0x38, register map, touch-event format.
3. **`TPS65186_datasheet.pdf`** — HV PMIC for e-paper bias rails. Only need to read if going bare-panel route; if using the DESPI-M02 driver board, this is internal to that board.
4. **`GDEY42T81-T02-drawing.pdf`** — mechanical drawing. Useful when designing the enclosure cutout.
5. **`Catalog-New.pdf`** — GoodDisplay general catalogue. Reference only.

## Sample code archives — the gold mine

Three RARs were extracted in-place. **The one to mine first:**

### `S-GDEY042T81-FP-Touch20230405/` — the complete reference firmware

Targets STM32F103 (different family from our STM32U585, but chip-side code is 100% portable).
Key files:

- `HARDWARE/EPD/Display_EPD_W21.c/h` — e-paper SSD1683 driver: init sequence, refresh modes, framebuffer push.
- `HARDWARE/EPD/Display_EPD_W21_spi.c/h` — bare-metal STM32F1 SPI. **REPLACE** with STM32U5 HAL SPI when porting.
- `HARDWARE/FT6336/FT6336.c/h` — FT6336 touch driver: I²C reads, touch-event decoding, IRQ handling.
- `HARDWARE/I2C/i2c.c/h` — bare-metal STM32F1 I²C. **REPLACE** with STM32U5 HAL I²C when porting.
- `HARDWARE/Fonts/` — 7 bitmap fonts (8/12/16/20/24 px Latin, 12/24 px Chinese). **LIFT AS-IS.**
- `HARDWARE/GUI/GUI_Paint.c/h` — drawing primitives (lines, rectangles, text). Pure framebuffer code. **LIFT AS-IS.**
- `USER/main.c` — demo application; shows the init → loop → handle touch → refresh pattern.

### `FT6336_4.2DEMO20200914/` — older, FT6336-only

Subset of the above. Skip — the middle archive has everything.

### `T042T81&EPD_ESP32-20230523/` — ESP32 / Arduino

Useful as a reference for behaviour comparison only — Arduino style, not directly portable to STM32.

## Porting strategy when firmware bring-up starts

1. Create a fresh STM32U5 firmware project in CubeMX (pin mux, clock tree, HAL init).
2. **Lift fonts + GUI_Paint directly** into `firmware/device/lib/gui/`.
3. **Lift the e-paper init sequences** from `Display_EPD_W21.c`. Wrap them in your STM32U5 HAL SPI calls — the bytes sent to the panel are identical regardless of host MCU.
4. **Lift the FT6336 register reads** from `FT6336.c`. Wrap in HAL I²C calls.
5. **Replace** bare-metal F103 peripheral code with HAL equivalents — shape stays the same.
6. **Discard** the `STM32F10x_FWLib/` StdPeriph library — superseded by CubeMX HAL on U5.
7. **Recreate** the build setup as STM32CubeIDE or VSCode/PlatformIO project; Keil µVision files are ignored.

This saves ~1–2 weeks of firmware bring-up. The init sequences and waveform tables alone would otherwise be a multi-day reverse-engineering exercise.
