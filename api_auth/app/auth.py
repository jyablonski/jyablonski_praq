from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jwt
from fastapi import HTTPException
from jwt import (
    DecodeError,
    ExpiredSignatureError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
)


API_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = API_DIR / ".env"
MAX_HMAC_AGE_SECONDS = 300


@dataclass(frozen=True)
class Settings:
    api_key: str
    bearer_token: str
    hmac_secret: str
    hs256_secret: str
    jwt_issuer: str
    rs256_public_key_path: Path


def _load_dotenv(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _resolve_api_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else API_DIR / path


def _load_settings() -> Settings:
    _load_dotenv()
    return Settings(
        api_key=_required_env("DEMO_API_KEY"),
        bearer_token=_required_env("DEMO_BEARER_TOKEN"),
        hmac_secret=_required_env("DEMO_HMAC_SECRET"),
        hs256_secret=_required_env("DEMO_HS256_SECRET"),
        jwt_issuer=os.environ.get("DEMO_JWT_ISSUER", "demo-client"),
        rs256_public_key_path=_resolve_api_path(
            _required_env("DEMO_RS256_PUBLIC_KEY_PATH")
        ),
    )


SETTINGS = _load_settings()


def _unauthorized(message: str) -> None:
    raise HTTPException(status_code=401, detail=message)


def _bad_request(message: str) -> None:
    raise HTTPException(status_code=400, detail=message)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        _unauthorized("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        _bad_request("Authorization header must be 'Bearer <token>'")

    return parts[1]


def _decode_jwt(token: str, key: str, algorithm: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            issuer=SETTINGS.jwt_issuer,
            options={"require": ["exp", "iss"]},
        )
    except ExpiredSignatureError:
        _unauthorized("JWT has expired")
    except InvalidIssuerError:
        _unauthorized("JWT issuer is invalid")
    except InvalidSignatureError:
        _unauthorized("JWT signature is invalid")
    except DecodeError as exc:
        _bad_request(f"JWT is malformed: {exc}")
    except InvalidTokenError as exc:
        _unauthorized(f"JWT is invalid: {exc}")


def verify_api_key(api_key: str | None) -> None:
    if not api_key:
        _unauthorized("Missing X-API-Key header")
    if not hmac.compare_digest(api_key, SETTINGS.api_key):
        _unauthorized("Invalid API key")


def verify_static_bearer(authorization: str | None) -> None:
    token = _extract_bearer_token(authorization)
    if not hmac.compare_digest(token, SETTINGS.bearer_token):
        _unauthorized("Invalid bearer token")


def verify_hs256_jwt(authorization: str | None) -> dict[str, Any]:
    token = _extract_bearer_token(authorization)
    return _decode_jwt(token, SETTINGS.hs256_secret, "HS256")


def verify_hmac_signature(
    raw_body: bytes, timestamp: str | None, signature: str | None
) -> None:
    if not timestamp:
        _unauthorized("Missing X-Timestamp header")
    if not signature:
        _unauthorized("Missing X-Signature header")

    try:
        timestamp_int = int(timestamp)
    except ValueError:
        _bad_request("X-Timestamp must be a unix timestamp")

    age_seconds = int(time.time()) - timestamp_int
    if age_seconds > MAX_HMAC_AGE_SECONDS:
        _unauthorized("HMAC timestamp is older than 5 minutes")

    signed_payload = timestamp.encode("utf-8") + b"." + raw_body
    expected_signature = hmac.new(
        SETTINGS.hmac_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        _unauthorized("Invalid HMAC signature")


def verify_rs256_jwt(authorization: str | None) -> dict[str, Any]:
    token = _extract_bearer_token(authorization)
    try:
        public_key = SETTINGS.rs256_public_key_path.read_text()
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"RS256 public key not found: {SETTINGS.rs256_public_key_path}"
        ) from exc

    return _decode_jwt(token, public_key, "RS256")
