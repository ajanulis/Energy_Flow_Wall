# Energy Flow Wall (Public)

Public hardware/reference repository for the Energy Flow Wall mesh-networked
ventilation valve system, organized by subsystem:

```
Actuator/   Wall-mounted valve unit — KiCad PCB designs, Fusion 360 case, manuals
Gateway/    Raspberry Pi + NC1000 mesh gateway — NeoCortec protocol docs
Device/     In-room e-paper touchscreen — hardware planning, procurement, datasheets
Docs/       Whole-system docs (functional requirements, architecture reference)
```

Source code (firmware, Gateway pipeline, Node-RED deploy scripts) is
maintained in a separate private repository. `Device/`'s own progress
notes, photos, and manuals are also published separately, publicly, at
[Energy_Flow_Wall_Device](https://github.com/ajanulis/Energy_Flow_Wall_Device).

---

## Actuator

The wall unit itself — PSoC5 + NC1000 mesh radio + motors + flaps + fan.

- [`Actuator/KiCad/`](Actuator/KiCad/) — PCB designs.
- [`Actuator/Actuator_EFW#4_based_on_8411A v4_non_symmetrical_case.f3d`](<Actuator/Actuator_EFW%234_based_on_8411A%20v4_non_symmetrical_case.f3d>) — Fusion 360 mechanical design (non-symmetrical case, v4). Open with Autodesk Fusion 360; all parametric history included. [Direct download](<https://github.com/ajanulis/Energy_Flow_Wall/raw/main/Actuator/Actuator_EFW%234_based_on_8411A%20v4_non_symmetrical_case.f3d>).
- [`Actuator/Manuals/DK_USER_MANUAL.md`](Actuator/Manuals/DK_USER_MANUAL.md) — End-user manual for the shipped demo unit: setup, dashboard usage, Demo Mode, troubleshooting.
- [`Actuator/Manuals/COMMANDS.md`](Actuator/Manuals/COMMANDS.md) — Developer/integrator reference: MQTT topics, JSON request format, full firmware command set, timeouts.

**Hardware**: PSoC 5 (CY8C5888LTQ-LP097) · DRV8411A motor driver · NC1000 mesh radio · UART 115200 baud.

## Gateway

Raspberry Pi 5 + NC1000 daughterboard, running NeoGateway + Node-RED +
the MQTT⇌mesh pipeline.

- [`Gateway/KiCad/Gateway_PCB/`](Gateway/KiCad/Gateway_PCB/) — the RPi/NC1000 HAT PCB design (moved here from `Actuator/KiCad/`, where it was previously grouped by mistake).
- [`Gateway/NeoCortec/`](Gateway/NeoCortec/) — NeoCortec integration manual, NC1000 datasheet, and UART communication spec — the protocol reference the Gateway pipeline implements against.

## Device

In-room e-paper touchscreen display — hardware planning stage docs (see
the [public Device repo](https://github.com/ajanulis/Energy_Flow_Wall_Device)
for live progress/photos of the working unit).

- [`Device/README.md`](Device/README.md), [`Device/Brief.md`](Device/Brief.md) — concept + scope.
- [`Device/Procurement.md`](Device/Procurement.md), [`Device/Datasheet_Stash.md`](Device/Datasheet_Stash.md) — parts sourcing and reference datasheets.
- [`Device/HW_Prep.md`](Device/HW_Prep.md), [`Device/Doc_Gaps.md`](Device/Doc_Gaps.md) — bring-up prep notes and known documentation gaps.

## Docs (whole-system)

- [`Docs/SYSTEM_REFERENCE.md`](Docs/SYSTEM_REFERENCE.md) — high-level system reference (architecture, mesh layout).
- [`Docs/EFW_Functional_Requirements_1.md`](Docs/EFW_Functional_Requirements_1.md) — original functional requirements document.

---

**Questions?** Contact the repository owner.
