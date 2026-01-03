# Memory

## Speed Naming Conventions

DDR stands for Double Data Rate. The RAM transfers data on both the rising and falling edge of each clock cycle, so two transfers per clock.

- DDR5-6400: The 6400 is MT/s (megatransfers per second), not the actual clock speed
- Actual clock: MT/s divided by 2 (so DDR5-6400 = 3200 MHz actual clock)
- PC5-51200: Alternative naming convention showing theoretical bandwidth in MB/s (6400 × 8 bytes = 51,200 MB/s, or 51.2 GB/s)
- The memory bus is 64 bits wide (8 bytes), so bandwidth = MT/s × 8s

This convention has been the same since DDR replaced SDR (Single Data Rate) in the early 2000s.

CPUs can process way more than 51.2 GB/s, so RAM is often the bottleneck in tasks that require the cpu to fetch data from memory constnatly.

## Decoding RAM Specs

Example: `Corsair Vengeance 64GB (2 x 32GB) DDR5-6400 PC5-51200 CL32`

| Spec | Meaning |
| ------------------- | ---------------------------------------------------------------------------------------------------------- |
| 64GB (2 x 32GB) | Total capacity and configuration. Two sticks enables dual-channel mode, doubling bandwidth vs single stick |
| DDR5-6400 | Generation and speed (6400 MT/s) |
| PC5-51200 | Same speed expressed as peak bandwidth (51,200 MB/s) |
| CL32 | CAS Latency - 32 clock cycles delay between requesting and receiving data |
| Timings 32-40-40-84 | CL-tRCD-tRP-tRAS (CAS Latency, Row-to-Column Delay, Row Precharge, Row Active Time) |
| 1.40V | Operating voltage (DDR5 stock is 1.1V, so this is overclocked/XMP) |

## Calculating Real-World Latency

Formula: `(CAS Latency ÷ actual clock) × 1000 = nanoseconds`

Examples:

- DDR4-3200 CL16: (16 ÷ 1600) × 1000 = 10ns
- DDR5-6000 CL30: (30 ÷ 3000) × 1000 = 10ns
- DDR5-6400 CL32: (32 ÷ 3200) × 1000 = 10ns
- DDR5-7200 CL36: (36 ÷ 3600) × 1000 = 10ns

Key insight: DDR5 has nearly double the bandwidth of DDR4, but well-binned kits have similar latency.

## DDR5 vs DDR4 at Same Speed

DDR5-3200 vs DDR4-3200: DDR4 wins.

- DDR5-3200 runs ~CL40: (40 ÷ 1600) × 1000 = 25ns
- DDR4-3200 runs ~CL16: (16 ÷ 1600) × 1000 = 10ns

At equal frequencies, DDR4 has much better latency. DDR5 needs higher speeds (5600+) to justify itself.

## Architectural Differences: DDR5 vs DDR4

| Feature | DDR4 | DDR5 |
| -------------------- | --------------------------------- | -------------------------------------------------- |
| Channel architecture | Single 64-bit channel per stick | Dual 32-bit channels per stick (better efficiency) |
| On-die ECC | No (only server-grade) | Yes (helps stability at high speeds) |
| Power management | Voltage regulation on motherboard | PMIC on the RAM stick itself |
| Base voltage | 1.2V | 1.1V (better efficiency) |
| Max density | ~32GB per stick consumer | 64GB+ per stick, roadmap to 128GB |
| Speed range | 2133-4000 MT/s practical | 4800-8000+ MT/s |
| Physical | 288 pins, notch position A | 288 pins, notch position B (not compatible) |

## Bandwidth vs Latency

Bandwidth: How much data you can move per second

- DDR4-3200 dual channel: ~51 GB/s
- DDR5-6000 dual channel: ~96 GB/s

Latency: How long it takes to get data once requested

- Well-binned DDR4 and DDR5 are similar (~10ns)

When bandwidth matters:

- Streaming large sequential data
- Bulk transfers
- Video rendering, large compiles

When latency matters:

- Small random accesses
- General snappiness and responsiveness
- Most desktop workloads

## The Memory Hierarchy

```
Storage (SSD/HDD)     Persistent, slowest
        ↓
      RAM             Active programs/data, managed by OS
        ↓
  CPU L3 Cache        Largest CPU cache, shared between cores
        ↓
  CPU L2 Cache        Per-core, smaller
        ↓
  CPU L1 Cache        Per-core, smallest, fastest
        ↓
   Registers          Tiny, where actual computation happens
```

- OS loads programs from storage into RAM
- CPU pulls data from RAM into cache hierarchy
- Cache hit = fast (data already in cache)
- Cache miss = slow (must fetch from RAM)

Key insight: If your working set fits in cache, RAM speed barely matters. RAM speed only matters when you're frequently missing cache and hitting main memory.

## When Fast RAM Actually Helps

Benefits significantly:

- Video encoding/rendering (Premiere, DaVinci, Blender)
- Large codebase compilation
- Running multiple VMs/containers
- Large dataset processing (pandas, data pipelines)
- Huge photo files (500MB+ PSDs, batch processing)
- Scientific computing, simulations
- APU/integrated graphics (heavily memory-bound)

Minimal benefit:

- General desktop use, browsing, Office
- Gaming at 1440p/4K (GPU-bound)
- Most programming (unless massive compiles)
- Audio production
- Typical Chrome + gaming workload

Most desktop tasks have working sets that fit in cache. The CPU isn't waiting on RAM.

## Platform Sweet Spots

AMD AM5: Infinity Fabric tops out at ~6000 MT/s in 1:1 mode. Going higher forces 2:1 ratio which adds latency. DDR5-6000 CL30 is often the sweet spot.

Intel: Scales more linearly with speed. Higher MT/s generally helps.

Always check motherboard QVL (qualified vendor list) for compatibility at rated speeds.

## Shopping Guidelines

1. Check your platform's sweet spot
1. Compare real-world latency using the formula
1. Given equal latency, prefer higher MT/s for more bandwidth
1. Don't overpay for marginal gains (single-digit percentages)
1. Capacity often matters more than speed for typical use

## RAM Thermals

| Type | Typical Temps |
| ------------------------ | ------------- |
| DDR4 stock | 35-45°C |
| DDR5 stock (1.1V) | 40-50°C |
| DDR5 overclocked (1.4V+) | 50-65°C |

DDR5 runs warmer because the PMIC is on the stick and higher clocks draw more power. Some DDR5 can throttle above 70°C.

Heatspreaders: cosmetic for DDR4, actually useful for high-speed DDR5. Still not a concern with any reasonable case airflow.

## Why DDR5 Hype Exceeds Reality

Legitimate reasons for DDR5:

- New platforms (Intel 12th+, AMD AM5) require or prefer it
- Scales well at 6000+ with tight timings
- Future-proofing (DDR4 is end-of-life)

Marketing/hype reasons:

- Bigger numbers sound better
- Tech media focuses on new tech
- Enthusiast echo chamber
- FOMO about "last gen"

Reality: CPU and GPU matter far more for most users. The difference between good DDR4 and good DDR5 is often single-digit percentages in workloads that benefit, and near-zero in typical use.

A solid PC built thoughtfully has 5-7+ year longevity. The yearly spec bumps and upgrade treadmill are mostly marketing. Build for current needs with some headroom, and ignore the noise.
