# Proton

Proton is a Linux compatibility layer developed by Valve that allows Windows games to run on Linux. It essentially translates Windows game code so it works on Linux without requiring game developers to port their games.

It's built on top of Wine which translates Windows API calls to Linux. Valve takes Wine and adds a bunch of game-specific improvements such as DXVK (translating DirectX to Vulkan) and other performance optimizations.

- DXVK only handles DirectX 9, 10, and 11
- VKD3D-Proton is a Proton component which translates DirectX 12 calls to Vulkan

This reduces the dependence on Windows for PC gaming and supports Valve's Steamdeck Product, which is a handheld gaming console which runs on Linux.

Proton can run most games at near-native performance, or sometimes even better, but it varies by title.

## How It Works

When you install a Windows game through Steam on Linux, Proton automatically runs in the background. You click play and it just works.

You have to enable compatibility for the specific game you want to run, and then select your Proton version. Experimental is the bleeding edge version that Valve releases, which has the newest possible updates but can also introduce bugs that aren't fixed yet like in most major / minor versions.

When you install Proton, it includes:

- Wine compatibility layer
- DXVK / VKD3D (DirectX to Vulkan translation)
- Various helper tools and libraries
- Media codecs (to decompress audio / video data)
- Downloads to `~/.steam/steam/steamapps/common/Proton - Experimental/`

Basically you get the pre-compiled executables and libraries. Everything is ready to run, there's no compilation needed. That's why it's plug & play and so seamless.

### Advanced

Proton also includes various optimizations to handle OS thread synchronization so you can play games at optimal performance.

- Multiple threads are used to run games (1 renders graphics, 1 plays audio, another manages physics etc)
- These threads have to coordinate with each other and write & share data in memory safely without interfering with one another
- Windows handles thread synchronization differently than Linux
- Wine handles synchronization in a simple but not so optimal way using polling

Esync and Fsync are basically event-based thread synchronization optimizations to improve efficiency and performance, while vanilla Wine is polling based which is simple but less efficient.

Esync (Eventfd Synchronization)

- Uses Linux's `eventfd` system to handle synchronization more efficiently
- Instead of constantly polling, threads can sleep until they're actually needed
- Leads to less CPU overhead, better performance, especially in CPU-bound games
- But, your system needs to have high enough file descriptor limits

Fsync (Futex Synchronization)

- The newer, better version of Esync
- Uses Linux `futex` (fast userspace mutex) system calls
- Even more efficient than Esync - handles synchronization in userspace when possible
- Enables better performance than Esync, especially in games with heavy threading
- But, requires a relatively recent Linux kernel (5.16+)

NTSync

- The newest synchronization method, requires kernel 6.14+ with `CONFIG_NTSYNC=y` or `CONFIG_NTSYNC=m`
- Even more efficient than Fsync, implements Windows NT synchronization primitives directly in the kernel
- Available in GE-Proton10-10+

## What Ships in a Proton Release

A Proton build bundles together many external projects (submodules) pinned to specific commits. Here's what gets compiled and packaged:

Core Components

| Component | Purpose |
| ------------ | ------------------------------------------------------------------- |
| Wine | Core Windows compatibility layer (Valve's fork with Proton patches) |
| wine-staging | Additional community Wine patches |
| DXVK | Translates DirectX 9/10/11 -> Vulkan |
| VKD3D-Proton | Translates DirectX 12 -> Vulkan |
| dxvk-nvapi | NVIDIA API support for DLSS, PhysX, etc. |

Media & Codecs

| Component | Purpose |
| --------------------- | ---------------------------------- |
| FFmpeg | Video/audio decoding |
| GStreamer (+ plugins) | Media framework for video playback |
| dav1d | AV1 video decoder |

Graphics & VR

| Component | Purpose |
| ------------------------------ | ---------------------- |
| Vulkan-Headers / SPIRV-Headers | Vulkan API definitions |
| OpenVR / OpenXR-SDK | VR support |
| wineopenxr | XR translation layer |

Steam Integration

| Component | Purpose |
| ------------ | ------------------------------- |
| lsteamclient | Steam API translation |
| steam_helper | Proton's integration with Steam |
| vrclient_x64 | VR client wrapper |

Game Fixes

| Component | Purpose |
| ----------- | ------------------------------------------------------ |
| protonfixes | Per-game workarounds (winetricks, env vars, overrides) |
| patches/ | Custom Wine/component patches |

### Release Tarball Structure

When you download a release like `GE-Proton10-25.tar.gz`, you get:

```
GE-Proton10-25/
├── proton                    # Main Python script that Steam calls
├── compatibilitytool.vdf     # Tells Steam this is a compatibility tool
├── toolmanifest_runtime.vdf  # Runtime manifest
├── version                   # Version string
├── files/
│   ├── bin/                  # wine, wine64, wineserver binaries
│   ├── lib/                  # 32-bit libraries (*.dll.so, *.so)
│   ├── lib64/                # 64-bit libraries
│   └── share/
│       └── wine/
│           └── gecko/        # Wine's IE replacement
│           └── mono/         # .NET implementation
└── protonfixes/              # Game-specific fixes
```

The `lib/` and `lib64/` directories contain compiled DXVK, VKD3D, Wine libraries, etc.

### Useful Environment Variables

| Variable | Description |
| -------------------------------- | -------------------------------------------------------- |
| `PROTON_LOG=1` | Dump debug log to `$HOME/steam-$APPID.log` |
| `PROTON_USE_WINED3D=1` | Use OpenGL wined3d instead of DXVK |
| `PROTON_NO_ESYNC=1` | Disable Esync |
| `PROTON_NO_FSYNC=1` | Disable Fsync |
| `PROTON_ENABLE_NVAPI=1` | Enable NVIDIA NVAPI support |
| `WINE_FULLSCREEN_FSR=1` | Enable AMD FSR upscaling |
| `WINE_FULLSCREEN_FSR_STRENGTH=2` | FSR sharpening (0=max, 5=min, 2=default) |
| `PROTON_ENABLE_WAYLAND=1` | Enable native Wayland (requires Mesa 25+ or NVIDIA 575+) |
| `PROTON_ENABLE_HDR=1` | Enable HDR support |

### Important Notes

- Proton runs in a container with a specific runtime environment - running it outside Steam without proper tooling breaks library compatibility
- For non-Steam games, use [UMU](https://github.com/Open-Wine-Components/umu-launcher) which properly replicates Steam's containerized environment
- Lutris and Heroic have UMU integration built-in when using GE-Proton
- Proton GE is NOT affiliated with Valve - bug reports should go to the GE GitHub, not Valve's tracker

## Proton GE

Proton GE (GloriousEggroll) is a community-maintained custom build of Proton maintained by Thomas Crider. It's not a fork in the traditional sense - it's a custom build that pulls from Valve's Proton, applies additional patches, and bundles newer/different versions of components.

What makes it different from official Proton:

- Additional media foundation patches for better video playback support
- AMD FSR patches added directly to fullscreen hack (`WINE_FULLSCREEN_FSR=1`)
- NVIDIA CUDA support for PhysX and NVAPI
- Raw input mouse support
- Protonfixes system - automated per-game fixes (winetricks, env vars, EAC workarounds)
- Various upstream Wine patches backported before they hit official Proton
- Wine-staging patches applied as needed
- NTSync enablement if kernel supports it
- Native Wayland support via `PROTON_ENABLE_WAYLAND=1`

When to use Proton GE: If a game doesn't work well on official Proton, Proton-GE is often the first thing to try. It frequently has fixes for specific games before Valve officially addresses them.
