# Linux Gaming Stack

## Why this stack exists

Most PC games are built for Windows. Developers target Windows because that's where the players are, and they write against Windows-only APIs — Win32 for OS-level stuff, DirectX for graphics and audio, XInput for controllers. Linux has a small share of the desktop gaming market, so historically very few studios ship native Linux builds. Even Valve, which pushes Linux gaming hardest, mostly invests in compatibility rather than asking developers to port.

That leaves two ways to play games on Linux:

1. Native Linux games — the developer shipped a Linux build. Simple stack, but the catalog is limited.
1. Windows games via translation — the much larger reality. Tools like Wine and Proton intercept Windows API calls and translate them into Linux equivalents at runtime, while DXVK and VKD3D-Proton translate DirectX graphics calls into Vulkan, which Linux GPU drivers actually speak.

This translation isn't emulation in the slow, instruction-by-instruction sense. It's more like a bilingual interpreter sitting between the game and the OS, converting calls in real time. Modern translation is good enough that many Windows games run as well on Linux as they do on Windows — sometimes better. The remaining pain points are usually anti-cheat (which has to actively allow Linux), launchers, and the occasional game that uses something obscure.

## The mental model

A Windows game expects Win32 APIs, DirectX, and a Windows GPU driver. On Linux, that gets translated into Vulkan calls running against the actual Linux GPU driver (Mesa for AMD/Intel, NVIDIA's proprietary driver for NVIDIA).

Windows game on Linux:

```text
Windows game -> Wine/Proton -> DXVK or VKD3D-Proton -> Vulkan -> Mesa/NVIDIA -> kernel -> GPU
```

Native Linux game:

```text
Game -> Vulkan/OpenGL -> Mesa/NVIDIA -> kernel -> GPU
```

## Graphics APIs

DirectX / Direct3D is Microsoft's Windows graphics API. In gaming contexts, "DirectX" usually means Direct3D specifically. Versions you'll encounter: D3D9 (older games), D3D11 (huge swath of PC games), D3D12 (newer AAA, lower-level). Linux doesn't run DirectX natively — it translates D3D calls into Vulkan.

Vulkan is the cross-platform low-level GPU API maintained by Khronos. It's the target for Linux native games and the backend for D3D translation layers.

OpenGL is the older cross-platform API. Still relevant for older native games, emulators, and some ports, but Vulkan dominates modern Linux gaming. Wine's built-in WineD3D used to translate Direct3D to OpenGL, but DXVK/VKD3D-Proton on Vulkan is now preferred for performance and compatibility.

## Compatibility layers

Wine is the base Windows compatibility layer — not a VM, not an emulator. It translates Windows API calls to POSIX/Linux at runtime, handling the registry, DLL loading, Win32 APIs, filesystem layout, and process behavior. A Wine "prefix" is an isolated fake Windows environment:

```text
~/.wine/
  drive_c/
  registry files
  installed DLLs
```

Tools like Lutris and Bottles create per-game prefixes so DLL overrides and Windows version settings don't pollute other games.

DXVK translates Direct3D 8/9/10/11 to Vulkan, usually inside Wine or Proton. This is the reason a massive number of older and mid-era Windows games run well on Linux.

```text
Game uses D3D11 -> DXVK -> Vulkan -> GPU driver -> GPU
```

VKD3D-Proton is the D3D12 equivalent (a fork of Wine's VKD3D, tuned for Proton). D3D12 is harder to translate because it's already low-level, so VKD3D-Proton is more sensitive to GPU driver quality, Vulkan extensions, shader compilation, and ray tracing behavior.

Proton is Valve's gaming-focused bundle built around Wine. It powers Steam Play and ships as a complete stack: patched Wine, DXVK, VKD3D-Proton, FAudio/XAudio shims, controller fixes, game-specific patches, and Steam integration.

Proton variants:

```text
Proton Stable        default Steam version
Proton Experimental  newer fixes, often useful for recent games
Proton Hotfix        targeted fixes for specific broken games
Proton-GE            community build with extra patches/codecs
```

Start with Stable or Experimental. Reach for Proton-GE when ProtonDB or a game-specific report says it helps.

## Drivers

After translation, Vulkan calls hit a real Linux graphics driver. There are two ecosystems.

Mesa is the open-source Linux graphics driver project — not a vendor, not tied to a specific GPU. It's a collection of drivers maintained collaboratively (with heavy contributions from Intel, AMD, Valve, Red Hat, and independent developers) that ship with most Linux distributions. Mesa is what AMD and Intel GPUs use on Linux, and it contains:

```text
RADV       AMD Vulkan driver
RadeonSI   AMD OpenGL driver
ANV        Intel Vulkan driver
Iris       Intel OpenGL driver
```

So when an AMD card runs a Vulkan game on Linux, the path is `game -> Vulkan API -> RADV (inside Mesa) -> kernel -> GPU`. There's no AMD-branded userspace driver in the picture the way there is on Windows.

NVIDIA is the other ecosystem. NVIDIA ships its own proprietary Linux driver, separate from Mesa, which is what most NVIDIA users run for gaming. There's also a growing open-source story (NVK in Mesa, NVIDIA's open kernel modules), but for now the proprietary driver is still the default for serious gaming on NVIDIA hardware.

Driver freshness matters a lot regardless of vendor — Vulkan extensions, shader behavior, ray tracing, frame pacing, and new-game compatibility all depend on having recent versions.

### Driver Example

Say your game wants to draw a triangle. Roughly:

```text
Game calls vkCmdDraw(3 vertices)
  |
  v
Vulkan loader routes the call to the installed driver
  |
  v
RADV (Mesa) receives the call
  - Looks at current pipeline state
  - Translates "draw 3 vertices" into RDNA3 packet format
  - Writes the packet bytes into a command buffer in GPU-visible memory
  |
  v
Game eventually calls vkQueueSubmit
  |
  v
RADV's userspace tells the kernel driver (amdgpu) "submit this buffer"
  |
  v
amdgpu kernel driver schedules the work, pokes the GPU's ring buffer
  |
  v
GPU hardware reads the packets and executes them — vertex shader runs,
rasterization happens, fragment shader runs, pixels land in a framebuffer
```

NVIDIA's proprietary driver does the same conceptual job, but the translation target is NVIDIA's command format and SASS instruction set, and the kernel side is NVIDIA's nvidia.ko module instead of amdgpu.

## Tooling

Gamescope is Valve's micro-compositor (formerly `steamcompmgr`). It creates an isolated display environment for a game, useful for fullscreen weirdness, resolution scaling, integer scaling, refresh-rate behavior, HDR/VRR scenarios, and Wayland/Xwayland isolation. Central on Steam Deck; on desktop, useful for games that fight your normal compositor.

MangoHud is the Linux equivalent of MSI Afterburner's overlay — a Vulkan/OpenGL overlay showing FPS, frametimes, CPU/GPU load, and temps. Drop `mangohud %command%` into a Steam launch option. Helps answer: am I CPU-bound, GPU-bound, throttling, stuttering on shaders?

Lutris is a launcher/manager especially useful for non-Steam games — GOG, Epic, Ubisoft, Battle.net, emulators, custom Wine setups. Use Steam/Proton for Steam games; use Lutris for everything else.

Bottles is a GUI manager for Wine prefixes, treating each Windows app as a separate environment. More of a clean prefix manager; Lutris is more of a full game library/launcher.

ProtonDB is the community compatibility database for Steam games on Proton. Check it before buying or when debugging — it surfaces things like "needs Proton-GE," "needs launch options," "single-player works but anti-cheat blocks multiplayer."

## Anti-cheat

Still one of the biggest Linux gaming pain points. Proton supports Easy Anti-Cheat and BattlEye, but developers have to enable Linux/Proton support per-title. This is why you see:

```text
Game launches:        yes
Single-player works:  yes
Multiplayer works:    no — anti-cheat not enabled for Linux
```

When a game fails on Linux, Wine/DXVK/Proton aren't always the cause — sometimes the game runs fine but anti-cheat or the launcher blocks it.

## Other pieces worth knowing

WineD3D — Wine's built-in Direct3D-to-OpenGL implementation. Still a fallback for some older games, but DXVK is preferred for D3D8/9/10/11.

FAudio / XAudio — Windows audio API shims so game audio works under Wine/Proton. Usually invisible.

XInput / SDL / Steam Input — controller translation. Windows games expect Xbox-style XInput; Linux uses evdev/SDL/Steam Input. Proton + Steam Input bridges this.

Shader caches — shader compilation under Vulkan/D3D translation causes stutter when it happens mid-gameplay. Steam pre-caches shaders for Proton games, which is part of why Steam's experience feels smoother than raw Wine.

Wayland / X11 / Xwayland — most games still go through Xwayland even on Wayland desktops. Surfaces as fullscreen behavior, VRR, HDR, scaling, and multi-monitor weirdness. Gamescope can isolate it.

## Quick paths

Steam Windows game:

```text
Steam -> Proton -> Wine + DXVK/VKD3D-Proton -> Vulkan -> Mesa/NVIDIA -> GPU
```

Non-Steam Windows game:

```text
Lutris/Bottles/Heroic -> Wine or Proton-derived runner -> DXVK/VKD3D-Proton -> Vulkan -> GPU
```

Native Linux game:

```text
Game -> Vulkan/OpenGL -> Mesa/NVIDIA -> GPU
```

## Beginner rule of thumb

Use Steam + Proton first. Check ProtonDB when something breaks. Use Proton Experimental or Proton-GE only when needed. Use Lutris or Bottles for everything outside Steam.

## Glossary at a glance

```text
DirectX / Direct3D  what many Windows games are written against
Wine                translates Windows OS/API behavior
DXVK                D3D8/9/10/11 -> Vulkan
VKD3D-Proton        D3D12 -> Vulkan
Vulkan              modern cross-platform GPU API
Mesa / NVIDIA       actual Linux GPU drivers
Proton              Valve's bundled gaming compatibility stack
Lutris / Bottles    managers for non-Steam/custom Wine setups
Gamescope           display/compositor wrapper
MangoHud            performance overlay
ProtonDB            community compatibility reports
```
