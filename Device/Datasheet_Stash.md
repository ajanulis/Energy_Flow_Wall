
# Device datasheet stash

Path: `/Users/Shared/Projects/EFW/Device/Docs/`

Layout (mirrors subsystem grouping used in [Brief](Brief.md)):

```
01_MCU/             STM32U585 DS, RM0456, errata, Cortex-M33 PM (PM0264), TrustZone AN, Nucleo UM
02_Display_Touch/   GoodDisplay GDEY042T81-T02, SSD1683 controller, Goodix GT911
03_Sensors/         Sensirion SHT45, SCD41, Infineon BGT60LTR11AIP + radar AppNote
04_Power/           TI BQ51013B (Qi Rx), BQ25570 (PV harvester), LFP143060 spec, Würth Qi coil
05_Mesh/            NC1000 datasheet + AAPI guide (sibling copy of Actuator stash)
06_Misc/            optocouplers, output FETs, glue parts
```

Sibling convention: Actuator KiCad lives at `/Users/Shared/Projects/#Actuator_EFW/KiCad/` (`reference-kicad-locations` (internal note)). Device docs follow the same "Shared/Projects" root but use a non-hashed `EFW/Device/...` tree — single namespace for Device + future Sniffer + shared PV module.

Read this when a Device firmware or schematic session opens and you need register-level or peripheral-protocol detail. Verify the relevant PDF is actually present before quoting page numbers — the stash is populated incrementally.
