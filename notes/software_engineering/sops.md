# SOPS

SOPS is a tool for encrypting secrets within files, designed to be used in Git Repositories. It uses envelope encryption with a combination of long-lived age identities, ephemeral keys, and a data encryption key (DEK) to securely manage secrets.

## Envelope encryption basics

SOPS uses envelope encryption. Three categories of keys are involved:

1. Long-lived age identity (X25519 keypair) per principal. Public key listed as a recipient, private key held by the principal.
1. Data Encryption Key (DEK). Random symmetric key generated per file. Encrypts the actual secret values with AES256-GCM. Never stored in plaintext.
1. Ephemeral X25519 keypair. Generated per recipient per encryption operation. Used once to wrap the DEK, then the private half is discarded.

X25519 is a key agreement primitive, not an encryption primitive. You cannot encrypt arbitrary data directly to an X25519 public key. You derive a shared secret via ECDH, then use that secret with a symmetric cipher.

## Why three keys instead of one

Using the age identity alone fails for several reasons:

- X25519 cannot encrypt bulk data directly.
- Multiple recipients would each need a full copy of the ciphertext.
- Static-static ECDH produces the same shared secret forever for a given pair, which means nonce reuse risk and no freshness.
- Rotation becomes nearly impossible without a DEK in the middle.

The DEK handles bulk encryption. The ephemeral keypair provides freshness per wrap. The static identity provides stable addressing.

## Encryption flow per recipient

1. SOPS generates one DEK for the file.
1. age generates an ephemeral X25519 keypair for this recipient.
1. shared_secret = ECDH(ephemeral_priv, recipient_static_pub)
1. HKDF derives a ChaCha20-Poly1305 key from shared_secret.
1. DEK is wrapped with that key.
1. ephemeral_pub + wrapped_DEK + header_HMAC is stored in the enc block. ephemeral_priv is discarded.

On decrypt, the recipient reverses this using their static private key and the ephemeral public key embedded in the enc block.

## SOPS file structure

For YAML files, structure is stable:

- Real keys at the top with `ENC[AES256_GCM,data:...,iv:...,tag:...,type:...]` values.
- `sops:` metadata block at the bottom containing recipient list, MAC, version, lastmodified.
- Keys are left plaintext by default. Only values are encrypted. This keeps diffs reviewable.
- `encrypted_regex`, `encrypted_suffix`, `unencrypted_regex`, `unencrypted_suffix` in `.sops.yaml` let you override what gets encrypted.
- The MAC protects against reordering and tampering. `mac_only_encrypted: true` scopes it to encrypted values only, which reduces breakage on structural edits.

## Decrypting

Any single private key matching any recipient in `sops.age[]` is sufficient. SOPS walks the enc blocks, tries to unwrap with whatever identities are available, and stops on the first success. You never need all recipient keys.

Base64 decoding an enc block reveals the age header structure but not the DEK itself. The wrapped DEK requires the matching static private key to unwrap.

## creation_rules only applies on creation

`.sops.yaml` is consulted when SOPS creates a new file. Existing files store their recipient list in the `sops:` block and do not re-read `.sops.yaml` on edit.

- `sops updatekeys <file>` syncs an existing file to match `.sops.yaml`. Cheap, does not rotate the DEK.
- `sops -r <file>` rotates the DEK and re-encrypts values. Required when removing a recipient so their old enc block becomes useless.
- Git history still contains old ciphertexts. Removed recipients can decrypt anything they had access to before rotation. Unavoidable without rewriting history.

## Team-scale patterns

### Solo or homelab

One age key per device you control (laptop, cluster, CI). Not really shared, just you wearing different hats.

### Small team, per-person keys (start here)

Every engineer generates their own age key. Public keys listed in `.sops.yaml`. `key_groups` with YAML anchors keeps the list maintainable.

- Onboard: add public key, run `sops updatekeys` across files.
- Offboard: remove public key, run `updatekeys`, run `sops -r` on anything sensitive.
- Skip the shared-key phase entirely. Migrating off a shared key later is painful.

### KMS backend (around 10 to 20 people)

Swap age recipients for AWS KMS, GCP KMS, Azure Key Vault, or Vault Transit ARNs. Access control moves to IAM.

- One ARN replaces N public keys.
- Onboard and offboard via normal IAM group membership.
- CloudTrail or equivalent provides audit trails.
- Costs per-decrypt and adds latency. Cache plaintext in CI to control quota usage.

### Mix backends by sensitivity

Low-sensitivity secrets stay on age for velocity. Prod secrets go through KMS for attribution. Highest-sensitivity dynamic credentials do not live in SOPS at all.

### SOPS as bootstrap only

At real scale, SOPS holds the bootstrap credentials that reach a runtime secrets manager like Vault or AWS Secrets Manager. The secrets manager is the system of record. External Secrets Operator or Vault Agent syncs into Kubernetes at runtime.

## Scaling properties

- Each enc block is roughly 300 to 400 bytes of YAML.
- Encrypted value ciphertext size is independent of recipient count. Only the `sops:` metadata scales linearly with recipients.
- 53 recipients times 350 bytes is about 18KB of metadata per file.
- `sops updatekeys` runs on personnel changes produce massive diffs that are not meaningfully reviewable.
- KMS flattens this. One ARN regardless of headcount.

## Tipping point signals

Migrate off per-person age keys when:

- `sops updatekeys` runs happen more than monthly.
- Someone cannot decrypt because their key was missed on a new file.
- Auditors ask who accessed what.
- `.sops.yaml` exceeds ~200 lines.
- Contractors or short-term access become common.

## Summary

age identity is for stable addressing. DEK is for bulk data. Ephemeral keys are for freshness. Per-person age keys scale cleanly to maybe 20 engineers. KMS scales to any headcount because access control lives in IAM. Proper secrets managers handle the runtime and rotation concerns SOPS was never designed for.
