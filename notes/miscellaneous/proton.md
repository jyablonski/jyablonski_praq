# Proton

Proton is a Linux compatability layer developed by Valve that allows Windows games to run on Linux. It essentially translates Windows game code so it works on Linux without requiring game developers to port their games.

It's built on top of Wine which translates Windows API calls to Linux. Valve takes Wine and adds a bunch of game-specific improvements such as DXVK (translating DirectX to Vulkan) and other performance optimizations.

- DXVK only handles DirectX 9, 10, and 11
- VKD3D-Proton is a Proton component which translates DirectX 12 calls to Vulkan

This reduces the dependence on Windows for PC gaming and supports Valve's Steamdeck Product, which is a handheld gaming console which runs on Linux.

Proton can run most games at near-native performance, or sometimes even better, but it varies by title.

## How It Works

When you install a Windows game through Steam on Linux, Proton automatically runs in the background. You click play and it just works.

You have to enable compatability for the specific game you want to run, and then select your Proton version. Experimental is the bleeding edge version that Valve releases, which has the newest possible updates but can also introduce bugs that aren't fixed yet like in most major / minor versions.

When you install Proton, it includes:

- Wine compatability layer
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

Esync and Fsync are basically event-based thread synchronization optimizations to improve efficiency and performance, while vanilla Wine is polling based which is simple but less efficient

Esync (Eventfd Synchronization)

- Uses Linux's `eventfd` system to handle synchronization more efficiently
- Instead of constantly polling, threads can sleep until they're actually needed
- Leads to less CPU overhead, better performance, especially in CPU-bound games
- But, your system needs to have high enough file descriptor limits

Fsync (Futex Synchronization):

- The newer, better version of Esync
- Uses Linux `futex` (fast userspace mutex) system calls
- Even more efficient than Esync - handles synchronization in userspace when possible
- Enables better performance than Esync, especially in games with heavy threading
- But, requires a relatively recent Linux kernel (5.16+)
