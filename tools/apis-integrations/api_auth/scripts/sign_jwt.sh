#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ( "$1" != "hs256" && "$1" != "rs256" ) ]]; then
  echo "Usage: $0 hs256|rs256" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${API_DIR}/.env"
ALG="$1"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Run ./scripts/gen_secrets.sh first." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

"${PYTHON_BIN}" - "${ALG}" "${API_DIR}" <<'PY'
import os
import pathlib
import sys
import time

import jwt

alg = sys.argv[1]
api_dir = pathlib.Path(sys.argv[2])
issuer = os.environ.get("DEMO_JWT_ISSUER", "demo-client")
payload = {"iss": issuer, "sub": "test-user", "exp": int(time.time()) + 300}

if alg == "hs256":
    key = os.environ["DEMO_HS256_SECRET"]
    token = jwt.encode(payload, key, algorithm="HS256")
else:
    key_path = pathlib.Path(os.environ["DEMO_RS256_PRIVATE_KEY_PATH"])
    if not key_path.is_absolute():
        key_path = api_dir / key_path
    token = jwt.encode(payload, key_path.read_text(), algorithm="RS256")

print(token)
PY
