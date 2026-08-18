from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import polars as pl
import requests

log = logging.getLogger("iterable_sync")

API_BASE = os.environ.get("ITERABLE_API_BASE", "https://api.iterable.com")
API_KEY = os.environ["ITERABLE_API_KEY"]

BATCH_SIZE = 1000  # hard API ceiling
MAX_WORKERS = 4  # keep well under per-endpoint rate limits
ITERABLE_DT = "%Y-%m-%d %H:%M:%S +00:00"


# ---------- schema contract ----------------------------------------------

# Explicit is the whole point: this pins the type Iterable will lock in,
# and anything not listed here never leaves your warehouse.
FIELD_SCHEMA = {
    "email": pl.Utf8,
    "user_id": pl.Utf8,
    "first_name": pl.Utf8,
    "plan_tier": pl.Utf8,
    "lifetime_value": pl.Float64,
    "order_count": pl.Int64,
    "is_trial": pl.Boolean,
    "signup_at": pl.Datetime("us", "UTC"),
    "last_seen_at": pl.Datetime("us", "UTC"),
    "favorite_categories": pl.List(pl.Utf8),
}

# Map warehouse names -> Iterable field names. Iterable dislikes spaces and
# leading digits; keep these stable forever, renaming creates a new field.
FIELD_RENAMES = {
    "user_id": "userId",
    "first_name": "firstName",
    "plan_tier": "planTier",
    "lifetime_value": "lifetimeValue",
    "order_count": "orderCount",
    "is_trial": "isTrial",
    "signup_at": "signupAt",
    "last_seen_at": "lastSeenAt",
    "favorite_categories": "favoriteCategories",
}

REVENUE_TIERS = [
    # label,             lo,       hi
    ("01_lt_1000", None, 1000.0),
    ("02_1000_2499", 1000.0, 2500.0),
    ("03_2500_4999", 2500.0, 5000.0),
    ("04_5000_9999", 5000.0, 10000.0),
    ("05_10000_plus", 10000.0, None),
]

BOOKING_TIERS = [
    ("01_none", None, 1.0),
    ("02_1_2", 1.0, 3.0),
    ("03_3_9", 3.0, 10.0),
    ("04_10_plus", 10.0, None),
]

# Fields that go to Iterable but must NOT trigger a sync on their own.
# lifetimeValue changing by $3 is not worth a write; revenueTier changing is.
HASH_EXCLUDE = {"lifetimeValue", "bookingCount", "lastSyncedAt"}


def row_hash(df: pl.DataFrame) -> pl.DataFrame:
    cols = sorted(
        c for c in df.columns if c not in HASH_EXCLUDE and not c.startswith("_")
    )
    payload = pl.concat_str(
        [pl.col(c).cast(pl.Utf8).fill_null("\x00") for c in cols], separator="\x1f"
    )
    return df.with_columns(
        payload.map_elements(
            lambda s: hashlib.sha256(s.encode()).hexdigest(), return_dtype=pl.Utf8
        ).alias("_row_hash")
    )


def tier_with_hysteresis(
    df: pl.DataFrame,
    prev: pl.DataFrame | None,
    value_col: str,
    out_col: str,
    tiers: list[tuple[str, float | None, float | None]],
    key: str = "userId",
    margin: float = 0.05,  # 5% deadband on each boundary
) -> pl.DataFrame:
    """Assign a tier, but stay in the previous tier until the value clears
    its boundary by `margin`. Kills boundary flapping."""
    labels = [t[0] for t in tiers]
    breaks = [t[2] for t in tiers[:-1]]

    naive = (
        pl.col(value_col)
        .cut(breaks=breaks, labels=labels, left_closed=True)
        .cast(pl.Utf8)
        .alias("_naive_tier")
    )
    df = df.with_columns(naive)

    if prev is None or out_col not in prev.columns:
        return df.with_columns(pl.col("_naive_tier").alias(out_col)).drop("_naive_tier")

    NEG, POS = float("-inf"), float("inf")
    bounds = pl.DataFrame(
        {
            "_prev_tier": labels,
            "_lo": [t[1] if t[1] is not None else NEG for t in tiers],
            "_hi": [t[2] if t[2] is not None else POS for t in tiers],
        }
    )

    df = df.join(
        prev.select([key, pl.col(out_col).alias("_prev_tier")]), on=key, how="left"
    ).join(bounds, on="_prev_tier", how="left")

    # Expand the previous tier's range by the margin; if the value is still
    # inside the widened band, don't move.
    lo_relaxed = (
        pl.when(pl.col("_lo") == NEG).then(NEG).otherwise(pl.col("_lo") * (1 - margin))
    )
    hi_relaxed = (
        pl.when(pl.col("_hi") == POS).then(POS).otherwise(pl.col("_hi") * (1 + margin))
    )

    sticky = (
        pl.col("_prev_tier").is_not_null()
        & (pl.col(value_col) >= lo_relaxed)
        & (pl.col(value_col) < hi_relaxed)
    )

    return df.with_columns(
        pl.when(sticky)
        .then(pl.col("_prev_tier"))
        .otherwise(pl.col("_naive_tier"))
        .alias(out_col)
    ).drop(["_naive_tier", "_prev_tier", "_lo", "_hi"])


def add_rank(df: pl.DataFrame, tier_col: str, tiers) -> pl.DataFrame:
    """Numeric twin so segments can do >= instead of a long is-one-of list."""
    mapping = {label: i + 1 for i, (label, _, _) in enumerate(tiers)}
    return df.with_columns(
        pl.col(tier_col)
        .replace_strict(mapping, default=None)
        .cast(pl.Int32)
        .alias(f"{tier_col}Rank")
    )


def prepare(df: pl.DataFrame, id_field: str = "email") -> pl.DataFrame:
    """Enforce schema, format temporals, drop unidentifiable rows."""
    missing = set(FIELD_SCHEMA) - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    df = df.select(
        [pl.col(c).cast(dtype, strict=True) for c, dtype in FIELD_SCHEMA.items()]
    )

    # Temporal -> Iterable's expected string format.
    temporal_exprs = []
    for name, dtype in df.schema.items():
        if isinstance(dtype, pl.Datetime):
            expr = pl.col(name)
            if dtype.time_zone is not None:
                expr = expr.dt.convert_time_zone("UTC").dt.replace_time_zone(None)
            temporal_exprs.append(expr.dt.strftime(ITERABLE_DT).alias(name))
        elif dtype == pl.Date:
            temporal_exprs.append(pl.col(name).dt.strftime("%Y-%m-%d").alias(name))
    if temporal_exprs:
        df = df.with_columns(temporal_exprs)

    df = df.rename(FIELD_RENAMES)

    key = "email" if id_field == "email" else "userId"
    before = df.height
    df = df.filter(
        pl.col(key).is_not_null() & (pl.col(key).str.strip_chars() != "")
    ).unique(subset=[key], keep="last")
    if before != df.height:
        log.warning("dropped %d rows: null/blank/duplicate %s", before - df.height, key)

    if key == "email":
        df = df.with_columns(pl.col("email").str.to_lowercase().str.strip_chars())

    return df


# ---------- delta detection ----------------------------------------------


def row_hash(df: pl.DataFrame) -> pl.DataFrame:
    """Stable content hash so reruns only push changed profiles."""
    payload = pl.concat_str(
        [pl.col(c).cast(pl.Utf8).fill_null("\x00") for c in sorted(df.columns)],
        separator="\x1f",
    )
    return df.with_columns(
        payload.map_elements(
            lambda s: hashlib.sha256(s.encode()).hexdigest(), return_dtype=pl.Utf8
        ).alias("_row_hash")
    )


def changed_only(df: pl.DataFrame, state_path: str, key: str) -> pl.DataFrame:
    df = row_hash(df)
    if os.path.exists(state_path):
        prev = pl.read_parquet(state_path)
        df_out = (
            df.join(prev, on=key, how="left", suffix="_prev")
            .filter(
                pl.col("_row_hash_prev").is_null()
                | (pl.col("_row_hash") != pl.col("_row_hash_prev"))
            )
            .drop("_row_hash_prev")
        )
    else:
        df_out = df
    return df_out


# ---------- payload construction -----------------------------------------


def to_users(df: pl.DataFrame, id_field: str) -> list[dict]:
    key = "email" if id_field == "email" else "userId"
    users = []
    for row in df.drop("_row_hash").to_dicts():
        ident = row.pop(key)
        # Nulls are omitted, not sent. Sending null does not reliably clear a
        # field in Iterable, and it can trip type inference on first write.
        data_fields = {k: v for k, v in row.items() if v is not None}
        user = {key: ident, "dataFields": data_fields, "mergeNestedObjects": True}
        if key == "userId":
            user["preferUserId"] = True  # only honored on email-based projects
        users.append(user)
    return users


def batches(users: list[dict], size: int = BATCH_SIZE):
    for i in range(0, len(users), size):
        yield users[i : i + size]


# ---------- transport -----------------------------------------------------


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Api-Key": API_KEY, "Content-Type": "application/json"})
    return s


def send_batch(
    session: requests.Session, batch: list[dict], attempt_cap: int = 6
) -> dict:
    url = f"{API_BASE}/api/users/bulkUpdate"
    body = {"users": batch}

    for attempt in range(attempt_cap):
        try:
            resp = session.post(url, json=body, timeout=90)
        except requests.RequestException as exc:
            if attempt == attempt_cap - 1:
                raise
            log.warning("network error, retrying: %s", exc)
        else:
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt == attempt_cap - 1:
                    resp.raise_for_status()
                log.warning("HTTP %s, backing off", resp.status_code)
            elif resp.ok:
                return resp.json()
            else:
                # 4xx other than 429 will not fix itself: surface the body.
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:2000]}")

        time.sleep(min(2**attempt, 30) + random.uniform(0, 1))

    raise RuntimeError("exhausted retries")


def sync(df: pl.DataFrame, id_field: str = "email", dry_run: bool = False) -> Counter:
    users = to_users(df, id_field)
    log.info(
        "prepared %d users in %d batches", len(users), -(-len(users) // BATCH_SIZE)
    )

    if dry_run:
        with open("iterable_payload.ndjson", "w") as fh:
            for u in users:
                fh.write(json.dumps(u) + "\n")
        log.info("dry run: wrote iterable_payload.ndjson, sent nothing")
        return Counter()

    tally = Counter()
    session = make_session()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(send_batch, session, b): i for i, b in enumerate(batches(users))
        }
        for fut in as_completed(futures):
            idx = futures[fut]
            result = fut.result()
            # bulkUpdate does not report per-record failures, so log the whole
            # response body and count everything it does hand back.
            log.info("batch %d response: %s", idx, json.dumps(result))
            for k, v in result.items():
                if isinstance(v, int):
                    tally[k] += v
                elif isinstance(v, list) and v:
                    tally[f"{k}_count"] += len(v)
                    log.warning("batch %d %s: %s", idx, k, v[:20])
    return tally


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    df = pl.read_parquet("user_profiles.parquet")  # or however you materialize it
    prepared = prepare(df, id_field="email")
    delta = changed_only(prepared, "state/last_sync.parquet", key="email")

    log.info("%d of %d profiles changed", delta.height, prepared.height)
    summary = sync(delta, id_field="email", dry_run=bool(os.environ.get("DRY_RUN")))
    log.info("summary: %s", dict(summary))

    if not os.environ.get("DRY_RUN"):
        os.makedirs("state", exist_ok=True)
        prepared.pipe(row_hash).select(["email", "_row_hash"]).write_parquet(
            "state/last_sync.parquet"
        )
