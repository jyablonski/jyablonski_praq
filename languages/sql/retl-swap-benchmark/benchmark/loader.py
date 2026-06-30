"""Bulk load via COPY and index creation."""

import csv
import os
import time
from collections.abc import Iterator
from pathlib import Path

import psycopg
from psycopg import sql

from benchmark.schema import get_columns


def bulk_load(conn, table_name: str, rows: Iterator[tuple]) -> float:
    """Load rows into table using COPY FROM STDIN (streaming). Returns elapsed seconds."""
    columns = [name for name, _ in get_columns()]
    col_list = ", ".join(columns)

    start = time.perf_counter()
    with conn.cursor() as cur:
        with cur.copy(f"COPY {table_name} ({col_list}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)
    elapsed = time.perf_counter() - start
    return elapsed


def generate_csv(rows: Iterator[tuple], csv_path: Path) -> tuple[float, float]:
    """Write rows to a CSV file. Returns elapsed seconds."""
    columns = [name for name, _ in get_columns()]

    start = time.perf_counter()
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)
    elapsed = time.perf_counter() - start

    size_mb = os.path.getsize(csv_path) / (1024 * 1024)
    return elapsed, size_mb


def bulk_load_from_csv(conn, table_name: str, csv_path: Path) -> float:
    """Load rows from CSV file using COPY FROM STDIN.

    Reads the CSV file and streams it into Postgres via COPY.
    This simulates what aws_s3.table_import_from_s3() does on RDS —
    Postgres reads from a file rather than receiving row-by-row from Python.

    Returns elapsed seconds.
    """
    columns = [name for name, _ in get_columns()]
    col_list = ", ".join(columns)

    start = time.perf_counter()
    with open(csv_path, "rb") as f:
        # Skip header row
        f.readline()
        with conn.cursor() as cur:
            with cur.copy(
                f"COPY {table_name} ({col_list}) FROM STDIN WITH (FORMAT csv)"
            ) as copy:
                while chunk := f.read(8 * 1024 * 1024):  # 8MB chunks
                    copy.write(chunk)
    elapsed = time.perf_counter() - start
    return elapsed


def create_indexes(conn, table_name: str) -> float:
    """Add primary key and indexes after bulk load. Returns elapsed seconds."""
    start = time.perf_counter()
    conn.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY (user_id)")
    elapsed = time.perf_counter() - start
    return elapsed
