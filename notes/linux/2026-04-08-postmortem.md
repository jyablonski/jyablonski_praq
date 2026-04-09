# Postmortem: GNOME login loop + boot failure (2026-04-08)

## Summary

A GNOME 50 upgrade on Arch triggered a login loop. A manual session workaround made things worse, and a concurrent EFI corruption prevented the system from booting entirely. Three independent failure layers, resolved in sequence.

______________________________________________________________________

## Root Causes

### GNOME 50 session regression

GNOME 50 tightened its dependency on systemd user sessions. A previously working workaround — launching GNOME via `dbus-run-session gnome-shell --wayland` — no longer satisfied session requirements, causing an immediate exit and login loop.

Confirmed by:

```
org.freedesktop.systemd1 does not exist
```

### Corrupted user config

The upgrade left stale state in `~/.config` and `~/.local`. Even after fixing the systemd issue, GNOME would read bad config, exit cleanly, and loop again.

### EFI partition corruption

Separately, the FAT32 EFI partition became corrupted and remounted read-only. `mkinitcpio` couldn't write the initramfs, and the bootloader couldn't read it on next boot:

```
Error preparing initrd: Volume Corrupt
```

______________________________________________________________________

## Resolution

### 1. Restore boot (Arch ISO)

```bash
fsck.fat -a /dev/nvme0n1p1
mkinitcpio -P
bootctl install
```

### 2. Fix GNOME login loop

Removed the `dbus-run-session` hack, restored GDM as the login manager, and wiped broken user state:

```bash
mv ~/.config ~/.config.bak
mv ~/.local ~/.local.bak
mv ~/.cache ~/.cache.bak
```

### 3. Rebuild user environment

Selectively restored `.local` for non-GNOME apps only. Avoided restoring anything touching `gnome-shell`, `xdg-desktop-portal`, or keyring/session artifacts.

### 4. Rebuild systemd user services

Recreated `goarctis.service` and `nvibrance.service` with corrected paths. GPU commands were running before NVIDIA was ready — fixed with:

```ini
ExecStartPre=/usr/bin/sleep 5
```

______________________________________________________________________

## Takeaways

- Don't launch GNOME outside of systemd. `dbus-run-session gnome-shell` is not a valid session.
- `~/.config` and `~/.local` are not sacred. Wipe and selectively restore when debugging session issues.
- FAT32 EFI partitions are fragile. A corrupted write during a kernel update is enough to prevent boot entirely.
- `After=graphical-session` in a unit file does not guarantee hardware is ready. Add delays for GPU-dependent services.

______________________________________________________________________

## Current State

| Component | Status |
| -------------------- | -------- |
| Boot | healthy |
| GNOME login | working |
| systemd user session | correct |
| User services | restored |
