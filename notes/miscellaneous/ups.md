# UPS Notes

## What a UPS Is For

A UPS (uninterruptible power supply) is a battery + circuitry that sits between wall power and your devices. It detects power loss and switches to battery, giving you continuity through outages.

Two distinct product categories share the name:

- Traditional UPS: Short ride-through (minutes), instant cutover, designed for graceful shutdown or bridging brief outages. Always plugged in. Sized in VA/watts with small batteries (30-300 Wh typical).
- Portable Power Station: Long runtime (hours), often slower transfer, designed for emergency backup or off-grid use. Large batteries (500-3000+ Wh). Not all have true UPS mode.

## Topologies (Traditional UPS)

- Standby (offline): Cheapest. Devices run off wall power until outage, then relay flips to inverter. 4-10ms transfer time. Fine for desktops, networking gear.
- Line-interactive: Adds voltage regulation (boost/buck) for brownouts without using battery. Sweet spot for homelabs, small servers.
- Double-conversion (online): Devices always run off inverter. Zero transfer time, full power conditioning. Expensive, less efficient. For sensitive equipment.

## Battery Types

| Type | Lifespan | Cycle Life | Weight | Cost | Notes |
| -------------------------------- | --------- | ----------------- | ------ | ------------ | --------------------------------------------------------------------------- |
| AGM (sealed lead acid) | 3-5 years | 200-400 cycles | Heavy | Cheap | Most consumer UPSes. Heat-sensitive. |
| Gel (sealed lead acid) | 4-6 years | 300-500 cycles | Heavy | Cheap-mid | Better deep discharge tolerance than AGM. |
| LiFePO4 (lithium iron phosphate) | ~10 years | 2000-5000+ cycles | Light | 2-3x upfront | Thermally stable, holds voltage well, increasingly standard in newer units. |

Lead-acid suffers from the Peukert effect (capacity drops sharply at high discharge rates) and halves its lifespan for every 10C above 25C. LiFePO4 is much less affected by both.

## Runtime Expectations

Runtime depends on load vs battery capacity, and is nonlinear at the extremes.

| UPS Type | Battery (Wh) | Runtime at 100W load |
| ---------------------------- | ------------- | -------------------- |
| Consumer standby (500VA) | ~30 Wh | 10-15 minutes |
| Line-interactive (1500VA) | ~85 Wh | 30-45 minutes |
| Rack UPS w/ extended battery | 200-1000 Wh | 1-8 hours |
| Portable power station | 1000-3000+ Wh | 8-30+ hours |

Vendor runtime curves are more reliable than back-of-envelope math, especially for lead-acid.

## Price Ranges (USD, 2026)

| Category | Price | Examples |
| --------------------------------------- | ----------- | ---------------------------------- |
| Entry consumer (500-900VA, AGM) | $80-150 | CyberPower CP series, APC Back-UPS |
| Mid line-interactive (1000-1500VA, AGM) | $150-300 | APC SMT, CyberPower PR |
| Higher-end line-interactive (LiFePO4) | $400-900 | Eaton 5P Gen2 LFP, newer APC SMT-L |
| Rack double-conversion (1-3kVA) | $700-2500 | Eaton 9PX, APC Smart-UPS SRT |
| Portable power station (1kWh, LFP) | $500-900 | EcoFlow Delta 2, Bluetti AC180 |
| Large portable / hybrid (3-6kWh) | $2000-5000+ | EcoFlow Delta Pro 3, Bluetti AC500 |

## When to Reach for One

Good reasons:

- Equipment that corrupts data on hard power-off (databases, NAS, anything with active filesystem writes)
- Frequent brownouts or dirty power (line-interactive specifically handles voltage regulation)
- Medical equipment (CPAP, oxygen concentrators)
- Workstation where losing in-progress work hurts
- Long outages common in your area + you want to keep fridge/comms running (portable power station territory)

Reasons to hold off:

- Stable grid, rare outages, and nothing critical that can't recover from a hard reboot
- Devices that handle power loss gracefully on their own (modern journaled filesystems, Postgres, properly configured SQLite)
- Cost of UPS + battery replacements over time exceeds the cost of the rare recovery effort
- You have good backups and can tolerate the occasional rebuild

## Practical Notes

- Pure sine wave vs simulated sine wave matters for motors, audio gear, and some active PFC power supplies. Simulated sine is fine for most modern switching PSUs but can cause shutdowns on higher-end ones.
- VA rating is not watts. Real watts is typically 60-70% of VA. A "1500VA" unit often delivers ~900W.
- Battery replacement is part of TCO. AGM batteries die on a calendar, not just on usage. A $200 UPS with $80 battery replacements every 4 years adds up.
- The shutdown automation (NUT, vendor daemon) is what actually saves your data. The battery just buys the time window.
