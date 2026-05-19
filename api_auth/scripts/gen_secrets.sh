#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${API_DIR}/.env"
KEYS_DIR="${API_DIR}/keys"
FORCE=false

if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

mkdir -p "${KEYS_DIR}"

get_env_value() {
  local key="$1"
  if [[ -f "${ENV_FILE}" ]]; then
    grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 | cut -d= -f2- || true
  fi
}

hex_secret() {
  openssl rand -hex 16
}

value_or_new() {
  local key="$1"
  local existing
  existing="$(get_env_value "${key}")"

  if [[ "${FORCE}" == false && -n "${existing}" ]]; then
    printf "%s" "${existing}"
  else
    hex_secret
  fi
}

API_KEY="$(value_or_new "DEMO_API_KEY")"
BEARER_TOKEN="$(value_or_new "DEMO_BEARER_TOKEN")"
HMAC_SECRET="$(value_or_new "DEMO_HMAC_SECRET")"
HS256_SECRET="$(value_or_new "DEMO_HS256_SECRET")"
JWT_ISSUER="$(get_env_value "DEMO_JWT_ISSUER")"
JWT_ISSUER="${JWT_ISSUER:-demo-client}"
PRIVATE_KEY_PATH="keys/private.pem"
PUBLIC_KEY_PATH="keys/public.pem"

if [[ "${FORCE}" == true || ! -f "${API_DIR}/${PRIVATE_KEY_PATH}" || ! -f "${API_DIR}/${PUBLIC_KEY_PATH}" ]]; then
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "${API_DIR}/${PRIVATE_KEY_PATH}"
  openssl rsa -pubout -in "${API_DIR}/${PRIVATE_KEY_PATH}" -out "${API_DIR}/${PUBLIC_KEY_PATH}"
fi

cat > "${ENV_FILE}" <<EOF
DEMO_API_KEY=${API_KEY}
DEMO_BEARER_TOKEN=${BEARER_TOKEN}
DEMO_HMAC_SECRET=${HMAC_SECRET}
DEMO_HS256_SECRET=${HS256_SECRET}
DEMO_JWT_ISSUER=${JWT_ISSUER}
DEMO_RS256_PRIVATE_KEY_PATH=${PRIVATE_KEY_PATH}
DEMO_RS256_PUBLIC_KEY_PATH=${PUBLIC_KEY_PATH}
EOF

echo "Wrote ${ENV_FILE}"
echo "Keys are in ${KEYS_DIR}"
