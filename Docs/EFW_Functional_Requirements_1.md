# Energy Flow Wall (EFW) — Functional Requirements Document

**Version:** 0.8  
**Last Updated:** 2026-02-24  
**Status:** Draft

---

## 1. System Overview

The Energy Flow Wall (EFW) is a smart building ventilation system designed to automate ventilation valves for energy-efficient airflow control. The valves are incorporated into the top sash of the window and controlled by motorised actuators. The system uses a wireless mesh network to coordinate actuator nodes, enabling automated and remote control of valve positions to optimise indoor air quality, thermal comfort, and energy consumption. Efficacy testing has been conducted by the Fraunhofer Institute (Germany) and Aalborg University (Denmark).

---

## 2. Architecture

### 2.1 Network Topology

- **Mesh Protocol:** NeoCortec NC1000 mesh networking
- **Gateway:** NeoGateway software running on Raspberry Pi 5, hardwired to one NC1000 module
- **Node Types:** Actuator nodes, Device nodes

```
[Raspberry Pi 5 + NeoGateway]
        |
    [NC1000] ─── (mesh) ─── [NC1000] ─── [NC1000]
                               |               |
                          [PSoC CY8C5888]  [Device Node]
                          [Motor A] [Motor B]
```

### 2.2 Node Types

#### 2.2.1 Gateway Node
- **Hardware:** Raspberry Pi 5 in Argon One V5 Casted Aluminium case
- **Storage:** 256 GB NVMe SSD via Argon NVMe expansion board (faster boot, more reliable than microSD)
- **Wireless module:** NeoCortec NC1000-8 (868 MHz), external antenna mounted on Argon One V5 case
- **Display:** External mini OLED — shows IP address, CPU temperature, CPU core loads, memory utilisation
- **UPS:** Argon One V5 UPS planned (listed in Argon manuals, not yet available to order)
- **Software:** NeoGateway, Node-RED (automation logic), MQTT (message broker), Grafana (monitoring/visualisation)
- **Role:** Bridge between mesh network and higher-level control/monitoring systems
- **Interfaces:** UART to NC1000-8, Ethernet/WiFi for upstream connectivity

#### RPi ↔ NC1000-8 Wiring (4-wire)

| Signal | RPi 40-pin Header Pin |
|--------|-----------------------|
| NC1000 nReset | Pin 18 |
| NC1000 RX | Pin 24 |
| NC1000 TX | Pin 21 |
| NC1000 CTS | Pin 19 |

#### 2.2.2 Actuator Node
- **Hardware:** NC1000 + Cypress CY8C5888LTQ PSoC
- **Interface:** NC1000 to PSoC via UART — 3 signals: **RX, TX, CTS**. CTS used as wake signal for PSoC and as ready-to-communicate indicator from NC1000
- **Role:** Dual motor control for window flaps + fan PWM control
- **Motors:** 2 per node (Motor A, Motor B) — rotate flaps to open/close air pathways
- **Fan:** PWM-controlled via Port 3
- **Feedback:** Quadrature encoder per motor
- **Protection:** Overcurrent detection per motor
- **Power:** Battery-powered; PSoC in deep sleep during Normal mode, wakes on UART activity

#### 2.2.3 Device Node
- **Hardware:** TBD
- **Role:** TBD (sensors, switches, or other peripherals)

---

## 3. Functional Requirements

### 3.1 Gateway

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| GW-01 | Gateway shall receive and forward commands from upstream system to mesh nodes | High | Draft |
| GW-02 | Gateway shall relay status/telemetry from mesh nodes to upstream system | High | Draft |
| GW-03 | Gateway shall maintain persistent UART connection to local NC1000 module | High | Draft |
| GW-04 | Gateway shall support reconnection on UART failure | Medium | Draft |
| GW-05 | Gateway shall log mesh traffic for diagnostics | Low | Draft |

### 3.2 Actuator Node

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| AC-01 | Actuator shall receive motor commands via NC1000 wireless mesh | High | Draft |
| AC-02 | Actuator shall control two independent motors (Motor A, Motor B) via DRV8411A | High | Draft |
| AC-03 | Actuator shall track motor position using quadrature encoder feedback | High | Draft |
| AC-04 | Actuator shall detect and respond to overcurrent conditions per motor | High | Draft |
| AC-05 | Actuator shall report actual motor positions back through mesh after movement | High | Draft |
| AC-06 | Actuator shall execute position commands with configurable speed/ramp | Medium | Draft |
| AC-07 | Actuator shall support emergency stop command | High | Draft |
| AC-08 | Actuator shall retain last known motor positions on power cycle | Medium | Draft |
| AC-09 | PSoC shall remain in deep sleep during Normal mode | High | Draft |
| AC-10 | PSoC shall wake on CTS pin assertion by NC1000 | High | Tested |
| AC-11 | PSoC shall transmit current motor positions immediately on wake | High | Draft |
| AC-12 | PSoC shall not transmit to NC1000 until CTS is asserted | High | Tested |
| AC-13 | Actuator shall accept and execute fan PWM control commands | Medium | Draft |
| AC-14 | Actuator shall report position even if target not reached (mechanical fault) | High | Draft |

### 3.3 Device Node

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| DV-01 | TBD | - | Draft |

---

## 4. Communication Protocol

### 4.1 Physical Layer

- **Gateway ↔ NC1000:** UART (hardwired)
- **PSoC ↔ NC1000:** UART (hardwired), AAPI protocol
- **NC1000 ↔ SHT45:** Native NC1000 interface (no PSoC involvement)
- **Node ↔ Node:** NC1000 wireless mesh (NeoCortec proprietary)

### 4.2 Node ID Scheme

| Node Type | Node ID (Hex) |
|-----------|--------------|
| Gateway | 0x0010 |
| Actuator 1 | 0x0011 |
| Actuator 2 | 0x0012 |
| Actuator N | 0x0010 + N |
| Device nodes | TBD |

### 4.3 Mesh Operating Modes

### 4.3 Mesh Operating Modes

#### Normal Mode
- NC1000 on each node autonomously reads T & H data from SHT45
- Data is periodically transmitted to Gateway (Node ID 0x0010)
- PSoC is in deep sleep (power preservation — battery-powered nodes)
- Applies to both Actuator and Device nodes
- Future: CO2 sensor data to be added

#### Alternative Mode
- **Trigger:** Initiated by Gateway when monitored environmental thresholds are exceeded:
  - Temperature exceeds set limit, OR
  - Humidity exceeds set limit
  - Future: CO2 level exceeds set limit
- **Scope:** Entire mesh switches mode simultaneously (not per-node)

- **Activation sequence:**
  1. Gateway broadcasts switch to Alternative mode — entire mesh transitions
  2. NC1000 switches to UART mode on all nodes
  3. PSoC wakes up (triggered by NC1000 UART activity)
  4. On wake-up, PSoC immediately transmits current motor positions via UART ports
  5. PSoC parses incoming commands from Gateway:
     - New motor position commands (Motor A, Motor B)
     - Fan PWM level command
  6. PSoC executes received commands (motor movement, fan adjustment)
  7. Actuator reports actual achieved motor positions back to Gateway
     - Position may differ from commanded if mechanical obstruction or failure occurred
  8. Gateway switches entire mesh back to Normal mode
  9. PSoC returns to deep sleep
  10. Nodes resume periodic T & H (and future CO2) data collection

- **Timeout / retry handling:**
  - If Gateway does not receive motor position report after command, it waits 10 seconds
  - After 10 seconds, Gateway re-initiates Alternative mode (NC1000 switches to UART again)
  - PSoC waking up on UART activity should be sufficient to trigger position retransmission

#### Mode Transition Diagram
```
[Normal Mode] ──── threshold exceeded ────► [Alternative Mode]
    ▲                                              │
    │                                   NC1000 → UART mode
    │                                   PSoC wakes up
    │                                   PSoC sends positions
    │                                   Gateway sends commands
    │                                   Motors/Fan move
    │                                   PSoC reports positions
    │                                              │
    │         no response? wait 10s, retry Alt ───►│
    │                                              │
    └──────────── Gateway resets to Normal ────────┘
```

#### PSoC Power Management
- PSoC is in deep sleep during Normal mode (battery-powered)
- **Wake signal: CTS pin** — NC1000 asserts CTS when it transitions to UART mode (Alternative mode entry)
- PSoC ↔ NC1000 physical interface: **3 signals — RX, TX, CTS**
- On wake: PSoC immediately transmits current motor positions, then parses incoming commands
- Return to sleep: when mesh returns to Normal mode

> **Note:** NC1000 also sleeps most of the time and will not respond to any commands until it wakes up and asserts CTS. CTS must be monitored before any UART transmission is attempted in both directions — PSoC must not transmit until CTS is asserted by NC1000.

#### NC1000 UART Port Assignment

| Port | Assignment |
|------|------------|
| Port 0 | Reserved |
| Port 1 | Motor A position |
| Port 2 | Motor B position |
| Port 3 | Fan PWM control |

### 4.4 AAPI Protocol (NC1000 ↔ PSoC)

- Protocol used for communication between NC1000 module and PSoC firmware
- Commands received by NC1000 are forwarded to PSoC via AAPI over UART
- Known issue: "one packet delay" — response to a command arrives one packet late; must be accounted for in parsing logic
- AAPI parsing must handle complete packet detection before command execution

### 4.5 Command Reference

| Command | Direction | Description | Status |
|---------|-----------|-------------|--------|
| MOTOR_A_MOVE | Gateway → Actuator | Move Motor A to target position | Draft |
| MOTOR_B_MOVE | Gateway → Actuator | Move Motor B to target position | Draft |
| MOTOR_STOP | Gateway → Actuator | Emergency stop both motors | Draft |
| STATUS_REQ | Gateway → Actuator | Request current actuator status | Draft |
| STATUS_RESP | Actuator → Gateway | Motor positions, states, faults | Draft |

*(To be expanded)*

---

## 5. Hardware Reference

### 5.1 Key Components

| Component | Part | Role |
|-----------|------|------|
| Microcontroller | Cypress CY8C5888LTQ (PSoC 5LP) | Motor control, encoder reading, fault detection |
| Wireless module (Actuator/Device) | NeoCortec NC1000 | Mesh networking + native SHT45 interface |
| Wireless module (Gateway) | NeoCortec NC1000-8 (868 MHz, external antenna) | Mesh gateway radio |
| T&H Sensor | Sensirion SHT45 | Temperature & humidity, read natively by NC1000 |
| Motor driver | Texas Instruments DRV8411A | Dual H-bridge motor drive |
| Gateway hardware | Raspberry Pi 5 + Argon One V5 case + NVMe 256 GB | NeoGateway host |
| Gateway software | NeoGateway | Mesh-to-upstream bridge |
| Gateway display | Mini OLED | Local diagnostics (IP, CPU temp, load, memory) |

### 5.2 PSoC Peripherals Used

- Dual PWM for motor drive
- Quadrature Decoder (x2) for encoder feedback
- UART for NC1000 communication
- ADC or comparator for overcurrent sensing

### 5.3 Motor Drive

- **Driver IC:** Texas Instruments DRV8411A (dual H-bridge)
- One DRV8411A drives both Motor A and Motor B on the Actuator node

---

## 6. Known Issues / Development Notes

| ID | Area | Description | Status |
|----|------|-------------|--------|
| DEV-01 | AAPI/UART | "One packet delay" in UART communication — response arrives one cycle late | Resolved / Workaround in place |
| DEV-02 | AAPI | Proper packet boundary detection required before command execution | In progress |
| DEV-03 | Mesh | NC1000 mesh throughput limited — avoid high-frequency polling | Noted |

---

## 7. Open Questions

- What sensors or peripherals are planned for Device nodes beyond SHT45?
- DRV8411A control mode: IN/IN vs PH/EN?
- Target response time for actuator commands in Alternative mode?
- Mesh network size — number of Actuator/Device nodes expected?
- What are the specific threshold values for T, H (and future CO2) that trigger Alternative mode?
- Motor position units — encoder counts, degrees, or percentage of travel?
- Fan PWM range and resolution?

---

## 8. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-02-24 | Initial draft |
| 0.2 | 2026-02-24 | Added DRV8411A, SHT45, mesh modes, node ID scheme |
| 0.3 | 2026-02-24 | Added RPi software stack, Alternative mode flow, fault handling |
| 0.4 | 2026-02-24 | Added PSoC sleep/wake, fan control, NC1000 UART port assignments, 10s retry logic |
| 0.6 | 2026-02-24 | Corrected system overview: ventilation valve in window sash, added energy reduction goal and research partners |
| 0.7 | 2026-02-24 | Gateway hardware detailed: Argon One V5 case, NVMe 256GB, NC1000-8 at 868MHz, OLED display, planned UPS |
| 0.8 | 2026-02-24 | Added RPi ↔ NC1000-8 4-wire pin mapping (nReset, RX, TX, CTS) |
