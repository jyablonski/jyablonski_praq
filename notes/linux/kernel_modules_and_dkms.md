# Linux Kernel Modules and DKMS

## The Kernel and Modules

The Linux kernel is the core program managing hardware, memory, processes, and filesystems. It can be extended with modules: pieces of code loaded into the running kernel to add functionality. GPU drivers are modules. They live as `.ko` files (kernel objects) under `/lib/modules/<kernel-version>/`, with each kernel version having its own directory because modules are tied to the specific kernel they were built for.

## In-Tree vs Out-of-Tree Modules

In-tree modules are part of the official kernel source code maintained by the kernel team. They get built alongside the kernel automatically and are updated by the same people changing kernel internals. Examples: `amdgpu`, `i915`, most network drivers.

Out-of-tree modules are maintained externally in a separate codebase. They must be compiled separately and dropped into `/lib/modules/<kernel-version>/`. Examples: Nvidia proprietary driver, ZFS, VirtualBox, some Wi-Fi drivers.

## No Stable Kernel ABI

Linux deliberately does not provide a stable ABI (Application Binary Interface) for in-kernel modules. Internals like struct layouts, function signatures, and exported symbols can change between any version, including minor or patch releases.

Distinction worth knowing:

- API: source-level contract (function names, argument types)
- ABI: binary-level contract (memory layouts, register conventions, struct field offsets)

Linux refuses to stabilize either for in-kernel modules. The user-space ABI (syscalls) is sacred and never broken, but that's separate.

Reasons:

- Freedom to refactor kernel internals without maintaining shims forever
- Pressure on hardware vendors to upstream their drivers (in-tree drivers get updated automatically when internals change)
- Performance and code-health priorities over external module convenience

The canonical reasoning is in the kernel source at `Documentation/process/stable-api-nonsense.rst`.

## Why DKMS Exists

Without a stable ABI, an out-of-tree `.ko` compiled against kernel 6.8 may not load against 6.9, even if it loads it might crash. The module must be recompiled against each new kernel's headers.

DKMS (Dynamic Kernel Module Support) is the framework that automates this. When a new kernel is installed, DKMS hooks into the package manager's post-install scripts and:

1. Looks at registered out-of-tree module sources in `/usr/src/<module>-<version>/`
1. Finds kernel headers for the newly installed kernel
1. Runs the build (essentially `make` against those headers)
1. Drops the resulting `.ko` into `/lib/modules/<new-kernel>/updates/`
1. Runs `depmod` so the kernel can find the module

It is a build automation tool, not a compatibility detector.

## Kernel Headers

Kernel headers are `.h` files declaring kernel structs, function signatures, macros, and constants without implementations. They're the "shape" of the kernel that out-of-tree code needs to compile against. They live under `/usr/lib/modules/<kernel-version>/build/include/`.

A simplified slice from something like `linux/module.h`:

```c
struct module {
    enum module_state state;
    struct list_head list;
    char name[MODULE_NAME_LEN];
    const struct kernel_symbol *syms;
    unsigned int num_syms;
    void *init;
    /* ... many more fields ... */
};

int register_module(struct module *mod);
void unregister_module(struct module *mod);
```

A driver does `#include <linux/module.h>` and calls into these. If a future kernel reorders struct fields or renames a function, the same source produces a different (or failing) compile.

## When DKMS Fails

Most kernel updates don't touch what Nvidia or other out-of-tree modules depend on, so rebuilds succeed silently. When they fail, common causes:

- Kernel API changes (function renamed, signature changed, removed) break the driver source
- Missing kernel headers package for the new kernel
- Compiler version mismatches
- Disk full or broken build environment

When DKMS fails, the new kernel boots without the module, and you fall back to whatever else can drive the hardware (nouveau, basic framebuffer).

## You Cannot Know in Advance

The package manager knows `nvidia` depends on `linux` being installed but does not know whether the Nvidia source will actually compile against the new kernel headers. That validation only happens when DKMS runs, after the new kernel is already on disk.

Mitigations on rolling-release distros:

- LTS kernel installed alongside main kernel as a fallback boot option
- Holding back kernel updates with `IgnorePkg` in `/etc/pacman.conf` until verified
- Btrfs snapshots or timeshift for rollback
- Reading distro news (Arch news page) before big updates
- Distro testing repos that catch breakage before it hits stable

## Possible Outcomes After a Kernel Update

1. Build succeeds, module loads, hardware works (the 95%+ case)
1. Build fails, compile error surfaced, module missing on next boot
1. Build succeeds but module misbehaves at runtime (rare, DKMS cannot catch this)

## Summary

- Modules are kernel extensions tied to a specific kernel version
- Out-of-tree modules need recompilation on every kernel update because Linux has no stable in-kernel ABI
- DKMS automates that recompilation by invoking the build against new kernel headers
- The package manager triggers DKMS via post-install hooks during kernel upgrades
- Compatibility cannot be predicted ahead of time, only discovered when the build runs
- In-tree drivers (AMD, Intel GPU) avoid this entirely because they are updated as part of the kernel itself
