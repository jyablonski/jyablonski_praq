# What Happened

After a bad-shutdown sequence (MSI OLED off → digital vibrance automation failed → reboot), GNOME flipped the `org.gnome.shell.disable-user-extensions` dconf key to `true`. That's a global kill switch — when it's on, GNOME refuses to load any user extension, regardless of what's in the `enabled-extensions` list. Most likely GNOME's safe mode auto-triggered after detecting an unclean session, but it could also have been an automation touching dconf during the failed boot.

That's why everything looked correct on the surface — appindicator was installed, metadata listed GNOME 50, the extension was in `enabled-extensions` — but `gnome-extensions enable` kept silently no-op'ing and the state stayed stuck at `INITIALIZED`. The kill switch was overriding everything downstream.

The fix:

```bash
gsettings set org.gnome.shell disable-user-extensions false
```

Then log out and back in (Wayland needs a fresh session to cold-load extensions).

Why it was hard to diagnose:

Nothing surfaces this. `gnome-extensions enable` returns success. The journal doesn't log "I'm refusing to load extensions because the kill switch is on." The metadata, the package, the enabled list — all looked fine. You have to know to check that one specific gsettings key, and it's not in any of the obvious troubleshooting docs.

## Follow Ups

### Ruled out: nvibrant as the cause

Initially suspected the digital vibrance autostart (`~/.config/autostart/nvibrance.desktop` running `uvx nvibrant 0 650 0 650 0 650 0`) was corrupting session state. Verified via journalctl that nvibrant runs cleanly even when displays are disconnected — it correctly reports `None` for unpowered/disconnected ports and exits without error. nvibrant uses ioctl calls to `/dev/nvidia-modeset` and does not touch dconf or session state. The vibrance automation is innocent. The OLED being off at boot was a symptom of the actual problem, not the cause.

### Root cause of the OLED-off-at-boot issue: missing NVIDIA suspend/resume config

The "monitor doesn't turn on at boot/resume" issue is a well-documented NVIDIA + Wayland + Arch problem. On suspend or cold boot, VRAM contents decay and the driver can't re-establish display state cleanly — resulting in black screens, dead DP links, or monitors that stay in deep sleep. The system was running with zero NVIDIA suspend/resume configuration:

- No `/etc/modprobe.d/nvidia*.conf` file existed
- `nvidia-suspend.service`, `nvidia-resume.service`, `nvidia-hibernate.service` all disabled
- No `NVreg_PreserveVideoMemoryAllocations` on kernel cmdline
- No explicit `nvidia_drm.modeset=1` / `nvidia_drm.fbdev=1` on kernel cmdline

### Fixes applied

1. Created `/etc/modprobe.d/nvidia.conf`:
