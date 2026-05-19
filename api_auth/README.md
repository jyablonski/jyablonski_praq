# FastAPI Auth Mechanism Demo

Minimal FastAPI app showing five common auth checks with no database, middleware stack, or business logic.

## When to use each

| Mechanism | Use when | Avoid when |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API key | Internal service-to-service calls, admin tooling, or low-risk public APIs with per-key rate limits. | The client is untrusted (browser, mobile app) or you need per-request identity beyond the key. |
| Static bearer | Quick machine-to-machine integrations, CI jobs, or scripts where rotation is manual and infrequent. Same as API Key functionally. | Tokens need to expire, carry claims, or be issued by a separate auth service. |
| HS256 JWT | A single trusted issuer signs short-lived tokens and the verifier can hold the shared secret safely. | Multiple verifiers exist, or the signer and verifier are in different trust boundaries (the shared secret leaks verification *and* signing capability). |
| HMAC over body | Webhooks and any callback where you need to prove the payload wasn't tampered with in transit and bind the request to a timestamp to prevent replay. | The client can't compute signatures (most browser flows), or you need user identity rather than payload integrity. |
| RS256 JWT | Tokens are issued by one party (IdP, partner, auth service) and verified by many; verifiers should only hold the public key. | You control both ends and don't need key separation — HS256 is simpler and faster. |

For Static Bearer vs API Key:

- Header: X-API-Key: <secret> vs Authorization: Bearer <secret>
- Parsing: bearer needs you to split the Bearer prefix off; API key is the raw header value
- They both use `hmac.compare_digest` to check the secret. This method is basically just a string comparison check, except it returns in constant time for any given sized input. Otherwise, attackers could measure how long it's taking the server to respond and where the byte mismatch is happening, and use that to brute force the secret one character at a time.

## Setup

Generate demo secrets:

```bash
cd api
./scripts/gen_secrets.sh
```

Regenerate everything with:

```bash
./scripts/gen_secrets.sh --force
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test

In another terminal:

```bash
./test_requests.sh
```

The JWT and HMAC helpers can also be used directly:

```bash
./scripts/sign_jwt.sh hs256
./scripts/sign_jwt.sh rs256
./scripts/sign_hmac.sh '{"hello":"world"}'
```

## Endpoints

- `POST /api-key`: verifies `X-API-Key`; useful for simple service or admin integrations where a shared secret is acceptable.
- `POST /bearer-static`: verifies a static `Authorization: Bearer <token>` value; useful for simple machine-to-machine calls.
- `POST /bearer-jwt`: verifies an HS256 JWT with `exp` and `iss`; useful when one trusted issuer signs short-lived tokens with a shared secret.
- `POST /hmac`: verifies `X-Timestamp` and `X-Signature` over the raw body; useful for webhooks where tamper detection matters.
- `POST /asymmetric`: verifies an RS256 JWT with `exp` and `iss`; useful when issuers sign with private keys and services verify with public keys.

## Output

`./test_requests.sh` prints one valid and one invalid request for each auth mechanism.

| Endpoint | Valid request | Invalid request |
| --------------------- | -------------------------------------------- | ----------------------------------------- |
| `POST /api-key` | `200 {"status":"ok","auth":"api-key"}` | `401 {"detail":"Invalid API key"}` |
| `POST /bearer-static` | `200 {"status":"ok","auth":"bearer-static"}` | `401 {"detail":"Invalid bearer token"}` |
| `POST /bearer-jwt` | `200` with decoded HS256 claims | `401 {"detail":"JWT has expired"}` |
| `POST /hmac` | `200 {"status":"ok","auth":"hmac"}` | `401 {"detail":"Invalid HMAC signature"}` |
| `POST /asymmetric` | `200` with decoded RS256 claims | `401 {"detail":"JWT has expired"}` |

JWT responses include the decoded claims:

```json
{
  "status": "ok",
  "auth": "bearer-jwt",
  "claims": {
    "iss": "demo-client",
    "sub": "test-user",
    "exp": 1779052291
  }
}
```

```json
{
  "status": "ok",
  "auth": "asymmetric",
  "claims": {
    "iss": "demo-client",
    "sub": "test-user",
    "exp": 1779052292
  }
}
```
