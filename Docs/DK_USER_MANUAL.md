# Energy Flow Wall — Demo Unit User Manual

**For the Denmark team. First-time setup and operation of the shipped prototype.**

---

## 1. What's in the Box

1. **1× Actuator** — the wall unit itself. Contains PSoC5 + NC1000 mesh radio + 2 motors + 2 flaps + fan + built-in T/H sensor. Runs on 1× rechargeable 18650 cell (**not provided** — you'll need to source one).
2. **1× Gateway** — Raspberry Pi 5 with NeoCortec NC1000 mesh daughter board on top. Supplied with EU-compatible power supply.
3. **3× Xiaomi LYWSD03MMC room sensors** (custom ATC firmware). Labelled **Kitchen**, **Bedroom**, **Living**. **Shipped without batteries** — you need **3× CR2032**.
4. **Ethernet cable** for the Gateway.

**You will need to provide:**
- 1× rechargeable 18650 cell for the actuator (3.2 V LiFePO₄, 3.7 V Li-ion, or 4.2 V all work) + a suitable charger.
- 3× CR2032 coin cells for the Xiaomi room sensors.

---

## 2. First-time Setup (5 minutes)

### 2.1 Gateway
1. **Plug the Ethernet cable** from the Gateway into a free port on your router.
2. Plug the supplied power supply into the Gateway and into the wall.
3. Wait ~60 seconds for it to boot (green LED activity).

### 2.2 Actuator
1. Insert a charged 18650 cell into the actuator's battery holder (+ side in the direction marked on the holder). Polarity protection is fitted so a reversed cell won't damage anything, but it won't run either.
2. Power should come up automatically when the cell is seated.
3. On first power-up it runs an **auto-homing cycle** — the flaps move to both end-stops then park in the centre. Takes ~60 seconds. Normal. If you hear motor noise right after power-up, that's the auto-homing.

### 2.3 Room Sensors
1. Open each Xiaomi sensor (gentle pry on the case seam, no screws).
2. Insert a CR2032 battery (+ side up).
3. Close the case. Screen should display temperature + humidity after a few seconds.
4. Place in the rooms you want monitored.

---

## 3. Accessing the System

### 3.1 Control Dashboard — **Valve + Fan + Demo Mode**

Open in any browser on the same network:

**`http://rp5.local:1880/dashboard/valve-control-v2`**

If `rp5.local` doesn't resolve in Chrome or Brave (some browsers bypass `.local` DNS), use the IP instead:

**`http://10.0.0.123:1880/dashboard/valve-control-v2`**

Safari resolves `.local` natively.

### 3.2 Graphs — **Temperature + Humidity history**

**`http://rp5.local:3000`**

Login: a view-only Grafana account has been provided separately (see the email accompanying this manual).

Direct deep link to the NeoCortec board:
**`http://rp5.local:3000/d/170ba90a-9986-4e36-bd84-e81960c5e9b9/neocortec`**

---

## 4. Using the Control Dashboard

### 4.1 Valve Sliders
- **V1 slider** (0-100%) — Valve 1 position. 0 = fully closed end-stop, 100 = fully open end-stop. Moves the flap.
- **V2 slider** — Valve 2, same.
- **Fan slider** — fan speed, 0 (off) to 100 (max).

Slide and release. Command is queued and executed within a few seconds.

### 4.2 HOME button
Click **HOME** if the flaps ever look misaligned (unlikely but possible after a mechanical disturbance). It re-homes both valves. Takes ~60 seconds per valve. Turns green **HOMED OK** when done.

You can also home individual valves with **H1** and **H2** buttons.

### 4.3 Demo Mode
Click the **DEMO** button (grey, bottom of the page). It turns green **"DEMO ON"**.

In Demo Mode the system automatically follows the **room with the highest humidity** (Kitchen / Bedroom / Living / the actuator's own sensor). It drives the V1 valve position and Fan speed based on which room is "winning".

To test, breathe on one of the sensors for 5-10 seconds — humidity spikes, that sensor wins, the unit reacts within 30 s.

Click the button again to turn Demo Mode off.

### 4.4 Status Display

At the top of the page:
- **TX / RX** — last command sent and last reply received.
- **Pending** — commands queued.
- **Queue** — names of queued commands.
- **ALT / Normal** indicator — yellow when the mesh is in ALT mode (commands being sent), green when in Normal mode (sensors reporting).

---

## 5. Typical Usage Flow

1. Power everything on, wait for auto-homing to finish (~60 s).
2. Open dashboard — valves should show "HOMED OK" (green).
3. Drive V1 and V2 manually to see them work.
4. Insert room sensor batteries — watch them appear in the Grafana graphs.
5. Enable Demo Mode — observe the system respond to room humidity changes.

---

## 6. Troubleshooting

### "rp5.local" doesn't work
- Try `http://10.0.0.123` instead (IP fallback).
- Chrome and Brave sometimes bypass `.local` DNS. Safari always works.
- Confirm the Gateway is plugged into Ethernet and has a green link light.

### Dashboard shows **"NOT HOMED YET — click to home"**
- Press the **HOME** button. Wait ~90 s.
- If it ends with red "FAILED" or "COUPLER / ENC / MOTOR FAIL", something mechanical is off — send us a photo or video and we'll diagnose.

### Demo Mode doesn't react to sensor changes
- Confirm the room sensors have CR2032 batteries installed (screens show T/H).
- Check Grafana graphs — sensor data updates every ~15 s when healthy.
- Demo Mode only reacts when the *winner changes*. Small humidity differences may not flip the winner.

### Actuator battery flat
- Remove the 18650 and charge it in your Li-ion charger. 3.2 V LiFePO₄, 3.7 V Li-ion, and 4.2 V cells all work (development has been done on a 3.2 V LiFePO₄ 1800 mAh).
- Reinsert, it'll auto-home on power-up.

### Flaps make noise or sound harsh
- One valve uses a 250:1 gear ratio and the other 380:1 — they sound slightly different. Intentional, so you can compare and help inform the production choice. Final production gear ratio is **TBD**.

---

## 7. Contact

**Aidas Janulis** — a.janulis@gmail.com

Include in bug reports: screenshot of dashboard, screenshot of Grafana for the last hour, brief description. Happy to help over email or a quick video call.

---

## 8. Notes for DK Control-Algorithm Development

A separate technical document with the full command set (mesh protocol, AAPI ports, firmware commands, pipeline MQTT topics) will be shared directly with the person leading the control algorithm work. This keeps this user manual focused on operation rather than internals.

Dashboard-level commands sufficient for end-user operation:
- `V1,<0-100>` — valve 1 position %
- `V2,<0-100>` — valve 2 position %
- `F,<0-100>` — fan speed %
- `H` / `H1` / `H2` — home both / valve 1 / valve 2

These can be issued directly via MQTT (`efw/cmd/request` topic) if the dashboard UI is limiting.

---

*Document version: 2026-04-23 — matches shipped firmware v2.3.42 and pipeline/dashboard as of the same date.*
