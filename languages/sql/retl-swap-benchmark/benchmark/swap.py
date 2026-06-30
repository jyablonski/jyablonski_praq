"""Atomic table swap via ALTER TABLE RENAME."""

import time

import psycopg


OLD_SUFFIX = "_old"


def atomic_swap(conn, main_table: str, staging_table: str) -> float:
    """Atomically swap staging table into main table position.

    In a single transaction:
    1. Rename main -> main_old
    2. Rename staging -> main

    Then drop the old table outside the transaction.

    Returns elapsed seconds for the rename transaction only.
    """
    old_table = f"{main_table}{OLD_SUFFIX}"

    # Drop any leftover old table
    conn.execute(f"DROP TABLE IF EXISTS {old_table} CASCADE")

    start = time.perf_counter()

    # autocommit must be off for the transaction block
    conn.autocommit = False
    try:
        conn.execute(f"ALTER TABLE {main_table} RENAME TO {old_table}")
        conn.execute(f"ALTER TABLE {staging_table} RENAME TO {main_table}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True

    elapsed = time.perf_counter() - start

    # Clean up old table outside transaction
    conn.execute(f"DROP TABLE IF EXISTS {old_table} CASCADE")

    return elapsed
