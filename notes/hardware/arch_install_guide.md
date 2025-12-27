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

| Flag   | Meaning                    | Example             |
| ------ | -------------------------- | ------------------- |
| `-S`   | Sync/install package       | `pacman -S firefox` |
| `-R`   | Remove package             | `pacman -R firefox` |
| `-Q`   | Query installed packages   | `pacman -Q`         |
| `-Syu` | Sync, refresh, upgrade all | `pacman -Syu`       |

**Useful modifiers:**

| Flag   | Meaning                                | Example               |
| ------ | -------------------------------------- | --------------------- |
| `-Ss`  | Search for package                     | `pacman -Ss spotify`  |
| `-Qs`  | Search installed packages              | `pacman -Qs nvidia`   |
| `-Si`  | Info about a package                   | `pacman -Si firefox`  |
| `-Rs`  | Remove package + orphaned dependencies | `pacman -Rs firefox`  |
| `-Rns` | Remove + dependencies + config files   | `pacman -Rns firefox` |

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

4. Once in BIOS, select the USB drive as the boot device

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

### Force X11 on GDM (for nvidia-settings digital vibrance)

Edit `/etc/gdm/custom.conf`:

```
[daemon]
WaylandEnable=false
```

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
