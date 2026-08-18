# Energy Flow Wall — Command Reference

**Complete CLI / MQTT / firmware command reference.** Intended for developers and integrators. End-user operation is covered in [`DK_USER_MANUAL.md`](DK_USER_MANUAL.md).

---

## How to Issue Commands

All commands reach the PSoC firmware via the same pipeline:

```
You → MQTT (efw/cmd/request) → efw-pipeline → NeoGateway (TCP) → NC1000 mesh → PSoC UART
```

Three ways to send a command:

### 1. Interactive CLI (on the RP5)

```
ssh rp5.local
/home/aidas/efw-pipeline/venv/bin/python /home/aidas/efw-pipeline/efw_cli.py
```

You'll get a prompt like `efw>`. Type commands directly (see reference below). The CLI wraps MQTT for you and shows state transitions + replies.

### 2. Direct MQTT publish

From anywhere that can reach the broker (RP5 port 1883):

```bash
mosquitto_pub -t efw/cmd/request -m '{"id":"my-1","cmd":"V1","arg":"50","timeout_s":30}'
```

JSON fields:
- `id` (string) — unique ID you choose; echoed back in status/result
- `cmd` (string) — command name (see reference)
- `arg` (string, optional) — command argument
- `timeout_s` (number, optional) — override default command timeout
- `priority` (bool, optional) — jump the queue (reserved for FORCE_NORMAL etc.)
- `retries` (number, optional) — number of auto-retries on timeout (default 1)

### 3. Dashboard (Valve Control v2)

The user-facing buttons/sliders in `http://rp5.local:1880/dashboard/valve-control-v2` translate to the same MQTT requests.

---

## MQTT Topics

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `efw/cmd/request` | in → pipeline | Submit a command |
| `efw/cmd/status` | pipeline → out | State transitions: `queued` / `alt_on` / `sent` / `executed` / `alt_off` / `done` / `timeout` / `failed` |
| `efw/cmd/result` | pipeline → out | Terminal result with `outcome`: `ok` / `fail` / `timeout` and `reply` (firmware response string) |
| `efw/demo/enable` | in → demo brain | Toggle Demo Mode on/off (boolean payload) |
| `efw/demo/status` | demo brain → out | Demo Mode heartbeat text (winner + RH dump) |
| `efw/demo/rh/kitchen`, `/bedroom`, `/living` | Theengs/MQTT → demo brain | BLE sensor RH feed |

---

## Firmware Command Reference

Grouped by purpose. All values are **ASCII strings** sent via AAPI 0x03 on port 4. Replies arrive on port 4 from the actuator. All replies must fit in **21 bytes** (NC1000 AAPI payload limit).

### Queries (no argument)

| Command | Reply | Notes |
|---------|-------|-------|
| `V`  | `v2.3.42` | Firmware version string |
| `HS` | `HS=<v1>,<v2>` | Homing status per valve. Each field: `OK` / `NONE` / `COUPLER` / `ENC` / `MOTOR` / `FAIL` |
| `TR` | `TR=<m1_tr>,<m2_tr>` | Travel counts from EEPROM per motor |
| `V1` / `V2` | `V1=<pct>` / `V2=<pct>` | Current position as percent of travel (integer, truncated) |
| `F`  | `F=<pct>` | Current fan percent |
| `S1` / `S2` | `S1=<pwm>` / `S2=<pwm>` | Current motor PWM (0-255) |
| `T1` / `T2` | `T1=<val>` / `T2=<val>` | Per-motor OCP threshold VDAC8 value (0-255) |
| `T0` | `T0=<val>` | Startup T boost (added to T1/T2 for TD ms after M_Go) |
| `TD` | `TD=<ms>` | Duration of startup T0 boost (0-500 ms) |
| `GCC` | `GCC=<val>` | Global current ceiling (DRV8411A VREF) VDAC8_3 value (0-255) |
| `M1` / `M2` | `M1=<counts>` / `M2=<counts>` | Current absolute position, relative to `g_zero` (signed) |
| `SR` | (sets internal variable) | Read Status register snapshot |

### Valve Position (percent)

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `V1,<0-100>` | percent | Drive M1 to `(pct × tr / 100)` counts. Reply: `V1=<actual_pct>,<stop>` where `<stop>` = `Q`/`S`/`O`/`F`/`T`/`t`/`?` |
| `V2,<0-100>` | percent | Same for M2 |

Stop codes:
- `Q` — reached target (success)
- `S` — stalled short of target (watchdog fired)
- `O` — OCP tripped (current > T)
- `F` — nFAULT (DRV8411A hardware fault)
- `T`/`t` — inrush phase timeout (Phase 1 = T too high / Phase 2 = T too low)
- `?` — unknown stop reason

If the valve hasn't been homed, reply is `V1=NOT_HOMED`.

### Fan Speed (percent)

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `F,<0-100>` | percent | 0 = fan off. 1..100 maps non-linearly to PWM 38..255 (so "1 %" is already the minimum smooth-running speed — below 38 the fan stutters). Reply: `F=<pct>` |

### Homing

| Command | Reply (success) | Reply (fault) | Notes |
|---------|-----------------|---------------|-------|
| `H` | `H=OK` | `H=FAIL` | Home both valves. Success also emits per-motor `H1=OK,s,t,tr` + `H2=OK,s,t,tr` first |
| `H1` | `H1=OK,<s>,<t>,<tr>` | `H1=BROKEN_COUPLER` / `H1=ENC_FAIL` / `H1=MOTOR_FAIL` / `H1=FAIL` | Home valve 1 only |
| `H2` | `H2=OK,<s>,<t>,<tr>` | (same pattern) | Home valve 2 only |

Auto-home runs iteration loop: find min S where homing + 3-move validation pass, save `<s>`, `<t>`, `<tr>` to EEPROM, final re-home at `s_good`, park at `tr/2` (centre). Duration typically 30-90 s depending on motor/iteration count.

### Motor Control (raw, for dev / calibration)

**Prefer `V1` / `V2` for normal use.** M1/M2 take raw encoder counts, which are
**not comparable between motors** — the DK demo unit ships with mixed gear
ratios (M1: 250:1, full travel ≈ 715 counts; M2: 380:1, full travel ≈ 1095
counts), so `M1,500` ≈ 70 % open while `M2,500` ≈ 46 % open. V1/V2 divide
internally by each motor's stored travel range and stay correct across
hardware swaps.

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `M1,<counts>` | signed int16 | Drive M1 to absolute position `<counts>` relative to `g_zero`. Reply: `M1=<actual>,<stop>` |
| `M2,<counts>` | signed int16 | Same for M2 |
| `M1,32768` / `M2,32768` | (special) | **Emergency stop** — wraps to -32768 = immediate QuadDec UNDERFLOW, SRFF resets, motor stops instantly |

**Never use `M1,32766` or `M2,32766` for stop** — those are real targets (move 32766 counts). Only `32768` triggers the overflow stop trick.

### Motor PWM (speed, triggers CALT when set)

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `S1,<0-255>` | PWM value | Sets `g_m1_pwm`, then runs CALT to find new T1 threshold at this speed. Reply: `S1=<pwm>,T=<new_t>` or `S1=<pwm>,CALT_FAIL` |
| `S2,<0-255>` | PWM value | Same for M2 |
| `S1,+<delta>` / `S1,-<delta>` | relative | Add or subtract from current PWM |
| `S2,+<delta>` / `S2,-<delta>` | relative | Same for M2 |

CALT takes ~5-10 s (sweeps T to find minimum that lets the motor run).

### OCP Threshold (dev only — `S1,N` / `S2,N` auto-sets these)

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `T1,<0-255>` | VDAC8 value | Directly sets M1 OCP threshold. `I_trip = val × 0.008 A` (val × 16 mV / 10 kΩ / 200 µA·A⁻¹) |
| `T2,<0-255>` | VDAC8 value | Same for M2 |

**Warning:** setting T too low → OCP trips during normal running; too high → OCP never fires, motor can stall without detection. Normally auto_home + `S1,N` manage these for you.

### Calibration

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `CALT` / `CALT1` / `CALT2` | none | Calibrate minimum T for motor 1, 2, or both. Runs short 12-step test moves, alternating direction, with T sweeping from 25 up until motor runs without tripping, then sweeps back down to find the edge. Result stored in `g_calt_min1` / `g_calt_min2` |
| `CALMIN` | none | Calibrate minimum PWM that keeps motor moving (per-motor). Takes 10-30 s |
| `INRUSH1` / `INRUSH2` | none | Capture inrush phase timing. Reply includes t1/t2 ms for that motor's last run |

### Advanced / Debug

| Command | Arg | Behaviour |
|---------|-----|-----------|
| `T0,<0-50>` | value | Startup T boost (added to T1/T2 for the first TD ms of a move, helps overcome stiction) |
| `TD,<0-500>` | ms | Duration of the T0 boost |
| `D,<0-1000>` | ms | Gate delay (diagnostic only — normally 0). Formerly used during OCP gate-open tuning |
| `GCC,<0-255>` | VDAC8 | Global current ceiling. `I_max = val × 0.008 A`. Default 125 = 1.0 A |
| `RP` / `RT` / `RS` | none | Set report type: Position / Threshold / Speed — changes `build_status()` output on next reply |
| `ZP` / `ZP1` / `ZP2` | none | Zero position (both / motor 1 / motor 2) — captures current `QuadDec_1/2` as new `g_zero`. **Not typically useful on its own** — auto_home sets zeros correctly |

### Emergency Stop

```
M1,32768    ← stops motor 1 immediately
M2,32768    ← stops motor 2 immediately
```

These wrap to `-32768` in int16 which fires an immediate QuadDec UNDERFLOW ISR, resetting the motor SRFF. Use these if a move is stuck or you want to abort.

---

## FORCE_NORMAL (Pipeline-level, not firmware)

Cancel whatever command is in flight and return to Normal mesh mode immediately. Sent via MQTT:

```bash
mosquitto_pub -t efw/cmd/request -m '{"id":"fn-1","cmd":"FORCE_NORMAL","priority":true}'
```

Also accessible via the dashboard Emergency Stop button (if wired).

---

## Useful MQTT Command Recipes

**Find current firmware version:**
```bash
mosquitto_pub -t efw/cmd/request -m '{"id":"v1","cmd":"V","timeout_s":15}'
mosquitto_sub -C 1 -t efw/cmd/result
```

**Open both valves to 100 %, fan max:**
```bash
for cmd in '"V1","arg":"100"' '"V2","arg":"100"' '"F","arg":"100"'; do
  mosquitto_pub -t efw/cmd/request -m "{\"id\":\"c$RANDOM\",\"cmd\":$cmd}"
  sleep 8
done
```

**Home both valves:**
```bash
mosquitto_pub -t efw/cmd/request -m '{"id":"h1","cmd":"H","timeout_s":180}'
```

**Query stored travel (useful after homing):**
```bash
mosquitto_pub -t efw/cmd/request -m '{"id":"tr1","cmd":"TR"}'
```

**Enable Demo Mode:**
```bash
mosquitto_pub -t efw/demo/enable -m 'true'
```

---

## Default Command Timeouts (from `CMDS` dict in `efw_pipeline.py`)

| Cmd | Timeout | Cmd | Timeout |
|-----|---------|-----|---------|
| `V`, `F`, `S1/2`, `T1/2`, `T0`, `TD`, `GCC` | 10 s | `HS`, `TR`, `TL` | 10 s |
| `M1`, `M2`, `V1`, `V2` | 30 s | `ZP`, `ZP1`, `ZP2` | 10 s |
| `H1`, `H2` | 60 s | `H` | 90 s |
| `CALT`, `CALMIN`, `INRUSH*` | depends — use long `timeout_s` override in MQTT payload | | |

---

## Notes on Payload Limits

NC1000 AAPI payloads are hard-capped at **21 bytes** in both directions. All firmware replies fit inside this (e.g. `H1=OK,80,39,709` = 15 chars). If you add new commands, keep replies short.

Integer-percent rounding in `V1`/`V2` replies means small discrepancies between commanded and reported position are normal (e.g. command `V1,50` at a motor parked at 346/715 counts reports `V1=48` because `346 × 100 / 715 = 48.39 → 48` integer truncation).

---

*Document version: 2026-04-23 — matches firmware v2.3.42 and pipeline as of the same date.*
