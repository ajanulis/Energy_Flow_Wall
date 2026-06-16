
# Sniffer — Future Premium Air-Quality Variant (EXPLORATORY)

**Status: concept only.** Not yet a committed product. Captured here so the idea isn't lost when the [Brief](Brief.md) decided "SCD41 only, leave full AQ out of the Device base SKU".

## Role
Standalone indoor air-quality monitor that joins the same NC1000 mesh as Device, Actuator, and Gateway. Use case: rooms where the customer wants full IAQ visibility (PM, VOC, NOx in addition to CO₂ + T/H), and where that data can also influence flap behavior on the Actuator via the Gateway.

Distinct from Device because:
- **Mains-powered** — no LiFePO₄ / MagSafe constraints, so fan-driven sensors are fine.
- **AQ-first** — display may or may not be present; the value-add is the sensor suite, not the user interface.
- **Different enclosure mechanics** — needs intake/exhaust airflow paths.

## Sensors (initial concept)
- **Sensirion SEN6x** — combined module covering CO₂ + T + RH + VOC + NOx + PM. Exact variant (SEN66 with CO₂, SEN65 without, SEN63C without NOx) TBD by feature target.
- **Bosch BMV080** — optional. **Fan-less laser PM1/PM2.5 sensor** (no moving air required). Could either replace SEN6x PM (run SEN6x fan-disabled for the gas sensors only, use BMV080 for PM) — quieter, lower power, smaller enclosure — or run alongside as redundancy. Decide based on power-vs-accuracy testing.

## Power & enclosure
- Mains-powered (USB-C PD or barrel jack TBD).
- Continuous operation, no aggressive sleep.
- Enclosure must accommodate fan airflow if SEN6x is the PM source. If BMV080 replaces PM in SEN6x, fan can stay off → much quieter, smaller enclosure possible.

## Mesh integration
- Same NC1000 + AAPI as Device and Actuator.
- New node-ID class TBD.
- Reports periodic AQ readings to Gateway in Normal mode. Could accept commands in ALT mode (e.g. force-measurement, calibration).

## Open questions (don't burn cycles on these until Device is shipping)
1. Is Sniffer a separate PCB or a populate-variant of the Device PCB? Device PCB already has PSoC6 + NC1000 + display + CapSense — adding SEN6x + BMV080 as a populate option could keep the SKU count low. But airflow paths in the Device enclosure may be incompatible with the wall-flush aesthetic, forcing a separate enclosure.
2. Does Sniffer need its own display, or just a status LED?
3. SEN6x variant choice — SEN66 (with CO₂) vs SEN65 (without, paired with separate SCD41) vs SEN63C (no NOx).
4. BMV080 — confirmed availability, evaluation board, accuracy vs SEN6x PM at low duty cycle, power figures from datasheet.

## Linked
- [Brief](Brief.md) — the base SKU that this product extends
- `schematic-actuator` (internal note) — reference for what an authoritative schematic file should look like
