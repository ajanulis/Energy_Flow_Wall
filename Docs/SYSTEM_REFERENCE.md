# Energy Flow Wall — System Reference

## Mesh & Communication
- NC1000 (mesh radio) is hardwired to PSoC5 with 3 wires: CTS, RX, TX. No button.
- Commands sent from Node-RED via TCP, running on RP5. RP5 is hardwired to a Gateway NC1000.
- NC1000 sends binary AAPI packets (not plain text). Start bytes: 0x52 or 0x54.
- Mesh has 2 modes:
  - **Normal**: all NC1000 nodes collect T/H from SHT45 sensors, send to NeoGateway on RP5
  - **ALT**: triggered by Node-RED when conditions met (e.g. temperature threshold); NC1000 stops T/H and switches to UART mode so any command can be sent to any mesh node

## Device Types in Mesh
- **Gateway**: RP5 + NC1000, runs NeoGateway TCP server, Node-RED, InfluxDB, Grafana
- **Actuator**: PSoC5 + NC1000 + DRV8411A + 2 motors + 2 encoders + SHT45. Controls flaps. Node IDs confirmed: 0x55, 0x66.
- **Device**: NC1000-only nodes collecting T/H data. Node IDs: 0x33, 0x44.

## Actuator Hardware (Main PCB — KiCad: Hardware/KiCad/Main_PCB_Based_on_8411A)

### ICs / Active components
- **U1 — PSoC5**: CY8C5888LTQ-LP097 (ARM Cortex-M3, 80MHz, 256KB flash, 68-QFN)
- **U2 — Motor driver**: DRV8411ARTER — single chip, dual H-bridge, drives both motors independently
  - AIPROPI / BIPROPI: current sense outputs (ratio 1:2000) → R11/R12 = 1K5Ω each → PSoC ADC
  - VREF: driven by PSoC VDAC8 (software-controlled OCP threshold)
  - nFAULT: active-low fault output → PSoC interrupt
  - AIN1/AIN2, BIN1/BIN2: PWM inputs from PSoC (PWM_1, PWM_2 components)
- **U3 — T/H sensor**: SHT45-AD1F-R2 (on Actuator board — reports its own T/H to mesh)
- **U4 — Motor supply**: TPS63020QDSJRQ1 buck-boost converter, Vin 1.8–5.5V → Vout **5.0V** (R7=1.8M, R10=200K)
  - L1 = XAL4020-152MEC 1.5µH inductor (Coilcraft, on the same supply)
  - Enabled only during motor motion (M_Power pin) to save battery
- **U5 — System supply**: AP7354-33W5-7 LDO → 3.3V for logic (PSoC, NC1000, SHT45, encoders)
- **U6 — Mesh radio**: NC1000C
- **Q1 — Polarity protection**: BUK6Y33-60PX PMOS FET (60V, 30A)

### Passive / discrete
- **D1**: Blue status LED (LTST-C170TBKT)
- **R7=1.8MΩ, R10=200KΩ**: TPS63020 output voltage setting → 5.0V
- **R11, R12=1K5Ω**: AIPROPI/BIPROPI current sense load resistors → PSoC ADC

### Connectors
- **J3**: BM03B-PASS-1-TFT — 3-pin JST, fan output (Fan_PWM → P2[3])
- **J4, J5**: FM20C06VBNN — 6-pin encoder connectors (A, B, power, GND per motor)
- **J1, J2, J6**: ECV3-06 Tag-Connect — programming/debug headers (PSoC + NC1000)
- **JP1**: SolderJumper_3_Bridged12 — motor power source selection
  - **1–2 bridged** (default): battery powered → routes supply through U4 (TPS63020 buck-boost) for stable 5V motor rail
  - **2–3 bridged**: regulated supply (e.g. USB 5V 2A) → bypasses U4 entirely, connects supply directly to motor rail
  - DNP in this config: U4, L1, R7, R10 (converter + frequency-setting components) and all decoupling caps on U4 Vin/Vout rails: C22, C23, C24 (22µF bulk), C25, C26, C29 (0.1µF bypass), C30, C31 (10µF bulk)

## Motors
- **Pololu #3078**: 250:1 (actual 248.98:1) Micro Metal Gearmotor HPCB 6V
  - Rated voltage: 6V (run at 5V from TPS63020 — ~17% derated, acceptable)
  - No-load: 130 RPM, 150 mA at 6V
  - Stall: 3.2 kg·cm torque, **1.5A** current (DRV8411A rated 1.92A peak — OK)
- 2 motors, **mechanically independent** (M1 and M2 drive separate flaps)
- Expected flap travel: ~180° (TBC by homing)

## Encoders (Encoder PCB V2.0 — KiCad: /Users/Shared/Projects/#Actuator_EFW/KiCad/Pololu_Encoder_V2/Encoder.kicad_pro_v2)
- Custom PCB, based on Pololu magnetic encoder design for Micro Metal Gearmotors
- **12 CPR** on motor shaft (Hall effect, sensor: TLE4946-2K, Infineon, SOT-23)
- Quadrature A+B only (no index). PSoC5 uses hardware QuadDec_3 / QuadDec_4 components.
- Effective resolution: 12 × 4 × 248.98 ≈ **11,951 counts/output shaft revolution**
- Expected counts for full travel (~90° at output shaft): **~3000 counts** (confirmed experimentally)
- Encoder power controlled by Hall_Pwr pin (off when not needed)
- **TO BE DONE (next PCB revision)**: Power encoders from TPS63020 5V rail (already auto-switched by M_Power hardware OR gate — free power control, no extra FET needed). Add 8× voltage divider resistors on main PCB (2 per signal × 4 signals: M1_A, M1_B, M2_A, M2_B) to bring 5V open-drain outputs down to ~3.3V for PSoC. Divider values: R_top=5.6K + R_bottom=10K → 3.2V at PSoC pin. Encoder PCB unchanged (R1/R2 pull-ups to Vcc stay). Result: encoders off during sleep at zero extra BOM cost vs a FET.

## PSoC5 Firmware — Key PSoC Creator Components
- QuadDec_3, QuadDec_4: hardware quadrature decoders for M1/M2 (2 QuadDecs, not 4)
  - 16-bit signed counters. API: `QuadDec_3_GetCounter()` → int16, `QuadDec_3_SetCounter(int16)`
  - Full output shaft revolution ≈ 6000 counts (2× decoding). Max flap travel ≈ 3000 counts.
  - Counter trick for precise position stop: SetCounter(32767−steps) for CCW → overflow ISR fires
    after exactly `steps` counts; SetCounter(steps−32768) for CW → underflow ISR fires.
  - isr_QuadDec3 / isr_QuadDec4: user ISR components; use `QuadDec_3_GetEvents()` in handler
    (flags: QuadDec_3_COUNTER_OVERFLOW, QuadDec_3_COUNTER_UNDERFLOW)
- PWM_1, PWM_2: motor speed control (0–255, 8-bit). API: `PWM_1_WriteCompare(uint8)`
- PWM_3: fan speed control. Output routed to Fan_PWM pin.
- VDAC8_1, VDAC8_2: OCP threshold per motor (0–255). VDAC8_3: VREF for DRV8411A
- Comp_1, Comp_2: OCP comparators. Outputs → M1_ovcr / M2_ovcr nets
- Opamp_1, Opamp_2: AIPROPI / BIPROPI signal conditioning
- Em_EEPROM: emulated EEPROM. Init: `Em_EEPROM_Init((uint32)storageArray)`.
  Read/Write: `Cy_Em_EEPROM_Read/Write(addr, data, size, &Em_EEPROM_context)`
- Hall_Pwr: pin exists in firmware but not connected in current HW — pin unused
  - **PCB TODO (next revision)**: encoder power will be switched via TPS63020 5V rail (see Encoders section) — Hall_Pwr pin may be repurposed or removed
- Fan_PWM: fan output pin (driven by PWM_3)
- IAQ_Pwr: not used, IAQ sensor not implemented

## PSoC5 Hardware Motor Control Architecture (from schematic)
Source: PSoC_schematics_full_w_8411A_w_interrupt_new.pdf

**M1_Go / M2_Go SR flip-flops (hardware state machine):**
- Pulse M1_Go pin HIGH → SRFF sets (Q=1) → de-asserts PWM_1 kill → motor runs
- QuadDec_3 overflow/underflow → resets M1_Go SRFF (Q=0) → asserts kill → motor stops
- M1_ovcr (OC latch) → also resets M1_Go SRFF → motor stops on overcurrent
- nFAULT (inverted) → resets both M1_Go and M2_Go SRFFs → emergency stop both

**M_Power (TPS63020 enable) is hardware-driven:**
- OR(M1_Go_SRFF_Q, M2_Go_SRFF_Q) → M_Power pin — automatic, no firmware control needed

**Status register (Status_Read() → uint8):**
| Bit | Mask | Meaning |
|-----|------|---------|
| 0 | 0x01 | M1 stopped (HIGH) / running (LOW) = !M1_Go_SRFF_Q |
| 1 | 0x02 | M2 stopped (HIGH) / running (LOW) = !M2_Go_SRFF_Q |
| 2 | 0x04 | M1 OC latched (M1_ovcr SRFF Q) |
| 3 | 0x08 | M2 OC latched (M2_ovcr SRFF Q) |
| 4 | 0x10 | nFAULT active (HIGH = DRV8411A fault) |

- isr_Status fires on any status bit change → use for interrupt-driven move completion
- RST_ovcr pin resets M1_ovcr + M2_ovcr SRFFs (clears OC latches)

**Motor start sequence:**
1. `ResetOCP()` — clear OC latches (RST_ovcr pulse)
2. `VDAC8_1_SetValue(startup_thresh)` — apply startup OCP override
3. `M1_Dir_Write(dir)` + `PWM_1_WriteCompare(pwm)` — set direction and speed
4. `M1_Go_Write(1); CyDelayUs(10); M1_Go_Write(0)` — pulse to set SRFF, motor starts
5. `CyDelay(d0_ms); VDAC8_1_SetValue(run_thresh)` — drop to running threshold

## Firmware Versioning
- Format: main_vX.Y.Z — continue from v1.3.103 (sleep working) / v1.3.104 (sleep disabled debug)
- Next version: v1.3.105
- Files in /Users/aidas/Desktop/

## PSoC5 Firmware — Critical Notes
- CyPmSaveClocks() / CyPmRestoreClocks() are critical for hibernate
- CTS line is shared between UART and wake interrupt
- Timeout protection needed for spurious wakes (WAKE_TIMEOUT = 200 × 10ms = 2s)
- Race condition prevention with shouldSleep flag (set BEFORE processing, checked FIRST in loop)

## Actuator Command Set (AAPI Port 4, via NC1000 mesh in ALT mode)
| Command | Description | TBD |
|---------|-------------|-----|
| M1 \<counts\> | Move motor 1 to absolute encoder position | - |
| M2 \<counts\> | Move motor 2 to absolute encoder position | - |
| S1 \<pwm\> | Set motor 1 speed (PWM duty cycle) | format TBD |
| S2 \<pwm\> | Set motor 2 speed (PWM duty cycle) | format TBD |
| T1 \<val\> | Set motor 1 running OCP threshold | units TBD |
| T2 \<val\> | Set motor 2 running OCP threshold | units TBD |
| T01 \<val\> | Motor 1 startup OCP threshold override (higher, to overcome stiction) | - |
| T02 \<val\> | Motor 2 startup OCP threshold override | - |
| D01 \<ms\> | Duration of motor 1 startup threshold override | - |
| D02 \<ms\> | Duration of motor 2 startup threshold override | - |
| H1 | Home motor 1 on demand | - |
| H2 | Home motor 2 on demand | - |

## Homing Sequence (per motor, M1 then M2 — sequential to avoid current spike)
1. Enable TPS63020 (M_Power pin)
2. Start motor at low speed (PWM=50/255) toward home1 direction
3. Monitor AIPROPI/BIPROPI for overcurrent → motor stalled → record as home1, zero encoder
4. Apply startup threshold override (T0x) for D0x ms at start of each move to overcome stiction
5. Reverse, run to opposite end at same speed, stall → record as home2
6. Compute travel = abs(home2 - home1) in encoder counts. Expected: ~3000 counts
7. If travel outside 3000 ± 20 counts:
   - Too few counts → insufficient torque: increase PWM by 5/255, retry from step 2
   - Max 3 retries; if still failing → send Alert to Node-RED, stop motors, await H1/H2
   - Way out of range (stuck) → same: Alert + stop
8. Save home1, home2, working PWM, thresholds to Em_EEPROM
9. Homing runs on every power cycle

### Homing parameters (confirmed)
- Starting PWM: 50/255
- PWM increment per retry: 5/255
- Max retries: 3, then Alert
- Valid travel range: 3000 ± 20 counts
- All values (PWM, thresholds) are 0–255 (8-bit, matching PWM_M1/M2 and VDAC8)

## Node-RED / RP5
- SSH: ssh rp5.local (user: aidas)
- Node-RED flows: ~/.node-red/flows.json, port 1880
- Deploy: curl -X POST http://localhost:1880/flows -H 'Content-Type: application/json' -H 'Node-RED-Deployment-Type: full' -d @~/.node-red/flows.json
- InfluxDB: db=neogw, measurement=htu21d, fields: tempC, rh, nodeIdHex (as field not tag)
- Grafana dashboard: /Users/aidas/Desktop/NeoCortec-dashboard-fixed.json

## Sensor Formulas (Node-RED function d110437aa9daf440)
- 0x33, 0x44 (HTU21D): T = -46.85 + 175.72 × raw/65536, RH = -6 + 125 × raw/65536; mask raw & 0xFFFC
- 0x55, 0x66 (SHT45): T = -45.0 + 175.0 × raw/65535, RH = -6.0 + 125.0 × raw/65535; mask raw & 0xFFFC

## GitHub
- Repo: https://github.com/ajanulis/Energy_Flow_Wall.git
- Contains: KiCad hardware designs (Main PCB, Encoder PCB V2.0, Gateway PCB, End PCB)
- Source code in separate private repo
