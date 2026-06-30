#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 '<json-body>'" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${API_DIR}/.env"
BODY="$1"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Run ./scripts/gen_secrets.sh first." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

if [[ -z "${DEMO_HMAC_SECRET:-}" ]]; then
  echo "DEMO_HMAC_SECRET is missing from ${ENV_FILE}" >&2
  exit 1
fi

single_quote() {
  printf "'"
  printf "%s" "$1" | sed "s/'/'\\\\''/g"
  printf "'"
}

TIMESTAMP="$(date +%s)"
SIGNATURE="$(printf "%s" "${TIMESTAMP}.${BODY}" | openssl dgst -sha256 -hmac "${DEMO_HMAC_SECRET}" -hex | awk '{print $2}')"
QUOTED_BODY="$(single_quote "${BODY}")"

cat <<EOF
curl -i -X POST http://127.0.0.1:8000/hmac \\
  -H 'Content-Type: application/json' \\
  -H 'X-Timestamp: ${TIMESTAMP}' \\
  -H 'X-Signature: ${SIGNATURE}' \\
  --data-raw ${QUOTED_BODY}
EOF
