"""Correctness verification for benchmark results."""

import random

from benchmark.config import Config
from benchmark.generate import generate_row


def verify_row_count(conn, table_name: str, expected: int) -> bool:
    """Check that table has exactly the expected number of rows."""
    count = conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]
    return count == expected


def verify_sample_data(
    conn, table_name: str, config: Config, sample_size: int = 1000
) -> bool:
    """Verify a random sample of rows match the generated data.

    Re-generates expected rows using the same seed and compares.
    """
    rng_sample = random.Random(config.seed + 100)
    sample_ids = sorted(
        rng_sample.sample(
            range(1, config.row_count + 1), min(sample_size, config.row_count)
        )
    )

    # Regenerate expected rows for sampled IDs
    # We need to regenerate in sequence since the RNG is sequential
    rng = random.Random(config.seed)
    expected_by_id = {}
    for uid in range(1, config.row_count + 1):
        row = generate_row(user_id=uid, fake=None, rng=rng)
        if uid in sample_ids:
            expected_by_id[uid] = row

    # Fetch actual rows
    placeholders = ", ".join(["%s"] * len(sample_ids))
    actual_rows = conn.execute(
        f"SELECT * FROM {table_name} WHERE user_id IN ({placeholders}) ORDER BY user_id",
        sample_ids,
    ).fetchall()

    for actual in actual_rows:
        uid = actual[0]
        expected = expected_by_id[uid]
        # Compare all non-timestamp fields (timestamps may have tz formatting diffs)
        for i in range(len(expected) - 2):  # Skip last 2 timestamp columns
            if actual[i] != expected[i]:
                print(
                    f"Mismatch at user_id={uid}, col {i}: actual={actual[i]} expected={expected[i]}"
                )
                return False

    return True
