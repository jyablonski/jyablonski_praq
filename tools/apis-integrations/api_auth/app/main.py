from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Header, Request

from app.auth import (
    verify_api_key,
    verify_hmac_signature,
    verify_hs256_jwt,
    verify_rs256_jwt,
    verify_static_bearer,
)


app = FastAPI(title="Auth Mechanism Demo")


# Header affects swagger docs
@app.post("/api-key")
def api_key_auth(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> dict[str, str]:
    verify_api_key(x_api_key)
    return {"status": "ok", "auth": "api-key"}


@app.post("/bearer-static")
def bearer_static_auth(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict[str, str]:
    verify_static_bearer(authorization)
    return {"status": "ok", "auth": "bearer-static"}


@app.post("/bearer-jwt")
def bearer_jwt_auth(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict[str, object]:
    claims = verify_hs256_jwt(authorization)
    print(f"Verified HS256 JWT claims: {claims}")
    return {"status": "ok", "auth": "bearer-jwt", "claims": claims}


@app.post("/hmac")
async def hmac_auth(
    request: Request,
    x_timestamp: Annotated[str | None, Header(alias="X-Timestamp")] = None,
    x_signature: Annotated[str | None, Header(alias="X-Signature")] = None,
) -> dict[str, str]:
    raw_body = await request.body()
    verify_hmac_signature(raw_body, x_timestamp, x_signature)
    return {"status": "ok", "auth": "hmac"}


@app.post("/asymmetric")
def asymmetric_auth(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict[str, object]:
    claims = verify_rs256_jwt(authorization)
    print(f"Verified RS256 JWT claims: {claims}")
    return {"status": "ok", "auth": "asymmetric", "claims": claims}
