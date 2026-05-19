#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHON_BIN

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Run ./scripts/gen_secrets.sh first." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

echo
echo "# /api-key valid: X-API-Key matches DEMO_API_KEY and should return 200"
curl -i -X POST "${BASE_URL}/api-key" -H "X-API-Key: ${DEMO_API_KEY}"

echo
echo "# /api-key invalid: wrong API key should return 401"
curl -i -X POST "${BASE_URL}/api-key" -H "X-API-Key: wrong-key"

echo
echo "# /bearer-static valid: static bearer token matches DEMO_BEARER_TOKEN and should return 200"
curl -i -X POST "${BASE_URL}/bearer-static" -H "Authorization: Bearer ${DEMO_BEARER_TOKEN}"

echo
echo "# /bearer-static invalid: wrong bearer token should return 401"
curl -i -X POST "${BASE_URL}/bearer-static" -H "Authorization: Bearer wrong-token"

echo
echo "# /bearer-jwt valid: HS256 JWT has iss=demo-client and exp=now+5min"
HS256_TOKEN="$("${SCRIPT_DIR}/scripts/sign_jwt.sh" hs256)"
curl -i -X POST "${BASE_URL}/bearer-jwt" -H "Authorization: Bearer ${HS256_TOKEN}"

echo
echo "# /bearer-jwt invalid: expired HS256 JWT should return 401"
EXPIRED_HS256_TOKEN="$("${PYTHON_BIN}" - "${SCRIPT_DIR}" <<'PY'
import os
import sys
import time

import jwt

api_dir = sys.argv[1]
payload = {"iss": os.environ.get("DEMO_JWT_ISSUER", "demo-client"), "sub": "test-user", "exp": int(time.time()) - 60}
print(jwt.encode(payload, os.environ["DEMO_HS256_SECRET"], algorithm="HS256"))
PY
)"
curl -i -X POST "${BASE_URL}/bearer-jwt" -H "Authorization: Bearer ${EXPIRED_HS256_TOKEN}"

echo
echo "# /hmac valid: helper signs timestamp.raw_body with DEMO_HMAC_SECRET and should return 200"
eval "$("${SCRIPT_DIR}/scripts/sign_hmac.sh" '{"demo":"valid"}' | sed "s#http://127.0.0.1:8000#${BASE_URL}#")"

echo
echo "# /hmac invalid: bad signature over the body should return 401"
curl -i -X POST "${BASE_URL}/hmac" \
  -H 'Content-Type: application/json' \
  -H "X-Timestamp: $(date +%s)" \
  -H "X-Signature: bad-signature" \
  --data-raw '{"demo":"invalid"}'

echo
echo "# /asymmetric valid: RS256 JWT signed by private.pem verifies against public.pem and should return 200"
RS256_TOKEN="$("${SCRIPT_DIR}/scripts/sign_jwt.sh" rs256)"
curl -i -X POST "${BASE_URL}/asymmetric" -H "Authorization: Bearer ${RS256_TOKEN}"

echo
echo "# /asymmetric invalid: expired RS256 JWT should return 401"
EXPIRED_RS256_TOKEN="$("${PYTHON_BIN}" - "${SCRIPT_DIR}" <<'PY'
import os
import pathlib
import sys
import time

import jwt

api_dir = pathlib.Path(sys.argv[1])
key_path = pathlib.Path(os.environ["DEMO_RS256_PRIVATE_KEY_PATH"])
if not key_path.is_absolute():
    key_path = api_dir / key_path
payload = {"iss": os.environ.get("DEMO_JWT_ISSUER", "demo-client"), "sub": "test-user", "exp": int(time.time()) - 60}
print(jwt.encode(payload, key_path.read_text(), algorithm="RS256"))
PY
)"
curl -i -X POST "${BASE_URL}/asymmetric" -H "Authorization: Bearer ${EXPIRED_RS256_TOKEN}"
