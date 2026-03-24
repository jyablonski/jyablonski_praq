"""Streaming row generator for user_analytics data."""

import random
from collections.abc import Generator

from faker import Faker

from benchmark.config import Config

SEGMENTS = [
    "power_user",
    "casual",
    "dormant",
    "new",
    "returning",
    "at_risk",
    "loyal",
    "churned",
]
LIFECYCLE_STAGES = [
    "awareness",
    "acquisition",
    "activation",
    "retention",
    "revenue",
    "referral",
]
SOURCES = [
    "organic",
    "paid_search",
    "social",
    "email",
    "referral",
    "direct",
    "affiliate",
]
PLATFORMS = ["web", "ios", "android", "email", "push"]
AFFINITIES = [
    "politics",
    "tech",
    "sports",
    "business",
    "health",
    "entertainment",
    "science",
    "lifestyle",
]


def generate_row(user_id: int, fake: Faker | None, rng: random.Random) -> tuple:
    """Generate a single row as a tuple matching the schema column order."""
    return (
        user_id,
        # Integer counts
        rng.randint(0, 10_000),
        rng.randint(0, 500),
        rng.randint(0, 2_000),
        rng.randint(0, 1_000),
        rng.randint(0, 500),
        # Float scores
        round(rng.random(), 4),
        round(rng.random(), 4),
        round(rng.uniform(0, 10_000), 2),
        round(rng.random(), 4),
        round(rng.random(), 4),
        # Varchar segments
        rng.choice(SEGMENTS),
        rng.choice(LIFECYCLE_STAGES),
        rng.choice(SOURCES),
        rng.choice(PLATFORMS),
        rng.choice(AFFINITIES),
        # Boolean flags
        rng.choice([True, False]),
        rng.choice([True, False]),
        rng.choice([True, False]),
        # Timestamps (ISO format strings for COPY)
        f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:00+00:00",
        f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:00+00:00",
    )


def generate_rows(config: Config, start_id: int = 1) -> Generator[tuple, None, None]:
    """Yield row tuples for the configured number of rows."""
    rng = random.Random(config.seed)
    for i in range(start_id, start_id + config.row_count):
        yield generate_row(user_id=i, fake=None, rng=rng)


def generate_merge_rows(
    config: Config,
    overlap_ratio: float,
    existing_max_id: int,
) -> Generator[tuple, None, None]:
    """Generate rows for merge benchmark with specified overlap ratio.

    Args:
        config: Benchmark config.
        overlap_ratio: 0.0 to 1.0 — fraction of rows that match existing user_ids.
        existing_max_id: The highest user_id in the existing table.
    """
    rng = random.Random(
        config.seed + 1
    )  # Different seed so values differ from original
    overlap_count = int(config.row_count * overlap_ratio)
    new_count = config.row_count - overlap_count

    # Overlapping rows: reuse existing user_ids (1..overlap_count)
    for uid in range(1, overlap_count + 1):
        yield generate_row(user_id=uid, fake=None, rng=rng)

    # New rows: user_ids starting after existing max
    for uid in range(existing_max_id + 1, existing_max_id + 1 + new_count):
        yield generate_row(user_id=uid, fake=None, rng=rng)
