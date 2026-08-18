
# LFP Pouch Cell — Sourcing Reference (2026-06-14)

For Device project — Aidas wanted ANY verifiable producer making LFP pouch cells; the cylindrical-only market is well-trodden but pouch LFP is a niche. Three real options confirmed below.

## Primary — LFP143060 (1800 mAh, 14 × 30 × 60 mm)

- **Vendor**: lithium-lifepo4-battery.com — claims 10+ years as LFP manufacturer (China).
- **URL**: https://www.lithium-lifepo4-battery.com/lifepo4-battery-lfp143060-1800mah-3-2v/
- **PN encodes geometry**: `LFP` (chemistry) + `14` (thickness mm) + `30` (width mm) + `60` (length mm).
- **Specs**: 1800 mAh, 3.2 V nominal, 5.76 Wh, integrated protection PCB, >2000 cycles claimed.
- **Sample MOQ**: 5–10 pieces.
- **Sample lead time**: 3–5 days.
- **Production scale**: vendor claims 100k+ unit capacity.
- **What to verify on sample**: exact dimensions, weight, protection-PCB cutoff thresholds (overcharge / overdischarge / overcurrent), actual capacity at 0.2C discharge, internal resistance, behaviour from BQ51013B (MagSafe Rx) charge input.

## Backup #1 — Grepow

- **URL**: https://www.grepow.com/lifepo4-battery.html (LFP product family)
- **Notes**: Well-established Shenzhen battery manufacturer. Multiple LFP pouch lines including high-discharge variants (20C, 25C, 40C — overkill for our use). Sample-friendly, MOQ typically ~100 for stock sizes, ~500 for custom. Quote turnaround usually a few days via their sales contact form.
- **When to use**: if `lithium-lifepo4-battery.com` is unreachable or LFP143060 dims don't suit final enclosure.
- **Encyclopedia article on LFP pouches** (useful background): https://www.grepow.com/lfp-battery-encyclopedia/what-is-soft-pack-lithium-iron-phosphate-lifepo4-battery.html

## Backup #2 — Misen Power

- **URL**: https://www.misenpower.com/LiFePO4-Pouch-Cell-pl49090897.html
- **Notes**: Explicit "LiFePO4 Pouch Cell" product page. Less detail than Grepow but a third independent source confirming this market segment exists.

## Why pouch was harder to find than expected

LFP is a safer chemistry but lower energy density than NMC/LCO (~330 vs ~600 Wh/L). Most LFP capacity is sold as cylindrical (18650 LFP, 26650 LFP, 32650 LFP) because the rigid case suits the chemistry well. Pouch LFP exists but is a niche — used where slim form factor matters more than peak power density. Mainstream LFP makers (CATL, BYD, EVE) focus on prismatic/cylindrical; pouch is left to specialist makers and customs.

For Device's wall-mount form factor, pouch is correct (14 mm thick vs. 26 mm for 26650 = ~12 mm thinner Device).

## Linked

- [Brief](Brief.md) — the project this sourcing serves
- [Sniffer Concept](Sniffer_Concept.md) — future product, mains-powered, will NOT need LFP pouch
