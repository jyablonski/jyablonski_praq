# Motherboard Architecture

A motherboard is the central component in a computer that ties together the CPU, memory, storage, peripherals, and expansion devices. Understanding how data moves through this system requires understanding a few key concepts: controllers, interfaces, and the division of labor between the CPU and chipset.

## Controllers

Controllers are specialized hardware blocks that manage specific protocols or interfaces. They handle the electrical signaling, timing, packet formatting, device enumeration, and protocol-specific logic so that other components don't have to.

Both the CPU and chipset contain multiple controllers:

CPU-integrated controllers:

- Memory controller (DDR4/DDR5) — handles RAM communication
- PCIe root complex — manages primary PCIe lanes for GPU and fast NVMe storage
- DMI controller — communicates with the chipset

Chipset-integrated controllers:

- USB controller — manages all USB ports and devices
- SATA controller — handles SATA drives
- Secondary PCIe controller — provides additional PCIe lanes for expansion slots
- Audio controller (if onboard audio is present)
- Ethernet controller (on some boards)

Controllers abstract away protocol complexity. The CPU cores don't deal with USB handshaking or DDR4 timing, they just read and write memory addresses. The controllers handle the rest.

## The Chipset

The chipset is a physical chip on the motherboard (separate from the CPU) that acts as an I/O hub for lower-bandwidth and secondary interfaces. It aggregates traffic from various controllers and communicates with the CPU over a dedicated link called DMI.

On Intel systems, chipsets are named by platform (Z490, B560, H670, Z790, etc.). The letter indicates feature tier:

- Z-series: Full overclocking support, maximum I/O
- B-series: Mid-range, some limitations
- H-series: Budget, fewest features

The chipset determines what I/O the motherboard can offer (number of USB ports, SATA ports, PCIe lanes from chipset), while the CPU determines compute capability and direct high-speed I/O.

### PCIe Lanes from CPU vs. Chipset

The CPU provides a limited number of high-speed PCIe lanes (typically 16 for graphics + 4 for NVMe on mainstream desktop CPUs). These lanes connect directly to the CPU for maximum performance.

The chipset provides additional PCIe lanes (often 20-24) for expansion slots and devices, but these lanes route through the chipset and share bandwidth over the DMI link to the CPU. This can create a bottleneck if many devices are active simultaneously. The difference is routing.

- CPU PCIe lanes go straight from CPU to device: maximum bandwidth, lowest latency.
- Chipset PCIe lanes go from chipset to device, then all share that DMI link back to the CPU. So a device on chipset PCIe lanes is ultimately bottlenecked by DMI bandwidth if things get saturated.

For a secondary NVMe in a chipset-connected M.2 slot, this usually doesn't matter, a single PCIe 3.0 x4 NVMe (around 3.5 GB/s) fits comfortably within DMI 3.0's ~4 GB/s. But if you had multiple high-bandwidth devices all hammering chipset lanes simultaneously, they'd compete for that shared DMI pipe.

- This is why you need to read the motherboard manual to know which M.2 slots connect to CPU vs. chipset.
- Some M2 slots also share bandwidth with SATA ports or PCIe slots, so using one can disable the other.
- Using specific M2 slots can also downgrade the GPU PCIe link from x16 to x8 if they share lanes.

Ideally:

- GPU gets all 16 CPU PCIe lanes
- Primary NVMe gets 4 CPU PCIe lanes
- Everything else uses chipset lanes without impacting CPU lane allocation

### Chipset Location

The chipset sits on the motherboard, typically in the lower-right area below the CPU socket. It's usually covered by a heatsink with manufacturer branding. On an ASUS ROG board, for example, it's under the heatsink with the ROG logo near the lower PCIe slots.

## DMI (Direct Media Interface)

DMI is Intel's dedicated link between the CPU and chipset. It functions like a PCIe connection but is reserved specifically for CPU-to-chipset communication.

On 10th/11th gen Intel platforms, DMI 3.0 provides roughly 4 GB/s of bandwidth (equivalent to PCIe 3.0 x4). All chipset-connected devices share this bandwidth.

Traffic that flows over DMI:

- USB devices
- SATA drives
- Chipset-connected M.2 slots
- Chipset-provided PCIe slots
- Onboard audio
- Onboard ethernet (on most boards)

## How the CPU Receives Data

The CPU has three primary pathways for receiving data:

### 1. Direct PCIe Lanes

High-bandwidth devices connect directly to PCIe lanes from the CPU. This includes:

- The primary GPU (typically x16 lanes)
- The primary M.2 NVMe slot (typically x4 lanes)

These connections bypass the chipset entirely for maximum bandwidth and minimum latency.

### 2. Memory Bus

System RAM connects directly to the CPU's integrated memory controller via a dedicated parallel bus. Modern desktop CPUs support dual-channel or quad-channel memory configurations. This is the lowest-latency path for data the CPU needs to process.

### 3. Chipset via DMI

Everything else funnels through the chipset. USB peripherals, secondary storage, expansion cards in chipset-connected slots—all share the DMI link to reach the CPU.

## Example: USB Data Flow

When you press a key on a USB keyboard:

1. The keyboard sends USB packets over the cable
1. The packets arrive at a USB port on the motherboard
1. The chipset's USB controller receives and processes the packets
1. The controller translates this into data for the system
1. The data travels over the DMI link to the CPU
1. The CPU's DMI interface receives the data
1. The OS input stack processes the keystroke

The CPU never sees raw USB protocol—the chipset's USB controller handles all of that.

## VRMs (Voltage Regulator Modules)

VRMs are the power delivery components surrounding the CPU socket. They convert 12V power from the PSU into the precise, stable voltage the CPU requires (often around 1.2-1.4V under load).

VRMs consist of:

- MOSFETs — switch power on and off rapidly
- Chokes — smooth the switched output
- Capacitors — filter and stabilize voltage

Better VRMs (more phases, higher-quality components) allow more stable power delivery under heavy load and better overclocking headroom. VRMs are typically covered by heatsinks on higher-end motherboards.

## M.2 Slots and Routing

Most motherboards have multiple M.2 slots, but they're not all equal:

- CPU-connected M.2: Lanes go directly to the CPU's PCIe controller. Full bandwidth, no DMI bottleneck.
- Chipset-connected M.2: Lanes route through the chipset and share DMI bandwidth with other devices.

The motherboard manual specifies which slots connect where. For best NVMe performance, use the CPU-connected slot for your primary drive.

## Historical Context: Northbridge and Southbridge

Older systems (pre-2010ish) had two chips on the motherboard:

- Northbridge: Handled high-speed communication—memory controller, PCIe for graphics. Connected directly to the CPU.
- Southbridge: Handled slower I/O—USB, SATA, audio, legacy ports. Connected to the northbridge.

Modern CPUs absorbed the northbridge functions (memory controller, primary PCIe). What remains as "the chipset" is essentially the evolved southbridge—hence why it handles the slower, secondary I/O.

## Adding New Interfaces

CPUs evolve by integrating new controllers as interfaces become important enough. This has happened with:

- Memory controllers (moved from northbridge to CPU)
- PCIe root complex (moved on-die)
- USB4/Thunderbolt (appearing integrated on newer platforms)
- CXL (Compute Express Link, emerging for memory expansion)

The tradeoff is die space and pin count—every integrated controller takes silicon area and physical pins. High-bandwidth, latency-sensitive interfaces justify the cost. Lower-bandwidth interfaces stay on the chipset.

In theory, any new interface could be added to a CPU—you just need a controller that speaks the protocol and pins to connect it. Custom silicon designs (Apple M-series, AI accelerators) do exactly this for their specific requirements.

## Summary

| Component | Role |
| ----------- | ------------------------------------------------------------- |
| CPU | Compute cores, memory controller, primary PCIe, DMI interface |
| Chipset | I/O hub with USB, SATA, secondary PCIe, other controllers |
| DMI | Dedicated link between CPU and chipset |
| Controllers | Protocol-specific hardware blocks on both CPU and chipset |
| VRMs | Power delivery from 12V to CPU-appropriate voltage |

Data enters the system through various interfaces, gets processed by the appropriate controller, and ultimately lands in system memory where CPU cores can operate on it. Once data is in memory, its origin doesn't matter, the CPU just sees addresses and executes instructions.
