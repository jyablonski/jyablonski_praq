# Arch Linux Packaging

## Repository taxonomy

Arch is rolling-release with no versioned distro releases. Software is distributed through binary repositories synced via `pacman -Syu`.

### Official repositories

Maintained by Arch staff (Developers and Package Maintainers). Binary packages are pre-built, signed, and distributed via the mirror network.

- `core` — essential base system (kernel, glibc, pacman, systemd). Tightly controlled.
- `extra` — everything else official: desktop environments, applications, libraries, drivers. Most packages live here.
- `multilib` — 32-bit libraries for running 32-bit software on 64-bit systems.
- `core-testing` / `extra-testing` / `multilib-testing` — staging areas where updates land before promotion to stable. Most users do not enable these.

Inclusion in an official repo is not a vendor endorsement. The bar is: useful + maintainable + an Arch maintainer willing to own it. A package in `extra` might be from a Fortune 500 company or a community project with a handful of contributors. The signing and infrastructure benefits apply equally to both.

### AUR (Arch User Repository)

Not a binary repository. A collection of user-submitted PKGBUILD scripts hosted at `aur.archlinux.org`. AUR helpers like `yay` or `paru` clone these scripts, build packages locally on the user's machine, and install them via pacman. Anyone can submit; there is no review process or signing requirement. Packages can be orphaned if the maintainer disappears.

## Package fundamentals

### What a package is

An Arch package is a `.pkg.tar.zst` archive: a tar archive compressed with zstd. You can extract one with `tar --use-compress-program=unzstd -xf foo.pkg.tar.zst` and inspect the contents.

Inside the archive:

- The files that need to land on the filesystem, laid out in the paths they will occupy after install (`/usr/bin/foo`, `/etc/foo.conf`, etc.)
- `.PKGINFO` — plain-text metadata: name, version, dependencies, install size
- `.MTREE` — manifest of all files with checksums and permissions
- `.INSTALL` — optional shell script with lifecycle hooks (see below)
- `.BUILDINFO` — info about the build environment, used for reproducible builds

The package does not contain source code, only the built output. For a C program, that means the compiled ELF binary, not the .c files.

### What "compiled binaries" actually means per language

The package format is language-agnostic. It ships whatever files need to be on disk:

- **C / C++ / Rust / Go**: compiled ELF executables and shared libraries (`.so` files). Machine code the CPU executes directly.
- **Python (pure)**: `.py` source files plus optional `.pyc` bytecode in `__pycache__/`. Needs the `python` interpreter (itself an ELF binary) to run.
- **Python with C extensions** (numpy, pillow, cryptography): both `.py` files and compiled `.so` shared objects.
- **Interpreted languages** (Ruby, Perl, JS): source files plus possibly a wrapper script in `/usr/bin/` that invokes the interpreter.
- **Data-only packages** (fonts, icon themes): just the data files.

### PKGBUILD

The build recipe. A bash script defining variables (`pkgname`, `pkgver`, `pkgrel`, `depends`, `source`, etc.) and functions (`prepare`, `build`, `package`). Running `makepkg` in a directory with a PKGBUILD executes these functions to produce the `.pkg.tar.zst`.

The filename is uppercase with no extension by convention, like `Makefile` or `Dockerfile`. Unix decides file type from content (the shebang line) and the executable bit, not from extension. Bare names signal a well-known role in a tool's ecosystem.

Example excerpt:

```bash
pkgname=openrazer-daemon
pkgver=3.12.3
pkgrel=1
source=("https://github.com/openrazer/openrazer/archive/v$pkgver.tar.gz")
sha256sums=('a1b2c3...')
```

The `build()` function differs by language: C uses `./configure && make`, Go uses `go build`, Python uses `python -m build`. The package format does not care.

### .SRCINFO

A generated, machine-readable summary of the PKGBUILD. AUR uses it for indexing and dependency resolution. Regenerated with `makepkg --printsrcinfo > .SRCINFO` before pushing.

### .INSTALL hooks

Optional shell script bundled in the package. Sourced by pacman at specific lifecycle moments: `pre_install`, `post_install`, `pre_upgrade`, `post_upgrade`, `pre_remove`, `post_remove`. Used for creating system users, running `systemctl daemon-reload`, rebuilding font caches, or warning about manual intervention. Bash, not C.

## Verification mechanisms

### Checksums

Each `source` entry in a PKGBUILD has a corresponding hash (`sha256sums`, `b2sums`, etc.). When `makepkg` downloads sources at build time, it verifies the hash matches. This protects against corrupted downloads and unauthorized changes to source tarballs on upstream hosting.

Checksums verify integrity, not authenticity. They confirm "this file matches what the PKGBUILD author saw" but not "this file came from a trusted party."

Important: pacman does **not** use these sha256sums when you install a package. They are a build-time verification only. Install-time verification is via PGP signature on the final `.pkg.tar.zst`.

### PGP signatures

PGP (Pretty Good Privacy) provides authenticity through asymmetric cryptography. A signer holds a private key; everyone else holds the corresponding public key. The signer produces a signature over a file; anyone with the public key can verify it.

Two layers of PGP in Arch:

1. **Upstream source signatures.** Many projects sign their release tarballs. PKGBUILDs can declare `validpgpkeys=()` listing trusted upstream keys, and `makepkg` will verify the tarball signature before building. This applies to both official and AUR builds. The keys live in the user's GPG keyring, separate from the pacman keyring.

1. **Package signatures.** Every binary package in the official repos is signed by the maintainer who built it. Their public key is included in the `archlinux-keyring` package, which is itself signed by master keys held by Arch leadership. Pacman verifies signatures during install; an untrusted or invalid signature aborts the install.

The chain of trust: master keys → maintainer keys → individual packages. Compromising one maintainer's key affects only their packages, not the whole distribution.

### What pacman verifies on install

For every official package:

1. Downloads the `.pkg.tar.zst` and `.sig` from a mirror
1. Looks up the signer's public key in `/etc/pacman.d/gnupg/`
1. Verifies the signature is valid and the key is trusted
1. Aborts install if anything fails

The PGP signature implicitly covers the package contents (signatures include an internal hash), so any tampering after the maintainer signed is detected.

### Why update archlinux-keyring first

If a new maintainer joined since your last update, their key is not yet in your local keyring, and packages they sign will fail verification. If a key was revoked (compromise, maintainer left), you want that update before trusting any signatures. Standard update flow:

```bash
sudo pacman -Sy archlinux-keyring
sudo pacman -Syu
```

### Supply-chain risk

PGP verifies "this came from someone holding maintainer X's key" but not "maintainer X is trustworthy" or "their machine was not compromised." A rogue or compromised maintainer can sign malicious packages and your machine will accept them. Partial defenses:

- Maintainer keys are supposed to live on hardware tokens, making theft harder
- Keyring updates propagate revocations
- Reproducible builds let third parties independently rebuild and verify packages match
- Blast radius is bounded to packages that maintainer owns

The xz-utils backdoor in 2024 was a real example of this failure mode: a long-trusted upstream maintainer slipped in malicious code. PGP did not help because the signatures were valid; the trust assumption underneath was wrong.

## Pushing to official repositories

### Who can push

Only Arch Developers and Package Maintainers (collectively, Arch staff). Becoming staff requires a nomination process, demonstrated packaging skill, and existing staff approval.

### The workflow

1. Source lives in git at `gitlab.archlinux.org/archlinux/packaging/packages/<pkgname>`.
1. Maintainer clones the repo, edits the PKGBUILD, commits.
1. Builds using `pkgctl build`, which runs `makepkg` in a clean `systemd-nspawn` chroot containing only `base`, `base-devel`, and declared `makedepends`.
1. Signs the resulting `.pkg.tar.zst` with their personal PGP key (typically on a hardware token).
1. Runs `pkgctl release` to upload to staging and tag the git commit.
1. Server-side `dbscripts` tooling validates the signature, moves the package through `extra-testing` and then `extra`, updates the repo database.
1. Mirrors sync. Users see the update on next `pacman -Syu`.

Maintainer-initiated, not fully automated CI/CD. Shared build infrastructure exists (buildbot at `buildbot.pkgbuild.com`) but is opt-in. The trust model keeps signing keys in human hands rather than CI systems.

## Pushing to the AUR

1. Create an account at `aur.archlinux.org`, add an SSH key.
1. Write a PKGBUILD and generate `.SRCINFO`.
1. Clone the AUR git repo: `git clone ssh://aur@aur.archlinux.org/<pkgname>.git`.
1. Add files, commit, push.
1. AUR helpers see the new version on next sync.

No binary artifacts, no signing, no review. The maintainer is solely responsible.

### AUR risk

When you install an AUR package, you are trusting:

1. The PKGBUILD itself is not malicious. It is bash that runs on your machine during build.
1. The source URL points at the real upstream, not a tampered fork.
1. The build process does not do anything sneaky.

Mitigations:

- Read the PKGBUILD before installing, especially for less popular packages or new accounts.
- Prefer popular, long-maintained packages with high vote counts.
- Be skeptical of recently orphaned-and-adopted packages.
- Use `pkgctl build` or a clean chroot for higher-risk packages.

`archlinux-keyring` does not cover AUR packages. Source-level PGP verification may still happen if the PKGBUILD declares `validpgpkeys`, but there is no package-level signing.

## Flagging out-of-date

Both official and AUR packages have an "out-of-date" flag on their web page. Any user can mark a package outdated by providing the new upstream version. This notifies the maintainer. It is the canonical signal mechanism for "upstream released a new version."

## Kernel space vs userspace

Most software runs in userspace: ordinary processes that talk to the kernel through standardized system calls. Userspace packages are not coupled to the kernel version; a binary compiled against glibc keeps working across kernel updates.

Some software runs in kernel space: code linked directly against kernel internals with privileged hardware access. Kernel modules (`.ko` files) plug into the running kernel and must be compiled against the exact kernel version they will load into. Kernel internals change between versions, so a module built for 7.0.5 will not load into 7.0.6 if any relevant API moved.

A driver gets into the kernel one of two ways:

1. **In-tree**: merged into the mainline Linux kernel. Ships pre-compiled with every kernel release, version-matched automatically. Generic HID, most filesystems, most GPU drivers.
1. **Out-of-tree**: maintained separately. Must be recompiled for every kernel version. DKMS automates this.

Out-of-tree typically happens when upstream Linux will not accept the driver: proprietary licensing (NVIDIA), license incompatibility (ZFS), or reverse-engineered hardware without vendor cooperation (openrazer).

### Kernel-module AUR risk

Kernel modules run with full privilege, so compromise via a malicious module is severe. But most kernel-module AUR packages are thin packaging wrappers around well-known upstream projects (`nvidia-dkms`, `zfs-dkms`, `openrazer-driver-dkms-git`). If you trust the upstream and the PKGBUILD pulls from its legitimate URL without weird patches, the risk is bounded. Avoid brand-new kernel-module packages from unknown accounts.

## DKMS and kernel coupling

### What DKMS does

DKMS (Dynamic Kernel Module Support) ships kernel module source code that gets compiled against the current kernel's headers at install time and on every kernel update.

### How it works

A DKMS package installs source to `/usr/src/<modulename>-<version>/`. A hook fires on package install and on every kernel update:

1. Pacman installs a new kernel.
1. The DKMS hook iterates registered modules.
1. For each, runs `make` against the new kernel's headers in `/usr/lib/modules/<kernel>/build/`.
1. On success, the resulting `.ko` is installed into the new kernel's module tree.
1. On failure, the module is unavailable until the kernel is rolled back or the source is updated.

Check status with `dkms status`.

### Failure mode on rolling-release

Kernel APIs change. A common failure:

- Arch backports an API change from kernel `X.Y+1` into its current `X.Y.Z`.
- The DKMS module uses `LINUX_VERSION_CODE` to pick old vs new API, assuming the change landed at `X.Y+1`.
- The version check picks the wrong branch on Arch's kernel and the build fails.
- Fix requires either an upstream release adjusting the guard or a distro-level patch in the PKGBUILD.

A "backport" means taking a change from a newer version and applying it to an older still-supported one, usually for security or feature reasons.

### Mitigation: linux-lts

Install `linux-lts` alongside `linux`:

- `linux` tracks the latest stable kernel, currently moving fast.
- `linux-lts` tracks a long-term-support kernel, currently older and slower-moving.
- Both are installed simultaneously with separate kernel images, initramfs, and module trees.
- Bootloader shows both as boot options.
- If `linux` breaks a DKMS module or has a regression, reboot into `linux-lts`.

Recommended refinements:

- Set `linux-lts` as the default boot entry. A reboot during a broken state defaults to working.
- Keep `linux-lts-headers` installed so DKMS builds against both kernels.
- Verify `dkms status` shows modules built for both kernels before relying on the fallback.

## Quick reference

### Tools

| Tool | Purpose |
| ----------- | -------------------------------------------------------- |
| `pacman` | Install and manage packages from binary repos |
| `makepkg` | Build a package from a PKGBUILD |
| `pkgctl` | Maintainer tool wrapping makepkg in clean chroots |
| `dbscripts` | Server-side repo management |
| DKMS | Builds out-of-tree kernel modules against current kernel |

### Files

| File | Purpose |
| ------------------- | ------------------------------------------------- |
| `PKGBUILD` | Build recipe (bash script) |
| `.SRCINFO` | Machine-readable PKGBUILD summary for AUR |
| `.PKGINFO` | Package metadata |
| `.INSTALL` | Lifecycle hook scripts |
| `.MTREE` | File manifest with checksums |
| `archlinux-keyring` | Package containing trusted maintainer public keys |
