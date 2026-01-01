# Arch Linux Install

## Arch Terminology

- **Pacman**: Arch's package manager for installing, updating, and managing software packages from official repositories.
  - Requires root (sudo) for system-wide changes.
  - Example: `sudo pacman -S discord`
- **AUR (Arch User Repository)**: A community-driven repository of user-submitted packages not found in the official repositories.
  - You use **yay** (Yet Another Yogurt) as an AUR helper to simplify installing and managing AUR packages.
  - Example: `yay -S spotify`
- **Systemd-boot**: A simple UEFI boot manager that comes with systemd, used to boot operating systems on UEFI systems.

### Arch Pacman Commands

**Common operations:**

| Flag | Meaning | Example |
| ------ | -------------------------- | ------------------- |
| `-S` | Sync/install package | `pacman -S firefox` |
| `-R` | Remove package | `pacman -R firefox` |
| `-Q` | Query installed packages | `pacman -Q` |
| `-Syu` | Sync, refresh, upgrade all | `pacman -Syu` |

**Useful modifiers:**

| Flag | Meaning | Example |
| ------ | -------------------------------------- | --------------------- |
| `-Ss` | Search for package | `pacman -Ss spotify` |
| `-Qs` | Search installed packages | `pacman -Qs nvidia` |
| `-Si` | Info about a package | `pacman -Si firefox` |
| `-Rs` | Remove package + orphaned dependencies | `pacman -Rs firefox` |
| `-Rns` | Remove + dependencies + config files | `pacman -Rns firefox` |

## Install Media

1. Install OS boot media

- Go to https://archlinux.org/download/
- Download `archlinux-<date>-x86_64.iso` from a nearby mirror in your region (should be between 800 MB - 1.5 GB)
- Verify the download if desired (checksums are provided on the download page)
  - Download PGP signature
  - Run `gpg --verify ~/Downloads/archlinux-2025.12.01-x86_64.iso.sig ~/Downloads/archlinux-2025.12.01-x86_64.iso`
  - You want to see `Good signature ...`

2. Flash the boot media onto a USB Drive

- This requires first wiping the USB Drive
- This ISO File that we download isnt bootable by the Motherboard out of the box
- Then use belena-etcher to flash the boot media onto the USB Drive; you can't just drag and drop the raw iso image into the USB Drive and expect it to work
- This turns the .iso image on the USB Drive into a bootable device, and it places the files in a layout that the system can understand and use during insetallation

3. Plug USB Drive into new PC and get into the BIOS menu by spamming delete or f12 keys.

1. Once in BIOS, select the USB drive as the boot device

- Look for "Boot Menu" or "Boot Order" in your BIOS
- Select your USB drive (might show as the manufacturer name or "UEFI: USB")
- Save and exit—system will reboot into the Arch live environment

5. Connect to the internet

- For ethernet: should work automatically
- For wifi: run `iwctl`, then `station wlan0 connect "Your-SSID"`, enter password, `exit`
- Verify with `ping -c 3 archlinux.org`

6. Run `archinstall` and complete the setup

- Select your drive (the new Samsung NVMe)
- Filesystem: ext4
- No disk encryption needed
- Bootloader: systemd-boot for single-boot or GRUB for dual-boot
- Create your user account
- Select desktop environment (GNOME)
- Enable NetworkManager when prompted
- Let it install, then reboot and remove the USB

## Post-Install Steps

### Enable multilib repository

Edit `/etc/pacman.conf` and uncomment:

```
[multilib]
Include = /etc/pacman.d/mirrorlist
```

Then refresh:

```bash
sudo pacman -Syu
```

### Nvidia Drivers

```bash
sudo pacman -S nvidia nvidia-utils lib32-nvidia-utils nvidia-settings
```

### Shell Setup (zsh)

#### Install zsh and plugins

```bash
sudo pacman -S zsh zsh-autosuggestions zsh-syntax-highlighting
```

#### Set as default shell

```bash
chsh -s /usr/bin/zsh
```

Log out and back in for it to take effect.

#### Create ~/.zshrc

- This runs on every new shell (good for aliases, history settings, plugins).

```bash
nvim ~/.zshrc
```

```bash
# History
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt APPEND_HISTORY

# Plugins
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Aliases
alias ll='ls -alF'
alias la='ls -A'
alias k='kubectl'
alias grep='grep --color=auto'

# Path
export PATH=$PATH:$HOME/.local/bin
export PATH=$PATH:$HOME/.cargo/bin
export PATH=$PATH:$(go env GOPATH)/bin

# Cargo
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"
```

#### Create ~/.zprofile

This runs once at login (good for environment variables and one-time commands like digital vibrance).

```bash
nvim ~/.zprofile
```

```bash
# Digital vibrance on login (X11 only)
if [[ -z $WAYLAND_DISPLAY ]] && [[ -n $DISPLAY ]]; then
    nvidia-settings -a "DigitalVibrance=650" &>/dev/null
fi

```

### Git & SSH Key

#### Install git

```bash
sudo pacman -S git
```

#### Configure git

```bash
git config --global user.name "Jacob Yablonski"
git config --global user.email "jyablonski9@gmail.com"
git config --global init.defaultBranch main
```

#### Generate SSH key

```bash
ssh-keygen -t ed25519 -C "jyablonski9@gmail.com"
```

Press enter to accept default location, optionally set a passphrase.

#### Start ssh-agent and add key

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

#### Copy public key to clipboard

```bash
sudo pacman -S xclip
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard
```

Then add to GitHub: Settings -> SSH and GPG keys -> New SSH key

#### Test connection

```bash
ssh -T git@github.com
```

### Development Tools

#### Base development packages

```bash
sudo pacman -S base-devel neovim curl wget unzip lshw dmidecode
```

#### Python (uv)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart shell, then verify:

```bash
uv --version
```

#### Go

```bash
sudo pacman -S go
```

#### Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Terraform

```bash
sudo pacman -S terraform
```

#### kubectl

```bash
sudo pacman -S kubectl
```

#### Docker

```bash
sudo pacman -S docker docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and back in for docker group to take effect.

### Gaming

#### Steam

```bash
sudo pacman -S steam
```

Launch Steam and log in. Proton should be available in Steam Play settings.

#### 500GB Game Drive

Find the drive:

```bash
lsblk
```

Create mount point and mount:

```bash
sudo mkdir /mnt/games
sudo mount /dev/sda1 /mnt/games  # adjust device name as needed
```

Add to `/etc/fstab` for auto-mount:

```bash
# Get UUID
blkid /dev/sda1

# Add to /etc/fstab
UUID=your-uuid-here  /mnt/games  ntfs-3g  defaults,nofail  0  0
# or if ext4:
UUID=your-uuid-here  /mnt/games  ext4     defaults,nofail  0  0
```

Point Steam to the drive: Settings -> Storage -> Add Drive -> /mnt/games

### Apps

#### Discord

```bash
sudo pacman -S discord
```

#### Spotify

Spotify is in the AUR. First install an AUR helper:

```bash
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
cd ..
rm -rf yay
```

Then install Spotify:

```bash
yay -S spotify
```

#### Firefox

```bash
sudo pacman -S firefox
```

#### VS Code (or Cursor)

```bash
yay -S visual-studio-code-bin
# or for Cursor:
yay -S cursor-bin
```

#### nvibrant

Setup digital vibrance on Wayland - this didn't work on Ubuntu but worked fine out of the box w/ Arch

- https://github.com/Tremeschin/nvibrant

### Makefile

```makefile
.PHONY: update
update:
	@echo ------------------------------------------------------------
	@echo hello jacob, running updates for `date` --------------------
	@sudo pacman -Syu
	@yay -Syu --aur
	@echo ------------------------------------------------------------
	@echo updates complete at `date`, hasta la vista -----------------

.PHONY: parts
parts:
	@echo motherboard is ---------
	@sudo dmidecode -t 2
	@echo cpu is -----------------
	@sudo dmidecode -t 4
	@echo gpu is -----------------
	@lspci | grep ' VGA ' | cut -d" " -f 1 | xargs -i lspci -v -s {}
	@echo gpu driver is ----------
	@nvidia-smi
	@echo ram is -----------------
	@sudo lshw -C memory

.PHONY: uv-update
uv-update:
	@uv self update

.PHONY: clean
clean:
	@echo cleaning package cache ---------
	@sudo pacman -Sc --noconfirm
	@echo removing orphaned packages -----
	@sudo pacman -Rns $(pacman -Qdtq) 2>/dev/null || echo "no orphans to remove"

.PHONY: installed
installed:
	@pacman -Qe

.PHONY: search
search:
	@pacman -Ss $(pkg)

.PHONY: info
info:
	@echo kernel -------------------
	@uname -r
	@echo uptime -------------------
	@uptime
	@echo disk usage ---------------
	@df -h / /mnt/games 2>/dev/null || df -h /
	@echo memory -------------------
	@free -h
```

### Reboot

```bash
reboot
```

### Environment Files

`.env` files were copied into Discord, pull from there into local directories as needed.

### Post-Reboot Checklist

- [ ] Nvidia driver working: `nvidia-smi`
- [ ] Digital vibrance applied (check nvidia-settings)
- [ ] Steam launches and sees game drive
- [ ] SSH key works: `ssh -T git@github.com`
- [ ] zsh plugins working (type a command, should see suggestions)

## Full Package List

Full package list after ~3 days of Arch:

```sh
[2025-12-28T04:11:10+0000] [ALPM] installed iana-etc (20251120-1)
[2025-12-28T04:11:10+0000] [ALPM] installed filesystem (2025.10.12-1)
[2025-12-28T04:11:10+0000] [ALPM] installed linux-api-headers (6.17-1)
[2025-12-28T04:11:10+0000] [ALPM] installed tzdata (2025c-1)
[2025-12-28T04:11:10+0000] [ALPM] installed glibc (2.42+r33+gde1fe81f4714-1)
[2025-12-28T04:11:10+0000] [ALPM] installed gcc-libs (15.2.1+r301+gf24307422d1d-1)
[2025-12-28T04:11:10+0000] [ALPM] installed ncurses (6.5-4)
[2025-12-28T04:11:10+0000] [ALPM] installed readline (8.3.003-1)
[2025-12-28T04:11:10+0000] [ALPM] installed bash (5.3.9-1)
[2025-12-28T04:11:10+0000] [ALPM] installed acl (2.3.2-1)
[2025-12-28T04:11:10+0000] [ALPM] installed attr (2.5.2-1)
[2025-12-28T04:11:10+0000] [ALPM] installed gmp (6.3.0-2)
[2025-12-28T04:11:10+0000] [ALPM] installed zlib (1:1.3.1-2)
[2025-12-28T04:11:10+0000] [ALPM] installed sqlite (3.51.1-1)
[2025-12-28T04:11:10+0000] [ALPM] installed util-linux-libs (2.41.3-1)
[2025-12-28T04:11:10+0000] [ALPM] installed e2fsprogs (1.47.3-2)
[2025-12-28T04:11:10+0000] [ALPM] installed keyutils (1.6.3-3)
[2025-12-28T04:11:10+0000] [ALPM] installed gdbm (1.26-1)
[2025-12-28T04:11:11+0000] [ALPM] installed openssl (3.6.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libsasl (2.1.28-5)
[2025-12-28T04:11:11+0000] [ALPM] installed libldap (2.6.10-2)
[2025-12-28T04:11:11+0000] [ALPM] installed libevent (2.1.12-4)
[2025-12-28T04:11:11+0000] [ALPM] installed libverto (0.3.2-5)
[2025-12-28T04:11:11+0000] [ALPM] installed lmdb (0.9.33-1)
[2025-12-28T04:11:11+0000] [ALPM] installed krb5 (1.21.3-2)
[2025-12-28T04:11:11+0000] [ALPM] installed libcap-ng (0.8.5-3)
[2025-12-28T04:11:11+0000] [ALPM] installed audit (4.1.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libxcrypt (4.5.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libtirpc (1.3.7-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libnsl (2.0.1-1)
[2025-12-28T04:11:11+0000] [ALPM] installed pambase (20250719-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libgpg-error (1.58-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libgcrypt (1.11.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed lz4 (1:1.10.0-2)
[2025-12-28T04:11:11+0000] [ALPM] installed xz (5.8.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed zstd (1.5.7-2)
[2025-12-28T04:11:11+0000] [ALPM] installed systemd-libs (259-1)
[2025-12-28T04:11:11+0000] [ALPM] installed pam (1.7.1-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libcap (2.77-1)
[2025-12-28T04:11:11+0000] [ALPM] installed coreutils (9.9-1)
[2025-12-28T04:11:11+0000] [ALPM] installed bzip2 (1.0.8-6)
[2025-12-28T04:11:11+0000] [ALPM] installed libseccomp (2.5.6-1)
[2025-12-28T04:11:11+0000] [ALPM] installed file (5.46-5)
[2025-12-28T04:11:11+0000] [ALPM] installed findutils (4.10.0-3)
[2025-12-28T04:11:11+0000] [ALPM] installed mpfr (4.2.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed gawk (5.3.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed pcre2 (10.47-1)
[2025-12-28T04:11:11+0000] [ALPM] installed grep (3.12-2)
[2025-12-28T04:11:11+0000] [ALPM] installed procps-ng (4.0.5-3)
[2025-12-28T04:11:11+0000] [ALPM] installed sed (4.9-3)
[2025-12-28T04:11:11+0000] [ALPM] installed tar (1.35-2)
[2025-12-28T04:11:11+0000] [ALPM] installed gnulib-l10n (20241231-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libunistring (1.3-1)
[2025-12-28T04:11:11+0000] [ALPM] installed icu (78.1-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libxml2 (2.15.1-4)
[2025-12-28T04:11:11+0000] [ALPM] installed gettext (0.26-1)
[2025-12-28T04:11:11+0000] [ALPM] installed hwdata (0.402-1)
[2025-12-28T04:11:11+0000] [ALPM] installed kmod (34.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed pciutils (3.14.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed psmisc (23.7-1)
[2025-12-28T04:11:11+0000] [ALPM] installed shadow (4.18.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed util-linux (2.41.3-1)
[2025-12-28T04:11:11+0000] [ALPM] installed gzip (1.14-2)
[2025-12-28T04:11:11+0000] [ALPM] installed licenses (20240728-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libtasn1 (4.20.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libffi (3.5.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libp11-kit (0.25.10-2)
[2025-12-28T04:11:11+0000] [ALPM] installed p11-kit (0.25.10-2)
[2025-12-28T04:11:11+0000] [ALPM] installed ca-certificates-utils (20240618-1)
[2025-12-28T04:11:11+0000] [ALPM] installed ca-certificates-mozilla (3.119.1-1)
[2025-12-28T04:11:11+0000] [ALPM] installed ca-certificates (20240618-1)
[2025-12-28T04:11:11+0000] [ALPM] installed brotli (1.1.0-3)
[2025-12-28T04:11:11+0000] [ALPM] installed libidn2 (2.3.8-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libnghttp2 (1.68.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libnghttp3 (1.14.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libpsl (0.21.5-2)
[2025-12-28T04:11:11+0000] [ALPM] installed libssh2 (1.11.1-1)
[2025-12-28T04:11:11+0000] [ALPM] installed curl (8.17.0-2)
[2025-12-28T04:11:11+0000] [ALPM] installed nettle (3.10.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed leancrypto (1.6.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed gnutls (3.8.11-2)
[2025-12-28T04:11:11+0000] [ALPM] installed libksba (1.6.7-2)
[2025-12-28T04:11:11+0000] [ALPM] installed libusb (1.0.29-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libassuan (3.0.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libsysprof-capture (49.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed glib2 (2.86.3-1)
[2025-12-28T04:11:11+0000] [ALPM] installed json-c (0.18-2)
[2025-12-28T04:11:11+0000] [ALPM] installed tpm2-tss (4.1.3-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libsecret (0.21.7-1)
[2025-12-28T04:11:11+0000] [ALPM] installed pinentry (1.3.2-2)
[2025-12-28T04:11:11+0000] [ALPM] installed npth (1.8-1)
[2025-12-28T04:11:11+0000] [ALPM] installed gnupg (2.4.8-4)
[2025-12-28T04:11:11+0000] [ALPM] installed gpgme (2.0.1-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libarchive (3.8.4-1)
[2025-12-28T04:11:11+0000] [ALPM] installed pacman-mirrorlist (20251021-1)
[2025-12-28T04:11:11+0000] [ALPM] installed device-mapper (2.03.38-1)
[2025-12-28T04:11:11+0000] [ALPM] installed popt (1.19-2)
[2025-12-28T04:11:11+0000] [ALPM] installed cryptsetup (2.8.3-1)
[2025-12-28T04:11:11+0000] [ALPM] installed expat (2.7.3-1)
[2025-12-28T04:11:11+0000] [ALPM] installed dbus (1.16.2-1)
[2025-12-28T04:11:11+0000] [ALPM] installed dbus-broker (37-2)
[2025-12-28T04:11:11+0000] [ALPM] installed dbus-broker-units (37-2)
[2025-12-28T04:11:11+0000] [ALPM] installed dbus-units (37-2)
[2025-12-28T04:11:11+0000] [ALPM] installed kbd (2.9.0-1)
[2025-12-28T04:11:11+0000] [ALPM] installed libelf (0.194-1)
[2025-12-28T04:11:11+0000] [ALPM] installed systemd (259-1)
[2025-12-28T04:11:12+0000] [ALPM] installed jansson (2.14.1-1)
[2025-12-28T04:11:12+0000] [ALPM] installed binutils (2.45.1-1)
[2025-12-28T04:11:12+0000] [ALPM] installed libmakepkg-dropins (18-1)
[2025-12-28T04:11:12+0000] [ALPM] installed pacman (7.1.0.r7.gb9f7d4a-1)
[2025-12-28T04:11:12+0000] [ALPM] installed archlinux-keyring (20251116-1)
[2025-12-28T04:11:14+0000] [ALPM] installed systemd-sysvcompat (259-1)
[2025-12-28T04:11:14+0000] [ALPM] installed iputils (20250605-1)
[2025-12-28T04:11:14+0000] [ALPM] installed libmnl (1.0.5-2)
[2025-12-28T04:11:14+0000] [ALPM] installed libnftnl (1.3.1-1)
[2025-12-28T04:11:14+0000] [ALPM] installed libnl (3.12.0-1)
[2025-12-28T04:11:14+0000] [ALPM] installed libpcap (1.10.5-3)
[2025-12-28T04:11:14+0000] [ALPM] installed libnfnetlink (1.0.2-2)
[2025-12-28T04:11:14+0000] [ALPM] installed libnetfilter_conntrack (1.0.9-2)
[2025-12-28T04:11:15+0000] [ALPM] installed iptables (1:1.8.11-2)
[2025-12-28T04:11:15+0000] [ALPM] installed libbpf (1.6.2-1)
[2025-12-28T04:11:15+0000] [ALPM] installed iproute2 (6.18.0-1)
[2025-12-28T04:11:15+0000] [ALPM] installed base (3-2)
[2025-12-28T04:11:15+0000] [ALPM] installed m4 (1.4.20-1)
[2025-12-28T04:11:15+0000] [ALPM] installed diffutils (3.12-2)
[2025-12-28T04:11:15+0000] [ALPM] installed db5.3 (5.3.28-5)
[2025-12-28T04:11:15+0000] [ALPM] installed perl (5.42.0-1)
[2025-12-28T04:11:15+0000] [ALPM] installed autoconf (2.72-1)
[2025-12-28T04:11:15+0000] [ALPM] installed automake (1.18.1-1)
[2025-12-28T04:11:15+0000] [ALPM] installed bison (3.8.2-8)
[2025-12-28T04:11:15+0000] [ALPM] installed xxhash (0.8.3-1)
[2025-12-28T04:11:15+0000] [ALPM] installed debugedit (5.2-1)
[2025-12-28T04:11:15+0000] [ALPM] installed fakeroot (1.37.1.2-1)
[2025-12-28T04:11:15+0000] [ALPM] installed flex (2.6.4-5)
[2025-12-28T04:11:15+0000] [ALPM] installed libmpc (1.3.1-2)
[2025-12-28T04:11:15+0000] [ALPM] installed libisl (0.27-1)
[2025-12-28T04:11:15+0000] [ALPM] installed gcc (15.2.1+r301+gf24307422d1d-1)
[2025-12-28T04:11:15+0000] [ALPM] installed groff (1.23.0-7)
[2025-12-28T04:11:15+0000] [ALPM] installed libtool (2.6.0-1)
[2025-12-28T04:11:15+0000] [ALPM] installed gc (8.2.10-2)
[2025-12-28T04:11:15+0000] [ALPM] installed guile (3.0.11-1)
[2025-12-28T04:11:15+0000] [ALPM] installed make (4.4.1-2)
[2025-12-28T04:11:15+0000] [ALPM] installed patch (2.8-1)
[2025-12-28T04:11:15+0000] [ALPM] installed pkgconf (2.5.1-1)
[2025-12-28T04:11:15+0000] [ALPM] installed sudo (1.9.17.p2-1)
[2025-12-28T04:11:15+0000] [ALPM] installed texinfo (7.2-1)
[2025-12-28T04:11:15+0000] [ALPM] installed which (2.23-1)
[2025-12-28T04:11:15+0000] [ALPM] installed base-devel (1-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-whence (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-amdgpu (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-atheros (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-broadcom (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-cirrus (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-intel (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-mediatek (20251125-2)
[2025-12-28T04:11:15+0000] [ALPM] installed linux-firmware-nvidia (20251125-2)
[2025-12-28T04:11:16+0000] [ALPM] installed linux-firmware-other (20251125-2)
[2025-12-28T04:11:16+0000] [ALPM] installed linux-firmware-radeon (20251125-2)
[2025-12-28T04:11:16+0000] [ALPM] installed linux-firmware-realtek (20251125-2)
[2025-12-28T04:11:16+0000] [ALPM] installed linux-firmware (20251125-2)
[2025-12-28T04:11:16+0000] [ALPM] installed mkinitcpio-busybox (1.36.1-1)
[2025-12-28T04:11:16+0000] [ALPM] installed mkinitcpio (40-4)
[2025-12-28T04:11:16+0000] [ALPM] installed linux (6.18.2.arch2-1)
[2025-12-28T04:11:16+0000] [ALPM] installed intel-ucode (20251111-1)
[2025-12-28T04:11:42+0000] [ALPM] installed zram-generator (1.2.1-1)
[2025-12-28T04:11:43+0000] [ALPM] installed efivar (39-1)
[2025-12-28T04:11:43+0000] [ALPM] installed efibootmgr (18-3)
[2025-12-28T04:11:44+0000] [ALPM] installed sof-firmware (2025.12-1)
[2025-12-28T04:11:54+0000] [ALPM] installed libpipewire (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed pipewire (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed alsa-card-profiles (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed alsa-topology-conf (1.2.5.1-4)
[2025-12-28T04:11:55+0000] [ALPM] installed alsa-ucm-conf (1.2.14-2)
[2025-12-28T04:11:55+0000] [ALPM] installed alsa-lib (1.2.14-2)
[2025-12-28T04:11:55+0000] [ALPM] installed bluez-libs (5.85-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libebur128 (1.2.6-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libfdk-aac (2.0.3-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libfreeaptx (0.2.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed liblc3 (1.1.3-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libldac (2.0.2.3-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libmysofa (1.3.3-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libogg (1.3.6-1)
[2025-12-28T04:11:55+0000] [ALPM] installed flac (1.5.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed lame (3.100-6)
[2025-12-28T04:11:55+0000] [ALPM] installed libvorbis (1.3.7-4)
[2025-12-28T04:11:55+0000] [ALPM] installed mpg123 (1.33.4-1)
[2025-12-28T04:11:55+0000] [ALPM] installed opus (1.6-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libsndfile (1.2.2-4)
[2025-12-28T04:11:55+0000] [ALPM] installed serd (0.32.6-1)
[2025-12-28T04:11:55+0000] [ALPM] installed zix (0.8.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed sord (0.16.20-1)
[2025-12-28T04:11:55+0000] [ALPM] installed lv2 (1.18.10-2)
[2025-12-28T04:11:55+0000] [ALPM] installed sratom (0.6.20-1)
[2025-12-28T04:11:55+0000] [ALPM] installed lilv (0.26.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed sbc (2.1-1)
[2025-12-28T04:11:55+0000] [ALPM] installed gtest (1.17.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed abseil-cpp (20250814.1-1)
[2025-12-28T04:11:55+0000] [ALPM] installed webrtc-audio-processing-1 (1.3-5)
[2025-12-28T04:11:55+0000] [ALPM] installed pipewire-audio (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libwireplumber (0.5.12-1)
[2025-12-28T04:11:55+0000] [ALPM] installed lua (5.4.8-2)
[2025-12-28T04:11:55+0000] [ALPM] installed wireplumber (0.5.12-1)
[2025-12-28T04:11:55+0000] [ALPM] installed pipewire-alsa (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed pipewire-jack (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libdaemon (0.14-6)
[2025-12-28T04:11:55+0000] [ALPM] installed avahi (1:0.9rc2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed dconf (0.49.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libasyncns (1:0.8+r3+g68cd5af-3)
[2025-12-28T04:11:55+0000] [ALPM] installed xcb-proto (1.17.0-3)
[2025-12-28T04:11:55+0000] [ALPM] installed xorgproto (2025.1-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxdmcp (1.1.5-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxau (1.0.12-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxcb (1.17.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libpulse (17.0+r98+gb096704c0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed pipewire-pulse (1:1.4.9-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libunwind (1.8.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed gstreamer (1.26.10-1)
[2025-12-28T04:11:55+0000] [ALPM] installed graphene (1.10.8-2)
[2025-12-28T04:11:55+0000] [ALPM] installed iso-codes (4.19.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libpciaccess (0.18.1-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libdrm (2.4.131-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libx11 (1.8.12-2)
[2025-12-28T04:11:55+0000] [ALPM] installed libxext (1.3.6-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxshmfence (1.3.3-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxxf86vm (1.1.6-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libedit (20250104_3.1-1)
[2025-12-28T04:11:55+0000] [ALPM] installed llvm-libs (21.1.6-1)
[2025-12-28T04:11:55+0000] [ALPM] installed lm_sensors (1:3.6.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed spirv-tools (1:1.4.335.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed default-cursors (3-1)
[2025-12-28T04:11:55+0000] [ALPM] installed wayland (1.24.0-1)
[2025-12-28T04:11:55+0000] [ALPM] installed mesa (1:25.3.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libglvnd (1.7.0-3)
[2025-12-28T04:11:55+0000] [ALPM] installed libgudev (238-3)
[2025-12-28T04:11:55+0000] [ALPM] installed libjpeg-turbo (3.1.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libpng (1.6.53-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxfixes (6.0.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxi (1.8.2-1)
[2025-12-28T04:11:55+0000] [ALPM] installed libxv (1.0.13-1)
[2025-12-28T04:11:55+0000] [ALPM] installed orc (0.4.41-1)
[2025-12-28T04:11:55+0000] [ALPM] installed gst-plugins-base-libs (1.26.10-1)
[2025-12-28T04:11:55+0000] [ALPM] installed gst-plugin-pipewire (1:1.4.9-2)
[2025-12-28T04:11:57+0000] [ALPM] installed nano (8.7-1)
[2025-12-28T04:11:57+0000] [ALPM] installed vim-runtime (9.1.1975-1)
[2025-12-28T04:11:57+0000] [ALPM] installed gpm (1.20.7.r38.ge82d1a6-6)
[2025-12-28T04:11:57+0000] [ALPM] installed vim (9.1.1975-1)
[2025-12-28T04:11:57+0000] [ALPM] installed openssh (10.2p1-2)
[2025-12-28T04:11:57+0000] [ALPM] installed htop (3.4.1-1)
[2025-12-28T04:11:57+0000] [ALPM] installed wget (1.25.0-3)
[2025-12-28T04:11:57+0000] [ALPM] installed ell (0.81-1)
[2025-12-28T04:11:57+0000] [ALPM] installed iwd (3.10-1)
[2025-12-28T04:11:57+0000] [ALPM] installed wireless_tools (30.pre9-4)
[2025-12-28T04:11:57+0000] [ALPM] installed duktape (2.7.0-7)
[2025-12-28T04:11:57+0000] [ALPM] installed polkit (127-2)
[2025-12-28T04:11:57+0000] [ALPM] installed pcsclite (2.4.0-3)
[2025-12-28T04:11:57+0000] [ALPM] installed wpa_supplicant (2:2.11-3)
[2025-12-28T04:11:57+0000] [ALPM] installed smartmontools (7.5-1)
[2025-12-28T04:11:57+0000] [ALPM] installed xdg-utils (1.2.1-2)
[2025-12-28T04:12:16+0000] [ALPM] installed freetype2 (2.14.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed fontconfig (2:2.17.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libxrender (0.9.12-1)
[2025-12-28T04:12:16+0000] [ALPM] installed lzo (2.10-5)
[2025-12-28T04:12:16+0000] [ALPM] installed pixman (0.46.4-1)
[2025-12-28T04:12:16+0000] [ALPM] installed cairo (1.18.4-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gsettings-system-schemas (49.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed adwaita-fonts (49.0-2)
[2025-12-28T04:12:16+0000] [ALPM] installed gsettings-desktop-schemas (49.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed hicolor-icon-theme (0.18-1)
[2025-12-28T04:12:16+0000] [ALPM] installed adwaita-icon-theme-legacy (46.2-3)
[2025-12-28T04:12:16+0000] [ALPM] installed adwaita-cursors (49.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed adwaita-icon-theme (49.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libxtst (1.2.5-1)
[2025-12-28T04:12:16+0000] [ALPM] installed xorg-xprop (1.2.8-1)
[2025-12-28T04:12:16+0000] [ALPM] installed at-spi2-core (2.58.2-1)
[2025-12-28T04:12:16+0000] [ALPM] installed desktop-file-utils (0.28-1)
[2025-12-28T04:12:16+0000] [ALPM] installed fribidi (1.0.16-2)
[2025-12-28T04:12:16+0000] [ALPM] installed bubblewrap (0.11.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed jbigkit (2.1-8)
[2025-12-28T04:12:16+0000] [ALPM] installed libdeflate (1.25-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libwebp (1.6.0-2)
[2025-12-28T04:12:16+0000] [ALPM] installed libtiff (4.7.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed lcms2 (2.17-1)
[2025-12-28T04:12:16+0000] [ALPM] installed giflib (5.2.2-2)
[2025-12-28T04:12:16+0000] [ALPM] installed gperftools (2.17.2-1)
[2025-12-28T04:12:16+0000] [ALPM] installed highway (1.3.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libjxl (0.11.1-5)
[2025-12-28T04:12:16+0000] [ALPM] installed dav1d (1.5.2-1)
[2025-12-28T04:12:16+0000] [ALPM] installed graphite (1:1.3.14-5)
[2025-12-28T04:12:16+0000] [ALPM] installed harfbuzz (12.3.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libdatrie (0.2.14-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libthai (0.1.29-3)
[2025-12-28T04:12:16+0000] [ALPM] installed libxft (2.3.9-1)
[2025-12-28T04:12:16+0000] [ALPM] installed pango (1:1.57.0-2)
[2025-12-28T04:12:16+0000] [ALPM] installed librsvg (2:2.61.3-1)
[2025-12-28T04:12:16+0000] [ALPM] installed glycin (2.0.7-1)
[2025-12-28T04:12:16+0000] [ALPM] installed shared-mime-info (2.4-2)
[2025-12-28T04:12:16+0000] [ALPM] installed gdk-pixbuf2 (2.44.4-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libproxy (0.5.12-1)
[2025-12-28T04:12:16+0000] [ALPM] installed glib-networking (1:2.80.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libsoup3 (3.6.5-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gssdp (1.6.4-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gupnp (1:1.6.9-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gupnp-igd (1.6.0-2)
[2025-12-28T04:12:16+0000] [ALPM] installed libnice (0.1.23-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libva (2.22.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed xkeyboard-config (2.46-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libxkbcommon (1.13.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libxkbcommon-x11 (1.13.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed vulkan-icd-loader (1.4.335.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gst-plugins-bad-libs (1.26.10-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gtk-update-icon-cache (1:4.20.3-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libcloudproviders (0.3.6-2)
[2025-12-28T04:12:16+0000] [ALPM] installed libcolord (1.4.8-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libcups (2:2.4.16-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libepoxy (1.5.10-3)
[2025-12-28T04:12:16+0000] [ALPM] installed libxcursor (1.2.3-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libxdamage (1.1.6-2)
[2025-12-28T04:12:16+0000] [ALPM] installed libxinerama (1.1.5-2)
[2025-12-28T04:12:16+0000] [ALPM] installed libxrandr (1.5.4-1)
[2025-12-28T04:12:16+0000] [ALPM] installed json-glib (1.10.8-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libstemmer (3.0.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed tinysparql (3.10.1-2)
[2025-12-28T04:12:16+0000] [ALPM] installed gtk4 (1:4.20.3-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libfyaml (0.9-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libxmlb (0.3.24-1)
[2025-12-28T04:12:16+0000] [ALPM] installed appstream (1.1.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libadwaita (1:1.8.2-1)
[2025-12-28T04:12:16+0000] [ALPM] installed baobab (49.1-1)
[2025-12-28T04:12:16+0000] [ALPM] installed libgirepository (1.86.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gobject-introspection-runtime (1.86.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed js140 (140.6.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gjs (2:1.86.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed cdparanoia (10.2-9)
[2025-12-28T04:12:16+0000] [ALPM] installed libtheora (1.2.0-1)
[2025-12-28T04:12:16+0000] [ALPM] installed gst-plugins-base (1.26.10-1)
[2025-12-28T04:12:16+0000] [ALPM] installed pcre (8.45-4)
[2025-12-28T04:12:16+0000] [ALPM] installed slang (2.3.3-4)
[2025-12-28T04:12:16+0000] [ALPM] installed aalib (1.4rc5-19)
[2025-12-28T04:12:16+0000] [ALPM] installed libraw1394 (2.1.2-4)
[2025-12-28T04:12:16+0000] [ALPM] installed libavc1394 (0.5.4-7)
[2025-12-28T04:12:16+0000] [ALPM] installed glu (9.0.3-2)
[2025-12-28T04:12:16+0000] [ALPM] installed freeglut (3.8.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed imlib2 (1.12.5-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libcaca (0.99.beta20-5)
[2025-12-28T04:12:17+0000] [ALPM] installed libdv (1.0.0-11)
[2025-12-28T04:12:17+0000] [ALPM] installed libiec61883 (1.2.0-9)
[2025-12-28T04:12:17+0000] [ALPM] installed speexdsp (1.2.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed speex (1.2.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libshout (1:2.4.6-5)
[2025-12-28T04:12:17+0000] [ALPM] installed libvpx (1.15.2-2)
[2025-12-28T04:12:17+0000] [ALPM] installed opencore-amr (0.1.6-2)
[2025-12-28T04:12:17+0000] [ALPM] installed taglib (2.1.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed twolame (0.4.0-4)
[2025-12-28T04:12:17+0000] [ALPM] installed v4l-utils (1.32.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed wavpack (5.8.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gst-plugins-good (1.26.10-1)
[2025-12-28T04:12:17+0000] [ALPM] installed decibels (49.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gcr-4 (4.4.0.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libportal (0.9.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libportal-gtk4 (0.9.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed enchant (2.8.14-1)
[2025-12-28T04:12:17+0000] [ALPM] installed harfbuzz-icu (12.3.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed hyphen (2.8.8-6)
[2025-12-28T04:12:17+0000] [ALPM] installed aom (3.13.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libyuv (r2426+464c51a03-1)
[2025-12-28T04:12:17+0000] [ALPM] installed rav1e (0.8.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed svt-av1 (3.1.2-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libavif (1.3.0-3)
[2025-12-28T04:12:17+0000] [ALPM] installed hidapi (0.15.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libevdev (1.13.6-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libmanette (0.2.13-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libxslt (1.1.45-1)
[2025-12-28T04:12:17+0000] [ALPM] installed openjpeg2 (2.5.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gnu-free-fonts (20120503-8)
[2025-12-28T04:12:17+0000] [ALPM] installed woff2 (1.0.2-6)
[2025-12-28T04:12:17+0000] [ALPM] installed xdg-dbus-proxy (0.1.6-1)
[2025-12-28T04:12:17+0000] [ALPM] installed webkitgtk-6.0 (2.50.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed epiphany (49.2-1)
[2025-12-28T04:12:17+0000] [ALPM] installed accountsservice (23.13.9-2)
[2025-12-28T04:12:17+0000] [ALPM] installed gnome-desktop-common (1:44.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gnome-desktop-4 (1:44.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libxcomposite (0.4.6-2)
[2025-12-28T04:12:17+0000] [ALPM] installed gtk3 (1:3.24.51-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gnome-autoar (0.4.5-1)
[2025-12-28T04:12:17+0000] [ALPM] installed fuse-common (3.17.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed fuse3 (3.17.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libbluray (1.4.0-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libcdio (2.3.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libcdio-paranoia (10.2+2.0.2-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed nspr (4.38.2-1)
[2025-12-28T04:12:17+0000] [ALPM] installed nss (3.119.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed volume_key (0.3.12-11)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-crypto (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libbytesize (2.11-1)
[2025-12-28T04:12:17+0000] [ALPM] installed parted (3.6-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-fs (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed mdadm (4.4-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-mdraid (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-loop (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed liburing (2.13-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libnvme (1.16.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-nvme (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-part (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libatasmart (0.19-7)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-smart (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libblockdev-swap (3.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed udisks2 (2.11.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gvfs (1.58.0-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libinih (61-1)
[2025-12-28T04:12:17+0000] [ALPM] installed exiv2 (0.28.7-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libgexiv2 (0.14.6-1)
[2025-12-28T04:12:17+0000] [ALPM] installed exempi (2.6.6-2)
[2025-12-28T04:12:17+0000] [ALPM] installed glslang (1:1.4.335.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gsm (1.0.23-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libunibreak (6.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libass (0.17.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libbs2b (3.1.0-9)
[2025-12-28T04:12:17+0000] [ALPM] installed libdvdread (7.0.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libdvdnav (7.0.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libmodplug (0.8.9.0-6)
[2025-12-28T04:12:17+0000] [ALPM] installed portaudio (1:19.7.0-3)
[2025-12-28T04:12:17+0000] [ALPM] installed libopenmpt (0.8.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed shaderc (2025.5-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libdovi (3.3.2-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libplacebo (7.351.0-4)
[2025-12-28T04:12:17+0000] [ALPM] installed libsoxr (0.1.3-4)
[2025-12-28T04:12:17+0000] [ALPM] installed libssh (0.11.3-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libvdpau (1.5-3)
[2025-12-28T04:12:17+0000] [ALPM] installed ocl-icd (2.3.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libvpl (2.16.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed fftw (3.3.10-7)
[2025-12-28T04:12:17+0000] [ALPM] installed libsamplerate (0.2.2-3)
[2025-12-28T04:12:17+0000] [ALPM] installed rubberband (4.0.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed sdl3 (3.2.28-1)
[2025-12-28T04:12:17+0000] [ALPM] installed sdl2-compat (2.32.60-1)
[2025-12-28T04:12:17+0000] [ALPM] installed snappy (1.2.2-2)
[2025-12-28T04:12:17+0000] [ALPM] installed srt (1.5.4-1)
[2025-12-28T04:12:17+0000] [ALPM] installed zimg (3.0.6-1)
[2025-12-28T04:12:17+0000] [ALPM] installed mpdecimal (4.0.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed python (3.13.11-1)
[2025-12-28T04:12:17+0000] [ALPM] installed vapoursynth (73-1)
[2025-12-28T04:12:17+0000] [ALPM] installed vid.stab (1.1.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed vmaf (3.0.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed l-smash (2.14.5-4)
[2025-12-28T04:12:17+0000] [ALPM] installed x264 (3:0.165.r3222.b35605a-2)
[2025-12-28T04:12:17+0000] [ALPM] installed x265 (4.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed xvidcore (1.3.7-3)
[2025-12-28T04:12:17+0000] [ALPM] installed libsodium (1.0.20-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libpgm (5.3.128-3)
[2025-12-28T04:12:17+0000] [ALPM] installed zeromq (4.3.5-2)
[2025-12-28T04:12:17+0000] [ALPM] installed ffmpeg (2:8.0.1-2)
[2025-12-28T04:12:17+0000] [ALPM] installed gexiv2 (0.16.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed gupnp-dlna (0.12.0-4)
[2025-12-28T04:12:17+0000] [ALPM] installed libcue (2.3.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libexif (0.6.25-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libgsf (1.14.54-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libgxps (0.3.2-5)
[2025-12-28T04:12:17+0000] [ALPM] installed libiptcdata (1.0.5-4)
[2025-12-28T04:12:17+0000] [ALPM] installed osinfo-db (20251212-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libosinfo (1.12.0-2)
[2025-12-28T04:12:17+0000] [ALPM] installed gpgmepp (2.0.0-2)
[2025-12-28T04:12:17+0000] [ALPM] installed poppler (25.12.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed poppler-glib (25.12.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed uchardet (0.0.8-3)
[2025-12-28T04:12:17+0000] [ALPM] installed totem-pl-parser (3.26.6+r30+g51b8439-2)
[2025-12-28T04:12:17+0000] [ALPM] installed libplist (2.7.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libimobiledevice-glue (1.3.2-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libtatsu (1.0.5-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libusbmuxd (2.1.1-1)
[2025-12-28T04:12:17+0000] [ALPM] installed libimobiledevice (1.4.0-1)
[2025-12-28T04:12:17+0000] [ALPM] installed upower (1.91.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed localsearch (3.10.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xdg-user-dirs (0.19-2)
[2025-12-28T04:12:18+0000] [ALPM] installed xdg-user-dirs-gtk (0.16-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libnautilus-extension (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed nautilus (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed rtkit (0.14-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xdg-desktop-portal (1.20.3-2)
[2025-12-28T04:12:18+0000] [ALPM] installed xdg-desktop-portal-gtk (1.15.3-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xdg-desktop-portal-gnome (49.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-session (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libmm-glib (1.24.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed geoclue (2.8.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed geocode-glib-common (3.26.4-4)
[2025-12-28T04:12:18+0000] [ALPM] installed geocode-glib-2 (3.26.4-4)
[2025-12-28T04:12:18+0000] [ALPM] installed tdb (1.4.14-1)
[2025-12-28T04:12:18+0000] [ALPM] installed sound-theme-freedesktop (0.8-6)
[2025-12-28T04:12:18+0000] [ALPM] installed libcanberra (1:0.30+r2+gc0620e4-6)
[2025-12-28T04:12:18+0000] [ALPM] installed libgweather-4 (4.4.4-3)
[2025-12-28T04:12:18+0000] [ALPM] installed libnm (1.54.3-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libnotify (0.8.7-2)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-settings-daemon (49.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libdbusmenu-glib (18.10.20180917-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libdbusmenu-gtk3 (18.10.20180917-1)
[2025-12-28T04:12:18+0000] [ALPM] installed python-gobject (3.54.5-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libibus (1.5.33-1)
[2025-12-28T04:12:18+0000] [ALPM] installed ibus (1.5.33-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libgdm (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libical (3.0.20-3)
[2025-12-28T04:12:18+0000] [ALPM] installed mobile-broadband-provider-info (20251101-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libnma-common (1.10.6-3)
[2025-12-28T04:12:18+0000] [ALPM] installed libnma-gtk4 (1.10.6-3)
[2025-12-28T04:12:18+0000] [ALPM] installed libgusb (0.4.9-2)
[2025-12-28T04:12:18+0000] [ALPM] installed colord (1.4.8-1)
[2025-12-28T04:12:18+0000] [ALPM] installed eglexternalplatform (1.2.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed egl-wayland (4:1.1.21-1)
[2025-12-28T04:12:18+0000] [ALPM] installed iio-sensor-proxy (3.8-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libdisplay-info (0.3.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libei (1.5.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libice (1.1.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libwacom (2.17.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed mtdev (1.1.7-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libinput (1.30.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libsm (1.2.6-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libxkbfile (1.1.3-1)
[2025-12-28T04:12:18+0000] [ALPM] installed python-argcomplete (3.6.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed python-dbus (1.4.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xcb-util (0.4.1-2)
[2025-12-28T04:12:18+0000] [ALPM] installed startup-notification (0.12-9)
[2025-12-28T04:12:18+0000] [ALPM] installed xorg-fonts-encodings (1.1.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libfontenc (1.1.8-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libxfont2 (2.0.7-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xorg-xkbcomp (1.5.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xorg-setxkbmap (1.3.4-2)
[2025-12-28T04:12:18+0000] [ALPM] installed xorg-server-common (21.1.21-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libxcvt (0.1.3-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libdecor (0.2.5-1)
[2025-12-28T04:12:18+0000] [ALPM] installed xorg-xwayland (24.1.9-1)
[2025-12-28T04:12:18+0000] [ALPM] installed mutter (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed unzip (6.0-23)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-shell (1:49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gdm (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-backgrounds (49.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gtksourceview5 (5.18.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libgee (0.20.8-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-calculator (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libgoa (3.56.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed protobuf (33.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libphonenumber (1:9.0.21-1)
[2025-12-28T04:12:18+0000] [ALPM] installed webkit2gtk-4.1 (2.50.4-1)
[2025-12-28T04:12:18+0000] [ALPM] installed evolution-data-server (3.58.2-2)
[2025-12-28T04:12:18+0000] [ALPM] installed libedataserverui4 (3.58.2-2)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-calendar (49.0.1-2)
[2025-12-28T04:12:18+0000] [ALPM] installed noto-fonts-emoji (1:2.051-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-characters (49.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-clocks (49.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-color-manager (3.36.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed sdl3_ttf (3.2.2-3)
[2025-12-28T04:12:18+0000] [ALPM] installed freerdp (2:3.19.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gtk-vnc (1.5.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libhandy (1.8.3-2)
[2025-12-28T04:12:18+0000] [ALPM] installed libcacard (2.8.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed phodav (3.0-4)
[2025-12-28T04:12:18+0000] [ALPM] installed spice-protocol (0.14.5-1)
[2025-12-28T04:12:18+0000] [ALPM] installed usbredir (0.15.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed spice-gtk (0.42-5)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-connections (49.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libgtop (2.41.3-2)
[2025-12-28T04:12:18+0000] [ALPM] installed vte-common (0.82.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed vte4 (0.82.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-console (49.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed folks (0.15.9-2)
[2025-12-28T04:12:18+0000] [ALPM] installed librest (0.10.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-online-accounts (3.56.2-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gst-plugin-gtk4 (0.14.4-1)
[2025-12-28T04:12:18+0000] [ALPM] installed qrencode (4.1.1-4)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-contacts (49.0-1)
[2025-12-28T04:12:18+0000] [ALPM] installed bolt (0.9.10-1)
[2025-12-28T04:12:18+0000] [ALPM] installed colord-gtk-common (0.3.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed colord-gtk4 (0.3.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed cups-pk-helper (0.2.7-2)
[2025-12-28T04:12:18+0000] [ALPM] installed bluez (5.85-1)
[2025-12-28T04:12:18+0000] [ALPM] installed bluez-obex (5.85-1)
[2025-12-28T04:12:18+0000] [ALPM] installed gsound (1.0.3-3)
[2025-12-28T04:12:18+0000] [ALPM] installed gnome-bluetooth-3.0 (47.1-2)
[2025-12-28T04:12:18+0000] [ALPM] installed libmalcontent (0.13.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed cracklib (2.10.3-1)
[2025-12-28T04:12:18+0000] [ALPM] installed libpwquality (1.4.5-6)
[2025-12-28T04:12:18+0000] [ALPM] installed libmd (1.1.0-2)
[2025-12-28T04:12:18+0000] [ALPM] installed libbsd (0.12.2-2)
[2025-12-28T04:12:18+0000] [ALPM] installed libwbclient (2:4.23.4-1)
[2025-12-28T04:12:18+0000] [ALPM] installed talloc (2.4.3-1)
[2025-12-28T04:12:18+0000] [ALPM] installed cifs-utils (7.4-1)
[2025-12-28T04:12:18+0000] [ALPM] installed tevent (1:0.17.1-1)
[2025-12-28T04:12:18+0000] [ALPM] installed ldb (2:4.23.4-1)
[2025-12-28T04:12:19+0000] [ALPM] installed smbclient (2:4.23.4-1)
[2025-12-28T04:12:19+0000] [ALPM] installed tecla (49.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-keybindings (49.2.2-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-control-center (49.2.2-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-disk-utility (46.1-2)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-font-viewer (49.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gcr (3.41.2-2)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-keyring (1:48.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-logs (49.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed protobuf-c (1.5.2-8)
[2025-12-28T04:12:19+0000] [ALPM] installed libshumate (1.5.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-maps (49.3-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-menus (3.38.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed grilo (0.3.19-1)
[2025-12-28T04:12:19+0000] [ALPM] installed chromaprint (1.6.0-2)
[2025-12-28T04:12:19+0000] [ALPM] installed gom (0.5.5-1)
[2025-12-28T04:12:19+0000] [ALPM] installed faac (1.31.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed faad2 (2.11.2-1)
[2025-12-28T04:12:19+0000] [ALPM] installed fluidsynth (2.5.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed imath (3.2.2-2)
[2025-12-28T04:12:19+0000] [ALPM] installed libavtp (0.2.0-3)
[2025-12-28T04:12:19+0000] [ALPM] installed libdc1394 (2.2.7-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libdca (0.0.7-2)
[2025-12-28T04:12:19+0000] [ALPM] installed libde265 (1.0.16-2)
[2025-12-28T04:12:19+0000] [ALPM] installed libgme (0.6.4-1)
[2025-12-28T04:12:19+0000] [ALPM] installed raptor (2.0.16-9)
[2025-12-28T04:12:19+0000] [ALPM] installed liblrdf (0.6.1-5)
[2025-12-28T04:12:19+0000] [ALPM] installed libltc (1.3.2-2)
[2025-12-28T04:12:19+0000] [ALPM] installed libmicrodns (0.2.0-2)
[2025-12-28T04:12:19+0000] [ALPM] installed libmpcdec (1:0.1+r475-6)
[2025-12-28T04:12:19+0000] [ALPM] installed libsrtp (1:2.7.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed mjpegtools (2.2.1-3)
[2025-12-28T04:12:19+0000] [ALPM] installed neon (0.36.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed openal (1.25.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed openexr (3.4.4-1)
[2025-12-28T04:12:19+0000] [ALPM] installed openh264 (2.6.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed rtmpdump (1:2.6-1)
[2025-12-28T04:12:19+0000] [ALPM] installed soundtouch (2.4.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed spandsp (0.0.6-6)
[2025-12-28T04:12:19+0000] [ALPM] installed svt-hevc (1.5.1-3)
[2025-12-28T04:12:19+0000] [ALPM] installed wildmidi (0.4.6-1)
[2025-12-28T04:12:19+0000] [ALPM] installed liblqr (0.4.3-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libraqm (0.10.3-1)
[2025-12-28T04:12:19+0000] [ALPM] installed imagemagick (7.1.2.11-1)
[2025-12-28T04:12:19+0000] [ALPM] installed zbar (0.23.93-4)
[2025-12-28T04:12:19+0000] [ALPM] installed zvbi (0.2.44-1)
[2025-12-28T04:12:19+0000] [ALPM] installed zxing-cpp (2.3.0-5)
[2025-12-28T04:12:19+0000] [ALPM] installed gst-plugins-bad (1.26.10-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libdmapsharing (3.9.13-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libmediaart (1.9.7-1)
[2025-12-28T04:12:19+0000] [ALPM] installed liboauth (1:1.0.3+r16+gc26f038-2)
[2025-12-28T04:12:19+0000] [ALPM] installed grilo-plugins (1:0.3.18-1)
[2025-12-28T04:12:19+0000] [ALPM] installed python-cairo (1.29.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-music (1:49.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libvncserver (0.9.14-4)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-remote-desktop (49.2-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-app-list (3.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-software (49.2-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libsigc++-3.0 (3.8.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed glibmm-2.68 (2.86.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed cairomm-1.16 (1.18.0-2)
[2025-12-28T04:12:19+0000] [ALPM] installed pangomm-2.48 (2.56.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gtkmm-4.0 (4.20.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-system-monitor (49.1-1)
[2025-12-28T04:12:19+0000] [ALPM] installed editorconfig-core-c (0.12.10-1)
[2025-12-28T04:12:19+0000] [ALPM] installed libspelling (0.4.9-2)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-text-editor (49.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed gnome-tour (49.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed yelp-xsl (49.0-1)
[2025-12-28T04:12:19+0000] [ALPM] installed yelp (49.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gnome-user-docs (49.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed apr (1.7.6-1)
[2025-12-28T04:12:20+0000] [ALPM] installed apr-util (1.6.3-2)
[2025-12-28T04:12:20+0000] [ALPM] installed apache (2.4.66-1)
[2025-12-28T04:12:20+0000] [ALPM] installed mod_dnssd (0.6-9)
[2025-12-28T04:12:20+0000] [ALPM] installed gnome-user-share (48.2-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gnome-weather (49.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed usbmuxd (1.1.1-4)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-afc (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-dnssd (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-goa (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed libsoup (2.74.3-4)
[2025-12-28T04:12:20+0000] [ALPM] installed libgdata (0.18.1-4)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-google (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed libxt (1.3.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libxpm (3.5.17-2)
[2025-12-28T04:12:20+0000] [ALPM] installed libheif (1.20.2-3)
[2025-12-28T04:12:20+0000] [ALPM] installed gd (2.3.3-9)
[2025-12-28T04:12:20+0000] [ALPM] installed libgphoto2 (2.5.33-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-gphoto2 (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed libmtp (1.1.22-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-mtp (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed libnfs (6.0.2-5)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-nfs (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed msgraph (0.3.3-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-onedrive (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-smb (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed python-defusedxml (0.7.1-7)
[2025-12-28T04:12:20+0000] [ALPM] installed python-systemd (235-4)
[2025-12-28T04:12:20+0000] [ALPM] installed wsdd (0.9-2)
[2025-12-28T04:12:20+0000] [ALPM] installed gvfs-wsdd (1.58.0-2)
[2025-12-28T04:12:20+0000] [ALPM] installed loupe (49.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed composefs (1.0.8-1)
[2025-12-28T04:12:20+0000] [ALPM] installed ostree (2025.7-1)
[2025-12-28T04:12:20+0000] [ALPM] installed flatpak (1:1.16.2-1)
[2025-12-28T04:12:20+0000] [ALPM] installed malcontent (0.13.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libyaml (0.2.5-3)
[2025-12-28T04:12:20+0000] [ALPM] installed liblouis (3.36.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libspeechd (0.12.1-2)
[2025-12-28T04:12:20+0000] [ALPM] installed brltty (6.8-5)
[2025-12-28T04:12:20+0000] [ALPM] installed libxres (1.2.3-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libwnck3 (43.3-1)
[2025-12-28T04:12:20+0000] [ALPM] installed python-dasbus (1.7-4)
[2025-12-28T04:12:20+0000] [ALPM] installed python-psutil (7.1.3-1)
[2025-12-28T04:12:20+0000] [ALPM] installed python-setproctitle (1.3.7-1)
[2025-12-28T04:12:20+0000] [ALPM] installed python-pyxdg (0.28-4)
[2025-12-28T04:12:20+0000] [ALPM] installed dotconf (1.4.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libao (1.2.2-7)
[2025-12-28T04:12:20+0000] [ALPM] installed speech-dispatcher (0.12.1-2)
[2025-12-28T04:12:20+0000] [ALPM] installed xorg-xmodmap (1.0.11-2)
[2025-12-28T04:12:20+0000] [ALPM] installed orca (49.5-1)
[2025-12-28T04:12:20+0000] [ALPM] installed djvulibre (3.5.29-1)
[2025-12-28T04:12:20+0000] [ALPM] installed papers (49.2-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gst-devtools-libs (1.26.10-1)
[2025-12-28T04:12:20+0000] [ALPM] installed python-typing_extensions (4.15.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gst-python (1.26.10-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gst-editing-services (1.26.10-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gupnp-av (0.14.4-1)
[2025-12-28T04:12:20+0000] [ALPM] installed rygel (1:45.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed showtime (49.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libieee1284 (0.2.11-18)
[2025-12-28T04:12:20+0000] [ALPM] installed net-snmp (5.9.4-7)
[2025-12-28T04:12:20+0000] [ALPM] installed sane (1.4.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed colord-sane (1.4.8-1)
[2025-12-28T04:12:20+0000] [ALPM] installed simple-scan (49.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed snapshot (49.1-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gnome-desktop (1:44.4-1)
[2025-12-28T04:12:20+0000] [ALPM] installed gsfonts (20200910-6)
[2025-12-28T04:12:20+0000] [ALPM] installed gspell (1.14.2-1)
[2025-12-28T04:12:20+0000] [ALPM] installed jbig2dec (0.20-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libpaper (2.2.7-1)
[2025-12-28T04:12:20+0000] [ALPM] installed ijs (0.35-6)
[2025-12-28T04:12:20+0000] [ALPM] installed libidn (1.43-1)
[2025-12-28T04:12:20+0000] [ALPM] installed poppler-data (0.4.12-2)
[2025-12-28T04:12:20+0000] [ALPM] installed ghostscript (10.06.0-1)
[2025-12-28T04:12:20+0000] [ALPM] installed libspectre (0.2.12-2)
[2025-12-28T04:12:20+0000] [ALPM] installed libsynctex (2025.2-3)
[2025-12-28T04:12:21+0000] [ALPM] installed evince (1:48.1-1)
[2025-12-28T04:12:21+0000] [ALPM] installed gst-plugin-gtk (1.26.10-1)
[2025-12-28T04:12:21+0000] [ALPM] installed gtksourceview4 (4.8.4-2)
[2025-12-28T04:12:21+0000] [ALPM] installed sushi (46.0-2)
[2025-12-28T04:12:21+0000] [ALPM] installed gnome-tweaks (49.0-1)
[2025-12-28T04:12:31+0000] [ALPM] installed pahole (1:1.31-1)
[2025-12-28T04:12:32+0000] [ALPM] installed linux-headers (6.18.2.arch2-1)
[2025-12-28T04:12:40+0000] [ALPM] installed xf86-input-libinput (1.5.0-1)
[2025-12-28T04:12:40+0000] [ALPM] installed egl-wayland2 (1.0.0.rc.r51.gada1c37-1)
[2025-12-28T04:12:40+0000] [ALPM] installed egl-gbm (1.1.2.1-1)
[2025-12-28T04:12:40+0000] [ALPM] installed egl-x11 (1.0.4-1)
[2025-12-28T04:12:41+0000] [ALPM] installed nvidia-utils (590.48.01-1)
[2025-12-28T04:12:41+0000] [ALPM] installed xorg-server (21.1.21-1)
[2025-12-28T04:12:41+0000] [ALPM] installed libxmu (1.2.1-1)
[2025-12-28T04:12:41+0000] [ALPM] installed xorg-xauth (1.1.4-1)
[2025-12-28T04:12:41+0000] [ALPM] installed xorg-xrdb (1.2.2-2)
[2025-12-28T04:12:41+0000] [ALPM] installed xorg-xinit (1.4.4-1)
[2025-12-28T04:12:41+0000] [ALPM] installed dkms (3.3.0-1)
[2025-12-28T04:12:41+0000] [ALPM] installed nvidia-open-dkms (590.48.01-1)
[2025-12-28T04:12:41+0000] [ALPM] installed libva-nvidia-driver (0.0.14-1)
[2025-12-27T20:43:29-0800] [ALPM] installed libndp (1.9-1)
[2025-12-27T20:43:29-0800] [ALPM] installed libnewt (0.52.25-1)
[2025-12-27T20:43:29-0800] [ALPM] installed libteam (1.32-3)
[2025-12-27T20:43:29-0800] [ALPM] installed networkmanager (1.54.3-1)
[2025-12-27T20:45:05-0800] [ALPM] installed libxss (1.2.5-1)
[2025-12-27T20:45:05-0800] [ALPM] installed mailcap (2.1.54-2)
[2025-12-27T20:45:06-0800] [ALPM] installed firefox (146.0.1-1)
[2025-12-27T20:47:27-0800] [ALPM] installed c-ares (1.34.6-1)
[2025-12-27T20:47:27-0800] [ALPM] installed minizip (1:1.3.1-2)
[2025-12-27T20:47:27-0800] [ALPM] installed electron39 (39.2.7-1)
[2025-12-27T20:47:27-0800] [ALPM] installed ripgrep (15.1.0-1)
[2025-12-27T20:47:28-0800] [ALPM] installed code (1.107.0-1)
[2025-12-27T20:48:25-0800] [ALPM] installed ayatana-ido (0.10.4-1)
[2025-12-27T20:48:25-0800] [ALPM] installed libayatana-indicator (0.9.4-1)
[2025-12-27T20:48:25-0800] [ALPM] installed libayatana-appindicator (0.5.94-1)
[2025-12-27T20:48:25-0800] [ALPM] installed libcurl-gnutls (8.17.0-2)
[2025-12-27T20:48:25-0800] [ALPM] installed sequoia-sqv (1.3.0-1)
[2025-12-27T20:48:25-0800] [ALPM] installed zenity (4.2.1-1)
[2025-12-27T20:48:25-0800] [ALPM] installed spotify-launcher (0.6.3-2)
[2025-12-27T20:49:19-0800] [ALPM] installed zsh (5.9-5)
[2025-12-27T20:49:19-0800] [ALPM] installed zsh-autosuggestions (0.7.1-1)
[2025-12-27T20:49:19-0800] [ALPM] installed zsh-syntax-highlighting (0.8.0-1)
[2025-12-27T20:50:02-0800] [ALPM] installed perl-error (0.17030-3)
[2025-12-27T20:50:02-0800] [ALPM] installed perl-timedate (2.33-9)
[2025-12-27T20:50:02-0800] [ALPM] installed perl-mailtools (2.22-3)
[2025-12-27T20:50:02-0800] [ALPM] installed zlib-ng (2.3.2-1)
[2025-12-27T20:50:02-0800] [ALPM] installed git (2.52.0-2)
[2025-12-27T20:50:27-0800] [ALPM] installed xclip (0.13-6)
[2025-12-27T20:52:04-0800] [ALPM] installed libuv (1.51.0-1)
[2025-12-27T20:52:04-0800] [ALPM] installed luajit (2.1.1765228720+7152e15-1)
[2025-12-27T20:52:04-0800] [ALPM] installed libluv (1.51.0-1)
[2025-12-27T20:52:04-0800] [ALPM] installed libutf8proc (2.10.0-2)
[2025-12-27T20:52:04-0800] [ALPM] installed libvterm (0.3.3-2)
[2025-12-27T20:52:04-0800] [ALPM] installed lua51-lpeg (1.1.0-4)
[2025-12-27T20:52:04-0800] [ALPM] installed msgpack-c (6.1.0-2)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter (0.25.10-1)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter-c (0.24.1-1)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter-lua (0.4.0-1)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter-markdown (0.5.1-1)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter-query (0.7.0-1)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter-vim (0.7.0-1)
[2025-12-27T20:52:04-0800] [ALPM] installed tree-sitter-vimdoc (4.0.0-1)
[2025-12-27T20:52:04-0800] [ALPM] installed unibilium (2.1.2-1)
[2025-12-27T20:52:04-0800] [ALPM] installed neovim (0.11.5-1)
[2025-12-27T20:52:04-0800] [ALPM] installed lshw (B.02.20-1)
[2025-12-27T20:52:04-0800] [ALPM] installed dmidecode (3.7-1)
[2025-12-27T20:52:24-0800] [ALPM] installed go (2:1.25.5-1)
[2025-12-27T20:52:32-0800] [ALPM] installed kubectl (1.34.3-1)
[2025-12-27T20:52:36-0800] [ALPM] installed terraform (1.14.3-1)
[2025-12-27T20:52:41-0800] [ALPM] installed nftables (1:1.1.6-1)
[2025-12-27T20:52:41-0800] [ALPM] installed runc (1.4.0-1)
[2025-12-27T20:52:41-0800] [ALPM] installed containerd (2.2.1-1)
[2025-12-27T20:52:41-0800] [ALPM] installed docker (1:29.1.3-1)
[2025-12-27T20:52:41-0800] [ALPM] installed docker-compose (5.0.1-1)
[2025-12-27T20:55:44-0800] [ALPM] installed libxcrypt-compat (4.5.2-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lsb-release (2.0.r55.a25a4fc-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lsof (4.99.5-2)
[2025-12-27T20:55:44-0800] [ALPM] installed usbutils (019-1)
[2025-12-27T20:55:44-0800] [ALPM] installed xorg-xrandr (1.5.3-1)
[2025-12-27T20:55:44-0800] [ALPM] installed alsa-plugins (1:1.2.12-5)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-glibc (2.42+r33+gde1fe81f4714-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-gcc-libs (15.2.1+r301+gf24307422d1d-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-alsa-lib (1.2.14-2)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-alsa-plugins (1.2.12-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-expat (2.7.3-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-brotli (1.1.0-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-bzip2 (1.0.8-4)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-zlib (1.3.1-2)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-libpng (1.6.53-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-freetype2 (2.14.1-1)
[2025-12-27T20:55:44-0800] [ALPM] installed lib32-fontconfig (2:2.17.1-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxdmcp (1.1.5-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxau (1.0.12-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxcb (1.17.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libx11 (1.8.12-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxext (1.3.6-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libpciaccess (0.18.1-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libdrm (2.4.128-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-e2fsprogs (1.47.3-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-keyutils (1.6.3-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-openssl (1:3.6.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxcrypt (4.5.2-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libldap (2.6.10-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-krb5 (1.21.3-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libunistring (1.3-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libidn2 (2.3.8-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libnghttp2 (1.68.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libnghttp3 (1.14.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libpsl (0.21.5-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libssh2 (1.11.1-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-zstd (1.5.7-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-curl (8.17.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-json-c (0.18-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-xz (5.8.2-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libelf (0.194-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxshmfence (1.3.3-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxxf86vm (1.1.5-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libffi (3.5.2-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-ncurses (6.5-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-icu (78.1-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-libxml2 (2.15.1-4)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-llvm-libs (1:21.1.6-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-lm_sensors (1:3.6.2-2)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-spirv-tools (1:1.4.335.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-wayland (1.24.0-1)
[2025-12-27T20:55:46-0800] [ALPM] installed lib32-mesa (1:25.3.2-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-nvidia-utils (590.48.01-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libglvnd (1.7.0-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libgpg-error (1.58-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-pcre2 (10.47-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-util-linux (2.41.3-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-glib2 (2.86.3-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-nspr (4.38.2-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libtasn1 (4.20.0-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-p11-kit (0.25.10-2)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-sqlite (3.51.1-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-nss (3.119.1-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-audit (4.1.2-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libtirpc (1.3.7-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libnsl (2.0.1-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-pam (1.7.1-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libcap (2.77-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libgcrypt (1.11.2-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-systemd (259-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libnm (1.54.3-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libxfixes (6.0.1-2)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libva (2.22.0-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libxcrypt-compat (4.5.2-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libxinerama (1.1.5-2)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libxss (1.2.4-2)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-libpipewire (1:1.4.9-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-dbus (1.16.2-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-pipewire (1:1.4.9-1)
[2025-12-27T20:55:47-0800] [ALPM] installed lib32-vulkan-icd-loader (1.4.335.0-1)
[2025-12-27T20:55:47-0800] [ALPM] installed steam (1.0.0.85-1)
[2025-12-27T20:56:06-0800] [ALPM] installed discord (1:0.0.119-1)
[2025-12-27T21:13:03-0800] [ALPM] installed yay (12.5.7-1)
[2025-12-27T21:13:03-0800] [ALPM] installed yay-debug (12.5.7-1)
[2025-12-27T21:13:49-0800] [ALPM] installed spotify (1:1.2.79.425-1)
[2025-12-27T21:17:46-0800] [ALPM] installed visual-studio-code-bin (1.107.1-1)
[2025-12-27T21:24:47-0800] [ALPM] installed libngtcp2 (1.19.0-1)
[2025-12-27T21:24:47-0800] [ALPM] installed simdjson (1:4.2.4-1)
[2025-12-27T21:24:47-0800] [ALPM] installed nodejs (25.2.1-1)
[2025-12-27T21:24:47-0800] [ALPM] installed electron37 (37.5.1-1)
[2025-12-27T21:25:40-0800] [ALPM] installed cursor-bin (2.3.8-1)
[2025-12-27T21:29:24-0800] [ALPM] installed gnome-browser-connector (42.1-7)
[2025-12-27T21:39:03-0800] [ALPM] installed openrazer-driver-dkms (3.11.0-2)
[2025-12-27T21:39:03-0800] [ALPM] installed python-daemonize (2.5.0-8)
[2025-12-27T21:39:03-0800] [ALPM] installed python-pyudev (0.24.3-2)
[2025-12-27T21:39:03-0800] [ALPM] installed xautomation (1.09-6)
[2025-12-27T21:39:03-0800] [ALPM] installed openrazer-daemon (3.11.0-2)
[2025-12-27T21:56:27-0800] [ALPM] installed libappindicator (12.10.1-1)
[2025-12-27T22:36:50-0800] [ALPM] installed libxnvctrl (590.48.01-1)
[2025-12-27T22:36:50-0800] [ALPM] installed nvidia-settings (590.48.01-1)
[2025-12-27T22:53:52-0800] [ALPM] installed otf-monaspace (1.301-1)
[2025-12-27T22:58:22-0800] [ALPM] installed ttf-jetbrains-mono (2.304-2)
[2025-12-27T23:00:14-0800] [ALPM] installed java-runtime-common (3-6)
[2025-12-27T23:00:14-0800] [ALPM] installed libnet (2:1.3-1)
[2025-12-27T23:00:14-0800] [ALPM] installed java-environment-common (3-6)
[2025-12-27T23:00:15-0800] [ALPM] installed jdk-openjdk (25.0.1.u8-1)
[2025-12-27T23:00:15-0800] [ALPM] installed dbeaver (25.3.1-1)
[2025-12-28T09:30:08-0800] [ALPM] installed fuse2 (2.9.9-5)
[2025-12-30T16:46:34-0800] [ALPM] installed helmfile (1.1.7-1)
[2025-12-30T16:49:37-0800] [ALPM] installed helm (3.19.4-1)
[2025-12-30T17:01:42-0800] [ALPM] installed open-isns (0.103-1)
[2025-12-30T17:01:42-0800] [ALPM] installed open-iscsi (2.1.11-1)
```
