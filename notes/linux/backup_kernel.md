# Arch Linux LTS Fallback Kernel With systemd-boot

## Purpose

A secondary LTS kernel entry provides a bootable fallback option when the primary rolling-release kernel breaks. This avoids needing to boot from a USB flash drive to repair the system.

## Use Case

The primary Arch kernel (`linux`) updates frequently and occasionally introduces regressions, whether from the kernel itself, driver changes, or initramfs issues. The `linux-lts` package tracks the latest LTS release from kernel.org, which receives fewer updates and is generally more stable. Having both installed with separate boot loader entries means you can select the working kernel at boot time if the primary one fails.

## What This Helps With

- Kernel panics or boot failures after a `linux` package update
- Driver regressions in newer kernels (GPU, networking, filesystems)
- Initramfs generation failures specific to the primary kernel
- Any situation where the machine won't boot past the kernel stage

## What This Does Not Help With

- Userspace breakage (desktop environment updates, library incompatibilities, display manager failures). The LTS kernel still boots into the same root filesystem, so broken packages remain broken.
- Filesystem corruption or broken fstab/crypttab configurations
- Bootloader corruption (if systemd-boot itself is broken, neither entry will load)
- BIOS/UEFI firmware issues

For userspace-level rollback, consider btrfs snapshots with snapper or timeshift, which allow booting into a previous snapshot of the entire root filesystem.

## Setup

### Install the LTS Kernel

```bash
sudo pacman -S linux-lts linux-lts-headers
```

### Create the Boot Loader Entry

Copy the existing entry and modify it:

```bash
sudo cp /boot/loader/entries/2025-12-28_04-10-48_linux.conf /boot/loader/entries/arch-lts-backup.conf
```

Edit `arch-lts-backup.conf` to point at the LTS kernel and initramfs:

```
# Created by: archinstall
# Created on: 2026-04-11_04-10-48
title   Arch Linux LTS (backup)
linux   /vmlinuz-linux-lts
initrd  /initramfs-linux-lts.img
options root=PARTUUID=35d8f0f3-dd1e-49b0-9f9f-87fd6366fb74 zswap.enabled=0 rw rootfstype=ext4
```

The `options` line should be identical to the primary entry. Only the `title`, `linux`, and `initrd` lines change.

### Verify

```bash
bootctl list
```

Both entries should appear. The primary kernel remains the default.

### Ensure the Boot Menu Is Visible

In `/boot/loader/loader.conf`, set a timeout so you can select the fallback entry:

```
timeout 3
default 2025-12-28_04-10-48_linux.conf
```

## Maintenance

The `linux-lts` package updates through `pacman -Syu` like any other package. Its initramfs is regenerated automatically via the mkinitcpio preset at `/etc/mkinitcpio.d/linux-lts.preset`. No manual maintenance is required beyond not removing the package.

## Verification

After setup, reboot and select the LTS entry from the systemd-boot menu to confirm it boots correctly. Test this before you actually need it.
