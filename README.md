# Energy Flow Wall - CAD Files (Public)

**Public repository** for sharing Fusion 360 3D CAD models of the Energy Flow Wall actuator.

## Files

### 3D CAD Model
- **Actuator_EFW#4_based_on_8411A v4_non_symmetrical_case.f3d** - Fusion 360 design file

## Download

You can download the Fusion 360 file directly:

**Direct Download Link:**
```
https://github.com/ajanulis/Energy_Flow_Wall/raw/main/Actuator_EFW%234_based_on_8411A%20v4_non_symmetrical_case.f3d
```

## Project Overview

This is the mechanical design for an Energy Flow Wall actuator based on the DRV8411A motor driver chip. The design features:

- Non-symmetrical case (version 4)
- Integration with PSoC 5 (CY8C5888LTQ-LP097) microcontroller
- NC1000 mesh network module support
- Motor driver circuitry based on DRV8411A

## Hardware Components

- **Microcontroller:** PSoC 5 (CY8C5888LTQ-LP097)
- **Motor Driver:** DRV8411A
- **Communication:** NC1000 Mesh Network Module
- **Interface:** UART (115200 baud)

## Documentation

- [`Docs/DK_USER_MANUAL.md`](Docs/DK_USER_MANUAL.md) — End-user manual for the shipped demo unit: setup, dashboard usage, Demo Mode, troubleshooting.
- [`Docs/COMMANDS.md`](Docs/COMMANDS.md) — Developer/integrator reference: MQTT topics, JSON request format, full firmware command set, timeouts.
- [`Docs/SYSTEM_REFERENCE.md`](Docs/SYSTEM_REFERENCE.md) — High-level system reference (architecture, mesh layout).
- [`Docs/EFW_Functional_Requirements_1.md`](Docs/EFW_Functional_Requirements_1.md) — Original functional requirements document.

## Related Repositories

The source code (firmware, RP5 pipeline, Node-RED deploy scripts) is maintained in a separate private repository. The documents above cover everything needed to interact with the system over MQTT without touching the source.

---

## License

This CAD file is provided for collaboration and reference purposes.

## Opening the File

1. Download the `.f3d` file
2. Open with **Autodesk Fusion 360**
3. All design features and parametric history are included

---

**Questions?** Contact the repository owner.
