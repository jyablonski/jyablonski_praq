# Hardware

CPU and GPU Clock speed can be overclocked for more performance, but this leads to more power consumption and more heat. Better cooling will is needed.

TDP (Thermal Design Power) - Term used to specify average power in Watts that the hardware component will likely use.

PCIe (Peripheral Component Interconnect Express) - Interface on the Motherboard that allows you to connect GPUs & SSDs.

- The version (PCIe 4 vs PCIe 5) keeps going up; basically it just keeps increasing the transfer rate in GT/s (gigatransfers / second) so more performance.
- Format specifications are maintained and developed by the PCI-SIG Group.

## Motherboard

CPU Socket Type - what CPU Chipsets are compatible with the Motherboard (if you buy a LGA 1700 CPU then you need a Motherboard that supports that).

PCIe (Peripheral Component Interconnect Express) - Interface on the Motherboard that allows you to connect GPUs & SSDs.

- The version (PCIe 4 vs PCIe 5) keeps going up; basically it just keeps increasing the transfer rate in GT/s (gigatransfers / second) so more performance.
- Format specifications are maintained and developed by the PCI-SIG Group.
- Motherboard typically has 20 lanes:
- 16 for the 1st PCIe Slot (for the GPU).
- 4 for the first NVME Slot (M.2).
- The other lanes have to go through a middleman to reach the CPU which means latency.

M2 Slots plug SSDs directly into the motherboard, rather than needing a cable.

- M2 can either use a SATA interface or the faster PCIe interface w/ an NVME drive.
- They fold down into the motherboard & are protected by covers, instead of sticking out like GPUs.

Memory Channel (DDR4 or DDR5)

BIOS Flashback - Optional feature used to reset BIOS to factory settings incase something fks up.

Size

- ATX - Standard, most popular.
- mATX - ~25% smaller, typically cutting back on a few features to save space and $$$.
- Mini ITX - Smallest and most expensive. Limited amount of features and space.
- e ATX - Biggest one typically for servers.

BIOS (Basic Input/Output System) - Everybody Motherboard Manufacturer offers their own BIOS (Asus ROG, Gigabyte Aorus etc).

## CPU

CPUs often are labeled with a chipset (ex. LGA 1700). This means that the 1700 pins are on the Motherboard rather than the processor.

CPUs are very small for a number of reasons

- Speed. If the CPU was larger there'd be more distance to cover to process the same operations.
- Cooling. We're basically limited by how much power we can throw at these components because we can only move so much hot air out of a PC in a short amount of time.
- Consumer demand. Are people really interested in buying $1500 CPUs ? Most applications are single threaded; 99% of people using PCs have more than enough processing power from their CPU. This isn't the bottleneck of performance for most people.

Clock Speed - measured in Gigahertz (GHz). Clock speed of 2.1 GHz means 2.1 billion cycles per second.

Cores - Individual processing component physically on the CPU.

Threads - Software term used to describe how we execute work on the physical CPU Cores.

Cache - Used by the CPU to reduce average time & energy needed to access data from memory. It's a smaller & faster memory located very close to the processor cores.

- L1, L2, L3, and even L4 Level caches with varying levels of performance.
  - Fetching instructions from a cache is generally faster than fetching from RAM
  - Every CPU Core has its own L1 Cache which is the fastest but also the smallest. Holds most frequently accessed data and instructions
  - Every CPU Core has its own L2 Cache which is slower but has a larger capacity. Holds data + instructions that are accessed less frequently.
  - The L3 Cache is shared amongst all CPU Cores.
  - The L4 Cache is a generic term for the highlest level of cache in a system, which can be the L3 Cache or its own L4 Cache. Depends on CPU Model

## GPU

GPUs are Graphical Processing Units that are like their own individual computer. They have a CPU, RAM, and tons of cores to process mathematical operations.

Bus - How the GPU connects to the Motherboard. Uses the PCIe Lane.

Ensure your GPU is running at the maximum supported PCIe speed (e.g., PCIe 4.0 x16 or PCIe 3.0 x16). You can check this in your GPU monitoring software or through your motherboard BIOS.

- If the GPU is running at x8 or lower speeds, it may be due to lane-sharing with the M.2 SSD.
- `PCIe v4.0 x16 (16.0 GT/s) @ x8 (16.0 GT/s)` actaully means it's running at 8 lanes instead of 16

GPU Clock - Core Clock speed. The speed at which the GPU's processor operates.

- A GPU with a core clock speed of 1.5 GHz can execute 1.5 billion instructions per second.

Memory Clock - usually measured in megahertz (MHz) or gigahertz (GHz).

- For example, a GPU with a memory clock speed of 8 GHz can access its memory 8 billion times per second.

Memory Type - GDDR6 vs GDDR5. These are 2 different VRAMs

- GDDR5 transfers data at a rate of 8 GB/s
- GDDR5X transfers data at a rate of 10-14 GB/s
- GDDR6 transfers data at a rate of 14-16 GB/s

NVIDIA CUDA Cores (Compute Unified Device Architecture) - Similar concept to CPU Core except they're used for much simpler operations, hence why there's 1000s of them instead of just ~20 like on a CPU.

- Very well suited for parallel workloads ,,, like displaying graphics on a 1920 x 1080 screen where 100s of pixels are changing color 60+ times per second.

AMD Stream Processors - AMD's equivalent of CUDA Cores.

## Memory

All data is loaded into memory before being sent off to the CPU. Similar to SSD Storage except it's very very fast, but not as much of it around to use (~32 GB instead of 2 TB in an HDD etc). Most motherboards offer 2 lanes for RAM to communicate with the CPU.

Memory normally comes in the form of 2 sticks which should go in the 2nd and 4th slots away from the CPU. The Memory Manual normally will say this. [Fancy Post](https://www.reddit.com/r/buildapc/comments/zfx0lg/i_understand_slot_2_4_is_ideal_for_dual_channel/#:~:text=You%20put%20the%20sticks%20in,the%20stability%20is%20the%20same.) on why the 1st and 3rd slots aren't used for dual channel sticks.

DIMM (Dual In-Line Memory Module) - Typically the kind we use in Desktops

SO-DIMM (Small Outline DIMM) - Typically used in Laptops. Much smaller.

DDR (Double Data Rate) - 2 transfers happen per clock cycle.

Motherboards can sometimes support both DDR4 + DDR5, or they might only support 1. Different RAMs have different notches to connect into the Motherboard.

DDR4

DDR5 - Newest, better performance but more expensive.

Single Channel - Only 1 RAM Slot is being used.

Dual Channel - The Memory controller uses both channels to communicate with the CPU, essentially doubling bandwith + performance.

## Storage

SATA - Interface used to connect HDDs + SSDs to the Motherboard via physical cables.

NVME - Non Volatile Memory Express. Utilizes PCIe lanes. More reliable and better power efficiency. Best performance up to 3500 mb/s.

SSD - Solid State Drive, no physical moving plates but still on SATA. Up to 500 mb/s.

HDD - Hard Disk Drive, physical moving plates. Very Slow. Up to 150 mb/s.

## PSU

Wattage (1000 W) -

Efficiency Rating - PSUs "performance" depends on how efficient they are at different workloads. You also typically want a lot more juice than is needed for your system so your PSU only has to operate at ~60% max power instead of going 100% at all times.

- 80 PLUS Gold PSUs are 87% efficient at 20% load, 90% efficient at 50% load, and 87% efficient at 100% load for 115V powered systems.
- 80 PLUS is a branding that refers to PSUs that are 80% efficient or better at converting input into output.
- As you move up from 80 PLUS to 80 PLUS Bronze to 80 PLUS Platinum the efficiency gets slightly better.
- You can still have a shit made PSU that will break in 3 months even if it's 80 PLUS branded.

## AIO

All In One Liquid Cooler.

Premade, closed loop liquid cooling system pack which comes with a Cooler that attaches to the CPU, a pump, and a Radiator.

- The liquid doesn't need to be changed (hence closed loop).
- Once connected it takes heat away from the attached component (CPU or GPU) to the Radiator via the liquid loop where it's cooled, and then the cool liquid returns to the CPU to repeat the loop via a pump.
- Typical Watercooling solutions you have to buy your own parts separately, add in your own tubing, your own liquid, and create your own loop. AIO products do this all for you.
- [Air Bubbles](https://www.youtube.com/watch?v=DKwA7ygTJn0)
  - Basically the Pump of the AIO which is attached to the CPU should be _LOWER_ than the highest point of the radiator. Otherwise, you can get air trapped in the AIO which will reduce efficiency over time.

Intake Radiators should be placed at the front or bottom of the case. Fresh air from outside of the case will get brought in via the intake fans where that fresh air can cool down the radiator.

- This is the _best_ solution for cooling the component attached to the radiator (CPU / GPU).
- This will increase overall case temps, because that slightly cooled but still warm radiator air is getting blown through the case (although it's not that bad).

Exhaust Radiators should be placed at the rear or the top of the case. These radiators will get cooled through slightly warmer air from inside of the case, but the warm radiator air will get blown outside of the case.

- This is not as good of a solution for cooling the component attached to the radiator (CPU / GPU).
- This will decrease overall case temps, because that warm radiator air is being blown completely out of the case.

CPUs can generally run a couple Celsius higher without it affecting that much. CPU only really gets affected at the top end where it's hitting its temperature limits and starts getting severely throttled.

GPU generally gets affected the entire time by temperature increases which could lead to incremental drops in FPS until the GPU becomes completed overheated.

Some AIOs will come with Washers for the Fans. In general, a washer is used when the material you're fastening is softer than the material you're fastening with... Eg a metal bolt on the wooden leg of a table, and its purpose is to spread the pressure of the bolt across a broader area, so you can tighten more without the bolt just sinking into the soft wood.

### Bad

![image](https://github.com/jyablonski/python_aws/assets/16946556/e8b6dfae-1e97-4e35-b184-b1915cca6bdc)

![image](https://github.com/jyablonski/python_aws/assets/16946556/acc4ca33-c9e2-4040-ba22-5eb0097be757)

### Good

![image](https://github.com/jyablonski/python_aws/assets/16946556/ef648c69-a264-4d17-8f17-bc573eb6c1ef)

![image](https://github.com/jyablonski/python_aws/assets/16946556/28673c3f-360a-4ebc-adf1-e24282db1125)

## Fans

Intake Fan - brings (room temp) air from outside the case into the case.

Exhaust Fan - transfers air from inside the case to outside of the case.

Typically intake fans are on the front or bottom part of the case, and exhaust is on the top or rear part of the case.

Mesh filters helps make sure smaller particles / excessive dust doesn't get brought in while the fans are running.

### Positive Pressure

- More air within the case than outside
- More intake fans than exhaust fans
- Less dust will get into the case and fk your shit up

### Negative Pressure

- Less air within the case than outside
- More exhaust fans than intake fans
- More dust will get into the case

## Install Media

1. Install OS boot media

- https://archlinux.org/download/

2. Flash the boot media onto a USB Drive

- This requires first wiping the USB Drive
- This ISO File that we download isnt bootable by the Motherboard out of the box
- Then use Rufus or belena-etcher to flash the boot media onto the USB Drive; you can't just drag and drop the raw iso image into the USB Drive and expect it to work
- This turns the .iso image on the USB Drive into a bootable device, and it places the files in a layout that the system can understand and use during insetallation

3. Plug USB Drive into new PC and get into the BIOS menu by spamming delete or f12 keys.

You can verify the .iso image you installed by verifying the integrity of the checksums provided by the boot media owner (Archlinux in this case)

- This process involves installing the `b2sums.txt` file which has a checksum for each iso image you can download
- You then compare that checksum value in the txt file with your downloaded ISO. If they match, it prints "OK" meaning the file is valid and hasn't been tampered with by wherever you downloaded it from
- If a file gets corrupted during download (due to a network issue, partial download, or disk error), the checksum won’t match.
- It also protects against malicious tampering—if someone modified the ISO, the checksum would be different.

## BIOS Flashback

BIOS Flashback is a feature on some motherboards that allows you to update the BIOS without having anything connected except the 24 pin ATX to the Motherboard.

- Motherboards w/ BIOS Flashback typically have a button on the rear I/O Panel, along with a dedicated USB Port that says "BIOS"

The process works by:

1. Grab a 4+ GB USB Stick and plug it into a 2nd PC on Windows

- I tried doing this on Linux, but ran into issues around running the `.exe` file later on and it borked the Motherboard. Don't do this on Linux.

2. Ensure the USB Stick is formatted as FAT32 so the Motherboard can understand it
3. Go to your Motherboard's Page and download the latest BIOS Update
4. Extract the BIOS Update Folder you just downloaded

- This will download 2 files: an `.exe` file and a `.CAP` file w/ the actual BIOS Update

5. Run the `.exe` File inside, which will rename the CAP File to something the Motherboard can understand
6. Place the renamed CAP file into the USB Folder
7. Take the USB Stick and plug it into the dedicated USB Port for BIOS Flashback
8. Plug in Power and flip the switch on the PSU, but do NOT power the PC on
9. With Power and USB Stick plugged in, Press and hold the BIOS Flashback button for 10 seconds until lights start flashing on the button
10. The Motherboard will begin updating and lights will continue flashing until the update is complete
11. After the lights stop flashing, waiting 3 minutes and then unplug the USB and power the PC on and finish the update process.

## CPU Undervolting

CPU Undervolting involves going into BIOS/UEFI and intentionally lowering the voltage being sent to the CPU. This leads to the CPU consuming less power, which means lower electricity used and less heat generated. Ultimately, this can lower CPU thermals and improve performance

- You're essentially running the CPU in a more efficient state which can result in better stability

By the nature of how they're created, all CPUs have minor imperfections that make them slightly different from each other, even ones that are the same model (i9 10900k).

- For this reason, CPU manufacturers deliberately set voltage thresholds that will work on all CPUs out of the box, otherwise they'd have to deal with tons of returns and RMAs
- If they shipped CPUs undervolted, some wouldn't boot, or would crash, or behave unpredictably

When undervolting, you're looking for a setting in the BIOS/UEFI called `Core Voltage Offset`. You want to set this to a negative value to actually "undervolt" the CPU.

- Undervolt in small steps (e.g., -20mV at a time)
- Run stress tests afterwards and monitor temps and performance
- If stable, decrease voltage by another -10 or -20 mV again
- If unstable, then increase voltage another 10 or 20 mV and check stability again

If you try undervolting and your chip cant handle it, nothing permanent or dangerous happens.

- Worst case, you'll have random system crashes or freezes etc
- Blue screens of death

If your system won't boot after attempting this, you have to reset your motherboard to factory settings by clearing CMOS

- The CPU itself doesn't store the CPU voltage settings, it just reads them from the motherboard
- Worst case if you brick your PC this way, resetting the motherboard should fix it up

Overvolting is possible in theory, but unneccessary. Don't do this.
