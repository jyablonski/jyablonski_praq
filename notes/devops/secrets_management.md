# Secret Sharing in Organizations

## Temporary Secrets

One-Time Secret Links

- Yopass - End-to-end encrypted secret sharing with time-limited access. Secrets are encrypted in the browser before being sent to the server, so the server never sees plaintext. You can set expiration times or one-time access. Great for sharing credentials during onboarding or sending API keys to contractors who don't have access to any long term secret store.
- OneTimeSecret - Similar concept, generates URLs that self-destruct after being viewed once
- SnapPass - Redis-backed temporary secret storage with configurable TTLs
- Bitwarden Send - Temporary sharing feature built into Bitwarden with file support

Use cases: Sharing initial passwords, API keys for demos, temporary database credentials, one-off access tokens

Key principle: These tools prevent secrets from living in email, Slack, or ticketing systems where they're searchable and archived indefinitely (even if deleted later).

## Long-Term Secrets

Vault Solutions

- HashiCorp Vault - Enterprise-grade secrets management with dynamic secrets, encryption as a service, and audit logging. Can generate temporary database credentials on-demand.
- AWS Secrets Manager - Managed service with automatic rotation, tight IAM integration
  - GCP and Azure have similar offerings
- Doppler - Developer-focused secrets management with sync capabilities
- Infisical - Open-source alternative to Doppler

Password Managers (Team)

- 1Password Business - Vaults with access controls, integration with SSO
- Bitwarden Organizations - Open-source with self-hosting option
- LastPass Enterprise - Though less popular after security incidents

Application-Level Strategies

- Environment variables injected at runtime from vault systems
- Kubernetes Secrets (often backed by external secret stores via operators like External Secrets Operator)
- SOPS (Secrets OPerationS) - Encrypts secrets in Git repos using KMS keys
- git-crypt - Transparent encryption for files in Git
- Sealed Secrets (Kubernetes) - Encrypt secrets that can only be decrypted in-cluster

## Architectural Patterns

Secret Zero Problem: How does your app authenticate to the vault? Solutions:

- IAM roles (AWS/GCP/Azure)
- Kubernetes service accounts
- AppRole authentication with secure token delivery
- Certificate-based auth

Rotation Strategies:

- Dynamic secrets that expire automatically
- Automated rotation pipelines (Vault can rotate database creds, AWS keys, etc.)
- Break-glass procedures for emergency access

Access Patterns:

- Just-in-time access with approval workflows (Vault's control groups, Teleport)
- Time-bounded leases that auto-expire
- Audit everything - who accessed what, when

## Why Yopass Specifically?

Yopass shines because:

- Zero-knowledge architecture - Server can't decrypt secrets
- Simple deployment - Just needs Redis/Memcached backend
- No accounts needed - Frictionless for recipients
- Flexible expiration - Time-based or one-time access

Good for: sharing production credentials during incidents, onboarding secrets, cross-team API keys when you don't share a vault system.

Less ideal for: Secrets needing audit trails, organizational policy enforcement, or integration with IAM systems.

## Hybrid Approach

A hybrid approach is needed for serving both temporary and long term secret needs.

Many orgs use multiple tools:

- Vault for application secrets and infrastructure
- Password manager for human credentials and shared team accounts
- Yopass/similar for external sharing or emergency situations
- SOPS/git-crypt for configuration secrets in IaC repos

The key is matching the tool to the secret's lifecycle and access patterns.

## Implementation (Helm)

When Vault starts up, all your secrets are encrypted on disk. Vault needs a master encryption key to decrypt them, but storing that key anywhere would be a security risk. So Vault uses Shamir's Secret Sharing to split the master key into multiple pieces.

- After initialization, you get several unseal keys and a root token.

Install Vault with Raft storage:

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com

helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --set server.ha.enabled=true \
  --set server.ha.replicas=3 \
  --set server.dataStorage.enabled=true \
  --set server.dataStorage.size=10Gi
```

Initialize and unseal:

```bash
# Initialize (save the keys!)
kubectl exec -n vault vault-0 -- vault operator init

# Unseal each replica (needs 3 of 5 keys)
kubectl exec -n vault vault-0 -- vault operator unseal <key1>
kubectl exec -n vault vault-0 -- vault operator unseal <key2>
kubectl exec -n vault vault-0 -- vault operator unseal <key3>

# Repeat for vault-1 and vault-2

```

## Secrets Storing (CI/CD Strategy)

Option 1: SOPS + Terraform (encrypted in Git) - this allows you to store secrets in Git securely and have Terraform manage them in Vault.

```
terraform/
├── secrets.tf
├── secrets.enc.yaml    # Encrypted, committed to Git
└── provider.tf
```

```yaml
# secrets.enc.yaml (SOPS-encrypted)
db_password: ENC[AES256_GCM,data:...]
api_key: ENC[AES256_GCM,data:...]
```

```hcl
# secrets.tf
locals {
  secrets = yamldecode(file("secrets.enc.yaml"))
}

resource "vault_kv_secret_v2" "app" {
  mount = "secret"
  name  = "apps/myapp"
  data_json = jsonencode(local.secrets)
}
```

Option 2: GitHub Secrets + Terraform vars

- Store secrets in GitHub repository secrets
- Pass via `TF_VAR_*` environment variables
- No encryption in repo, secrets live in GitHub

Option 3: Manual seeding + Terraform for config

- Manually add sensitive secrets via UI/CLI once
- Use Terraform only for policies, auth backends, roles
- Simple, but no automation

## CI/CD Pipeline

GitHub Actions with SOPS:

```yaml
name: Deploy to Vault

on:
  push:
    branches: [main]
    paths: ['terraform/']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup SOPS
        run: |
          curl -LO https://github.com/getsops/sops/releases/download/v3.8.1/sops-v3.8.1.linux.amd64
          sudo mv sops-v3.8.1.linux.amd64 /usr/local/bin/sops
          chmod +x /usr/local/bin/sops
      
      - name: Import decryption key
        run: |
          mkdir -p ~/.config/sops/age
          echo "${{ secrets.SOPS_AGE_KEY }}" > ~/.config/sops/age/keys.txt
      
      - uses: hashicorp/setup-terraform@v3
      
      - name: Terraform Apply
        env:
          VAULT_ADDR: "http://vault.vault.svc.cluster.local:8200"
          VAULT_TOKEN: ${{ secrets.VAULT_TOKEN }}
        working-directory: terraform
        run: |
          terraform init
          terraform apply -auto-approve
```


Key points:

- Store SOPS decryption key and Vault token as CI secrets
- Terraform auto-decrypts SOPS files when reading
- Use branch protection so secrets only deploy on merge to main
- Consider separate pipelines for dev/staging/prod secrets

### SOPS Developer Experience

Developers must have SOPS installed locally to edit encrypted files.

The actual workflow is straightforward:

Step 1: Edit the encrypted file

```bash
cd terraform/
sops secrets.enc.yaml
```

This opens your editor with the decrypted contents:

```yaml
db_password: "super-secret-pass"
stripe_key: "sk_live_xxxxx"
# Add your new secrets here:
openai_key: "sk-proj-new-key"
slack_webhook: "https://hooks.slack.com/services/XXX"
```

Step 2: Save and exit

SOPS automatically re-encrypts when you save. The file is now updated with your new secrets encrypted.

Step 3: Commit and PR
```bash
git add secrets.enc.yaml
git commit -m "Add OpenAI and Slack secrets"
git push origin feature/add-secrets
# Open PR
```

The developer never manually runs encrypt/decrypt commands. `sops <file>` handles everything:

- Decrypts for editing
- Re-encrypts on save
- Uses the key in `~/.config/sops/age/keys.txt` automatically

This workflow ensures:

- Can't accidentally commit plaintext (file stays encrypted)
- Git diffs show which keys changed, not the values
- Multiple people can edit with the same key
- If someone doesn't have the key, they can't decrypt (but can still see encrypted file structure)

## Service Integration

The easiest solution here to integrate Vault-stored secrets into your applications deployed via Helm is to use the External Secrets Operator (ESO). ESO syncs secrets from external secret stores like Vault into Kubernetes Secrets, which your applications can then consume.

Just template this out in your application's Helm chart in `values.yaml`:

```yaml
# values.yaml
vault:
  enabled: true
  address: "http://vault.vault.svc.cluster.local:8200"
  role: "my-api-role"
  secretStoreName: "vault-backend"
  
# Simple: all secrets from one path
secrets:
  vaultPath: "apps/my-api"
  keys:
    - db_password
    - api_key
    - stripe_key

# OR Complex: secrets from multiple paths
# secrets:
#   items:
#     - name: db_password
#       vaultPath: apps/my-api
#       vaultKey: db_password
#     - name: stripe_key
#       vaultPath: external-apis/stripe
#       vaultKey: api_key
```

Then in your Helm chart templates, reference the Kubernetes Secrets created by ESO (not showing full ESO setup here for brevity).