"""Merge (upsert) via INSERT ... ON CONFLICT DO UPDATE."""

import time
from collections.abc import Iterator

from benchmark.schema import get_columns


def merge_upsert(
    conn, table_name: str, rows: Iterator[tuple], batch_size: int
) -> float:
    """Upsert rows into table via INSERT ... ON CONFLICT DO UPDATE.

    Returns elapsed seconds.
    """
    columns = [name for name, _ in get_columns()]
    col_list = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    update_cols = [c for c in columns if c != "user_id"]
    update_set = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    upsert_sql = (
        f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT (user_id) DO UPDATE SET {update_set}"
    )

    start = time.perf_counter()

    batch = []
    with conn.cursor() as cur:
        conn.autocommit = False
        try:
            for row in rows:
                batch.append(row)
                if len(batch) >= batch_size:
                    cur.executemany(upsert_sql, batch)
                    batch.clear()
            if batch:
                cur.executemany(upsert_sql, batch)
                batch.clear()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = True

    elapsed = time.perf_counter() - start
    return elapsed
