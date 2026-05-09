# How CPUs Are Made

1. Mine quartz sand (silicon dioxide, SiO₂)

   - Because silicon is the element we want, but it's never found in pure form on Earth — it's too reactive and bonds aggressively with oxygen. Quartz sand is essentially the most abundant, accessible, and chemically convenient source of silicon on the planet. We specifically want high-purity quartz from particular deposits (Spruce Pine, North Carolina supplies a disproportionate amount of the world's ultra-pure quartz used in semiconductor crucibles).

1. Purify silicon to electronic grade (~99.9999999% pure, "9N")

   - Because the impurity tolerance for semiconductors is insane — at parts-per-billion levels, contaminants can dominate electrical behavior. First, quartz is reduced to metallurgical-grade silicon (~98% pure) by reacting it with carbon in an electric arc furnace at ~2,000°C: SiO₂ + 2C → Si + 2CO. The carbon grabs the oxygen, leaving elemental silicon. That's nowhere near clean enough, so the Siemens process converts it to trichlorosilane (SiHCl₃), a liquid that can be fractionally distilled to extreme purity (different boiling points let you separate impurities), then reduced back to solid silicon with hydrogen gas onto heated rods. The result is "polysilicon" — pure, but polycrystalline (random crystal orientations).

1. Grow a single-crystal silicon ingot via the Czochralski process

   - Because polysilicon's random crystal structure scatters electrons unpredictably and wrecks transistor performance. We need a single continuous crystal lattice with all atoms in perfect alignment. The Czochralski process melts the polysilicon in a fused silica crucible (~1,420°C), dips a small "seed crystal" into the melt, and slowly pulls it upward while rotating. Atoms attach to the seed in the same orientation, growing a cylindrical single crystal up to 300mm diameter and 1-2 meters long. Tiny precise impurity additions during this step ("doping") set the base electrical character — boron makes it p-type, phosphorus makes it n-type. Note: leading-edge logic wafers often add a thin epitaxial silicon layer on top of the CZ wafer, or use the float-zone method for ultra-low-defect substrates.

1. Slice the ingot into thin wafers

   - Because chips are essentially 2D structures with thin layers built up on a flat surface — you don't need a 2-meter cylinder of silicon, you need a flat substrate to build on. Diamond wire saws slice the ingot into wafers about 775 micrometers thick (less than a millimeter). The wafer becomes the "canvas" for everything that follows.

1. Polish the wafers to atomic flatness

   - Because semiconductor features are now smaller than 5 nanometers, and any surface roughness larger than the features themselves would make precise patterning impossible. Wafers go through chemical-mechanical polishing (CMP) until the surface is flat to within a few atoms. The mirror finish you see on a silicon wafer is necessary for everything downstream.

______________________________________________________________________

The patterning loop (steps 6-12, repeated per layer):

A modern chip is built up layer by layer, each layer requiring its own pattern. The next several steps describe one cycle of that loop.

______________________________________________________________________

6. Grow or deposit an insulating layer

   - Because the chip needs electrical "walls" between the parts that carry current — without insulators, electricity would just flow everywhere and nothing would work. Silicon got lucky here: if you heat it in oxygen, the surface basically rusts into a glass-like coating (SiO₂) that happens to be a near-perfect insulator. That's a huge part of why the entire industry runs on silicon and not some other element. For the most critical spot in modern chips — the tiny gap that controls each transistor — that classic rust-coating got too thin to do its job (electrons started leaking through it), so today's cutting-edge chips use a fancier material called hafnium oxide, sprayed on one atomic layer at a time. Most other insulating layers in the chip still use the original silicon-rust trick.

1. Apply photoresist (light-sensitive coating)

   - Because we need a way to selectively pattern the wafer at nanometer resolution, and chemistry that responds to light is how we do that. Photoresist is a polymer that changes its solubility when exposed to specific wavelengths of light. Spin-coating gets it into a uniform film of precise thickness across the wafer.

1. Photolithography — project the circuit pattern onto the wafer

   - Because we need to define billions of features per chip, and we can't do that one at a time. A photomask containing the circuit pattern is illuminated, and the image is projected (always demagnified, typically 4×) onto the photoresist-coated wafer. Modern processes use extreme ultraviolet light (EUV) at 13.5nm wavelength because shorter wavelengths can resolve smaller features (diffraction limit). EUV is so hard to work with that there's only one company in the world (ASML) that makes the machines, each costs ~$200 million, and they require generating a plasma by hitting tin droplets with a laser 50,000 times per second.

1. Develop the photoresist

   - Because we need to actually remove the exposed (or unexposed) regions to leave behind a patterned mask. A chemical developer washes away the soluble portions, leaving photoresist only where we want to protect the underlying material from the next step.

1. Etch the exposed pattern

   - Because the photoresist mask defines *where* we want to modify the wafer, but we still have to actually do the modification. Plasma etching (reactive ion etching) bombards the wafer with chemically reactive ions that remove material in vertical lines wherever the photoresist isn't protecting it. This carves trenches, vias, and features into the silicon or oxide layers below.

1. Ion implantation (doping specific regions)

   - Because transistors are formed by precisely controlled regions of differently-doped silicon, and we need to introduce dopant atoms exactly where transistors will form. An ion implanter accelerates dopant ions (boron, phosphorus, arsenic) and fires them into the wafer with controlled energy and dose, embedding them at precise depths in the silicon lattice. The implanted regions become the source and drain of transistors. Not every layer involves implantation — this step is specific to forming transistor structures.

1. Strip the photoresist and clean

   - Because the polymer mask has done its job and now needs to be removed before the next layer can be built. The wafer goes through chemical cleaning to remove all organic residue without damaging the patterned features beneath.

1. Repeat the patterning loop dozens of times across all mask layers

   - Because a modern CPU has many distinct front-end-of-line layers (transistor formation: well implants, gates, source/drain, contacts) and back-end-of-line layers (10-15+ levels of metal interconnect routing), with each requiring its own pattern, etch, deposition, and cleaning cycle. A cutting-edge chip can require 80-100+ mask layers and 1,000+ individual process steps total, taking 3-4 months from raw wafer to finished product. Yield (the percentage of working chips per wafer) depends on every single one of those steps being executed nearly perfectly — a single contamination particle in the wrong place can kill a chip.

1. Deposit metal interconnects (with CMP between every layer)

   - Because transistors alone don't compute — they need to be wired together into circuits. Since IBM's 1997 introduction of copper, modern chips use the *damascene process*: etch trenches into the dielectric, fill them with copper via electroplating, then chemical-mechanical polish back to a flat surface. This is necessary because copper, unlike the aluminum it replaced, can't be cleanly plasma-etched — so you etch the dielectric instead and fill it. CMP after each metal layer is what keeps the stack flat enough to keep building on. Modern chips have 10-15 progressively coarser metal layers, with the bottom layers connecting individual transistors and the top layers carrying power and global signals across the chip.

1. Test individual dies on the wafer ("wafer probe")

   - Because no manufacturing process is perfect, and we need to know which chips work before spending money packaging the bad ones. Probes touch each die's test pads and run electrical tests. Failed dies get marked. Surviving dies often get binned by performance — the best ones become higher-clock-speed parts, slower ones become lower-end SKUs, partially-defective ones might have cores or cache disabled and become different products entirely.

1. Cut the wafer into individual dies

   - Because each working chip needs to become a discrete product. Diamond saws or laser cutters separate the wafer along the streets between dies. A 300mm wafer might yield anywhere from a few hundred large dies (high-end server CPUs) to tens of thousands of small dies (microcontrollers).

1. Package the die

   - Because the bare die is too fragile and has connection points too small to interface with a circuit board, and it needs mechanical protection, thermal management, and environmental sealing. The die is mounted to a multi-layer substrate (basically a tiny PCB) using either wire bonding or flip-chip technology with solder bumps — the substrate fans out the connections to the larger pin/ball pitch of the final package. A heat spreader (the metal cap you see on top of a CPU) gets attached for thermal conduction, and the package is sealed against moisture, contamination, and physical damage.

1. Package-level test and binning

   - Because some defects only manifest at full operating conditions — temperature, voltage, real workloads. Packaged chips are tested across their full operating envelope. Final binning determines the SKU: a die that hits 5.5GHz at acceptable voltage becomes an i9, the same die that only hits 4.8GHz becomes an i7, and so on. This is why "silicon lottery" exists — physically identical manufacturing produces a distribution of performance characteristics.

1. Ship to OEMs and integrators

   - Because a CPU on its own does nothing — it needs a motherboard, RAM, storage, power, cooling, and an operating system to be useful. The chip enters the broader supply chain and ends up in servers, laptops, your homelab Beelinks, etc.

1. Software stack on top

   - Because the silicon has no idea what a database query is. Inside the CPU, hardware decoders translate ISA instructions (x86, ARM) into internal micro-ops — on x86, complex instructions fall back to microcode ROM, while simple ones decode directly in hardware; ARM is largely microcode-free. Above that, an operating system schedules work onto the CPU, compilers translate high-level code into machine instructions, and libraries, frameworks, runtimes, and applications layer on top until eventually you're running dbt models on Snowflake, training models, or rendering frames in a game.

## Jacobs ELI5 mfer

1. get quartz sand, which is the most practical source of silicon on earth
1. refine quartz sand into 99.999999% purity so we get minimal imperfections in our final product
1. use the Czochralski process to grow the purified silicon into one giant single crystal, so all the atoms are perfectly aligned in a predictable way
1. cut that shape into tons of smaller wafers (or slices)
1. polish the slices to get the surface perfectly flat
1. grow an insulating layer to act as walls that block electricity from flowing where we don't want it
1. apply photoresist so we can use light to selectively pattern the wafer. this chemical process + light is how we can do that.
1. apply a photomask to project billions of tiny patterns onto the wafer, which will define where the transistors and wires go. 1 wafer will end up containing hundreds or thousands of cpus all made simultaneously
1. develop the photoresist - a chemical bath washes away the parts we want to remove, leaving photoresist only where we want to protect the layer underneath from the next step.
1. etch the wafer - chemicals or plasma remove material wherever the photoresist isn't protecting it, carving the gaps and holes we want.
1. fire specific atoms (boron, phosphorus, arsenic) into precise spots in the silicon to change how those spots conduct electricity — this is what turns plain silicon into the working electrical guts of each transistor.
1. chemically clean the wafer to remove any leftover photoresist or organic residue, and prepare the surface for the next layer of processing
1. repeat steps 6-12 dozens of times, building up layer upon layer
1. use the damascene process to carve trenches into each layer and fill them with copper, building up the 3D wiring that connects all the transistors. after this final metal layer, each die on the wafer is electrically complete
1. run tests on each die to see which ones work and which ones don't. mark the bad ones so we don't waste time packaging them. good dies are binned by performance, the best ones become high-end cpus, the slower ones become lower-end etc
1. cut the wafer into individual dies, each die is a single cpu.
1. turn the die into a finished product by mounting it on a substrate, adding a heat spreader, and sealing it in a protective package. essentially add all the outer parts we see on a cpu.
1. test each packaged chip again for defects that only show up under real operating conditions, and do final binning to determine which SKU it becomes (i9, i7, etc)
1. ship and sell the finished chips
1. software stack on top of the finished chip:
   1. the cpu is built w/ an instruction set architecture (ISA) like x86 or ARM, which defines the basic commands it can execute.
   1. compilers translate high-level programming languages (C, Rust, etc) into machine code that uses those instructions.
   1. operating system manages which processes get to use the CPU and when, and provides system calls that programs can use to interact with hardware.

## Terminology

Materials & physical artifacts

- Silicon — the element we build chips out of. Comes from quartz sand, refined to extreme purity.
- Wafer — a thin circular slice of pure silicon (usually 300mm across) that serves as the canvas everything gets built on. One wafer becomes hundreds or thousands of chips.
- Die — a single chip. The wafer gets patterned with a grid of identical chip layouts and later cut apart, and each individual rectangle is a die. Like cutting a sheet of brownies into squares.
- Substrate — the small circuit board the bare die gets mounted onto. Acts as an adapter between the die's microscopic connection points and the larger pins/contacts that fit into a motherboard socket.

Building blocks

- Transistor — a tiny electrical switch that turns current on or off. The fundamental unit of computing — billions of these flipping in patterns is what runs everything. The whole manufacturing process exists to build these at scale.
- Doping — deliberately adding tiny amounts of other elements (boron, phosphorus, arsenic) to silicon to change how it conducts electricity. Pure silicon is a bad conductor on its own; doping is what makes transistors possible.

Patterning process

- Photoresist — a light-sensitive coating applied to the wafer. Light changes its solubility, so after exposure, parts of it can be washed away to leave a precise pattern that protects the layer underneath during the next step.
- Photomask — a pre-made stencil containing the chip's circuit pattern. Light shines through it onto the photoresist-covered wafer to transfer the pattern. Each layer of the chip has its own photomask.
- Lithography — the umbrella term for using light to project patterns onto the wafer. Modern chips use extreme ultraviolet (EUV) light because shorter wavelengths can resolve smaller features.

Software & business concepts

- ISA (instruction set architecture) — the published "menu" of commands a CPU supports, like "add these two numbers" or "load this from memory." x86 and ARM are the two dominant ISAs. Software has to be compiled for a specific ISA to run on that CPU.
- Yield — the percentage of chips on a wafer that actually work after all manufacturing steps. A single bad particle in the wrong place can kill a chip, so high yield is what separates profitable fabs from money pits.
