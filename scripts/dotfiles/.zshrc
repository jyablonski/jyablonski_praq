# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

export EDITOR=nano

# PATH gahbage
export PATH="$PATH:$HOME/.local/bin:$HOME/.cargo/bin:$(go env GOPATH)/bin"
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"

export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
[ -s "$BUN_INSTALL/_bun" ] && source "$BUN_INSTALL/_bun"

export PATH="$HOME/.opencode/bin:$PATH"

# dbt env vars
export DBT_DBNAME=jacob_db
export DBT_SCHEMA=source
export DBT_PORT=17841

# ai tool shit
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_LOGS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=60000

export ARC_EXTRA_COMMANDS=1

# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------
# Sensitive env vars live in ~/.zshrc.secrets (not committed).
# On a fresh machine, create the file with the following exports:
#
#   export SLACK_WEBHOOK_URL=...
#   export DISCORD_WEBHOOK_URL=...
#   export DB_HOST=...
#   export DB_USER=...
#   export DB_PASS=...
#
# The file is sourced only if it exists, so the shell will start fine
# without it (env-dependent commands will just fail until it's populated).
# ---------------------------------------------------------------------------

[ -f ~/.zshrc.secrets ] && source ~/.zshrc.secrets
