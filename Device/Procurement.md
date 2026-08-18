
# Device — Development Procurement List (2026-06-14)

Prepared to share with Poul to budget hardware needed before Device firmware + PCB work starts. Prices are USD, rounded, from major distributors (Digi-Key / Mouser) unless noted. Local taxes / shipping / NZD conversion not included. Exact prices to verify at point-of-purchase.

## Tier 1 — Essential (can't make progress without these)

| Item | Part / Source | ~Price USD | Purpose |
|---|---|---|---|
| **STM32U5 Nucleo Prototyping Board** | NUCLEO-U575ZI-Q (STMicroelectronics) — Digi-Key / Mouser | ~$33 | MCU bring-up, firmware development. Has on-board ST-LINK V3 programmer/debugger, Arduino + Zio + ST morpho headers, USB-C for power+programming. Native macOS workflow via STM32CubeIDE *or* VSCode + STM32-PlatformIO. **(MCU switched from PSoC6 to STM32U5 on 2026-06-15 — Aidas walked away from Infineon's PSoC tooling trajectory; STM32U5 also gives us 2 MB flash in a hand-solderable QFN-48 for the production board.)** |
| **Nordic Power Profiler Kit II** | PPK2 (Nordic Semiconductor) — Digi-Key / Mouser | ~$95 | **Settles the NC1000 1/sec ALT-mode wake question once and for all.** Also instruments every sleep current measurement on Device, sensor duty cycles, SCD41 single-shot energy, etc. Critical for proving the 6–12 month MagSafe interval before shipping. |
| **BGT60LTR11AIP Radar Shield2Go (full eval)** | **S2GORADARBGT60LTR11TOBO1** (Infineon) — RS Online / Farnell / Mouser | **~$50** (~$76 AUD ex-GST at RS Australia) | Full Shield2Go eval board. Has **mode-select switches** (autonomous vs SPI) + **threshold potentiometers** for tuning the four QS signals mechanically without firmware. Both modes directly useful for Device development. Far cheaper than the DEMO-BGT60LTR11AIP ($171). Don't confuse with the simpler SHIELDBGT60LTR11AIPTOBO1 ($40, discontinued at Digi-Key, autonomous-only-ish 4-pin module). |
| **GoodDisplay GDEY042T81-T02** (touch e-paper, 4.2" 400×300) | GoodDisplay direct or [buyepaper.com](https://buyepaper.com) | ~$35–50 | The display. Confirmed with touch overlay so this also covers GT911 evaluation. Order at least 2 (one for the bench, one as spare). |
| **DESPI-M02 Mini Driver Board** (or similar) | GoodDisplay direct | ~$15 | The TPS65186 HV driver + connector breakout. Plugs into the panel's FPC, exposes SPI to the STM32U5. Only needed if buying the bare panel — confirm whether the -T02 kit ships with one. |
| **Sensirion SCD41 Evaluation Kit** | SCD4x SEK — Digi-Key / Sensirion | ~$45–55 | CO₂ sensor on a breakout with SHT45 onboard too. Lets you validate single-shot energy + cadence + accuracy at room. |
| **Sensirion SHT45 breakout** | Adafruit 5665 or similar | ~$8 (skip if you have spare from Actuator pile) | T/H sensor on breakout. Probably already covered by the SCD41 SEK above. |
| **MagSafe magnet rings** | [AliExpress 10× set](https://www.aliexpress.com/item/1005007351344807.html) | ~NZ$11 (~$7) | Aidas already found this — 18-magnet pre-assembled rings. Two per Device-and-fixture set. |
| **LFP143060 LiFePO₄ pouch samples** | [lithium-lifepo4-battery.com](https://www.lithium-lifepo4-battery.com/lifepo4-battery-lfp143060-1800mah-3-2v/) — sample MOQ 5–10 | ~$50 + shipping | Battery cell for the Device. 1800 mAh, 14×30×60 mm. Used as final battery and as charging-rig load. |

**Tier 1 subtotal: ~$290–330 USD** + shipping (saved ~$12 vs the original PSoC6 kit budget by switching to the NUCLEO-U575ZI-Q).

## Tier 2 — Important (need before PCB tape-out)

| Item | Part / Source | ~Price USD | Purpose |
|---|---|---|---|
| **TI BQ51013B Qi Receiver EVM** | BQ51013BEVM-764 — Digi-Key / Mouser | ~$70 | Wireless charging Rx evaluation. Validate charging from a MagSafe pad onto LFP143060, measure efficiency. |
| **TI BQ25570 Solar Harvester EVM** | BQ25570EVM-206 — Digi-Key / Mouser | ~$50 | Solar harvester eval for the PV-module accessory SKU. |
| **MagSafe / Qi charging pad** | Anker MagGo, generic MagSafe puck, or Apple MagSafe Duo | ~$25–40 | The source side of the wireless charging — needed to bench-test BQ51013B + magnet ring + LFP charging chain. |
| **Small amorphous-Si solar panel** | Powerfilm SP3-37 (~$15) or 50×30 mm mono-Si sample | ~$15–25 | For the PV-module BQ25570 testing. |
| **Extra NC1000 modules** | NeoCortec NC1000C, qty 2–3 | ~$30 each = ~$90 | One to act as Device mesh node, one as spare. Possibly already covered by Aidas's existing NC1000 stock from Actuator work — confirm. |

**Tier 2 subtotal: ~$250–325 USD.**

## Tier 3 — Nice to have / risk reduction

| Item | Part / Source | ~Price USD | Purpose |
|---|---|---|---|
| **Saleae Logic 8** (or cheap clone $20) | Saleae / SparkFun | ~$400 (Saleae) or ~$20 (clone) | Debugging SPI / I²C / UART when something doesn't talk. Aidas may already own one. |
| **ST-LINK V3 MINI standalone programmer** | STLINK-V3MINIE — Digi-Key / Mouser | ~$11 | Only needed once moving from the NUCLEO board to a custom Device PCB. The on-board ST-LINK V3 on the NUCLEO covers Tier 1 work fine. Skip the $45 V3 SET — its extras (JTAG, SWO trace, USB-to-I²C bridge) aren't relevant for STM32U5 + USART debug print; if SWO trace ever becomes worth it, it's a $34 incremental purchase later. |
| **Pmod breakouts / jumper wires / 0.5 mm FPC adapters** | Adafruit / SparkFun assortment | ~$30 | The boring stuff that makes connecting heterogeneous parts possible on a bench. |
| **Second GoodDisplay panel — base GDEY042T81 (no touch)** | GoodDisplay | ~$25 | Optional A/B testing: how much does the PET overlay degrade contrast / refresh feel vs. bare e-paper? |

**Tier 3 subtotal: ~$90–490 USD** (huge range because of Saleae).

## Total

| Scenario | USD | NZD (~×1.65) |
|---|---|---|
| Tier 1 only (start firmware) | ~$310 | ~$510 |
| Tiers 1 + 2 (through PCB design) | ~$565 | ~$930 |
| Tiers 1 + 2 + 3 (everything incl. Saleae) | ~$990–1090 | ~$1680–1780 |

Realistic ask for Poul to cover the *productive* hardware (everything Aidas can't sensibly proceed without): **Tiers 1 + 2 ≈ ~$565 USD / ~$930 NZD**. Tier 3 can be added piecemeal as the project progresses.

## Things Aidas already has (no need to budget)

Verify before ordering — these are believed to be on-hand from Actuator work:
- Oscilloscope
- Bench power supply
- Soldering iron + hot-air rework (for hand-rework of QFNs)
- Multimeter
- Some NC1000 modules
- USB serial adapters
- LiPo / Li-Ion cells (not LFP though)

## What's deliberately NOT on this list

- **Custom Device PCB fabrication** — deferred until after firmware bring-up validates the architecture on the proto kit. JLCPCB / PCBWay assembly run will be separate cost (~$200–500 for a small batch of 5 boards including BGA assembly).
- **PV module PCB** — separate downstream SKU, not blocking.
- **Production enclosure (3D-printed or injection-molded)** — Aidas already prints, FDM cost is negligible.
- **NeoTools NC1000 development kit** — Aidas already has access via existing Actuator workflow.

## Update history

- 2026-06-14: Initial list, written after Device sensor / power / display / mesh / mechanical decisions locked.

## Linked
- [Brief](Brief.md) — what each kit supports
- [LFP Pouch Sources](LFP_Pouch_Sources.md) — battery sourcing detail
- [Sniffer Concept](Sniffer_Concept.md) — separate future product, no kits here yet
