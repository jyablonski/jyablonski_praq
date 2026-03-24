"""CLI entry point for RETL swap benchmark."""

import time
import threading
from pathlib import Path

import click
import psycopg

from benchmark.config import Config
from benchmark.schema import create_table, drop_table, TABLE_NAME, STAGING_TABLE_NAME
from benchmark.generate import generate_rows, generate_merge_rows
from benchmark.loader import bulk_load, bulk_load_from_csv, generate_csv, create_indexes
from benchmark.swap import atomic_swap
from benchmark.merge import merge_upsert
from benchmark.verify import verify_row_count, verify_sample_data

CSV_DIR = Path(__file__).parent.parent / "data"


def _print_header(row_count: int):
    click.echo(f"\n{'=' * 60}")
    click.echo(f"  RETL Swap Benchmark ({row_count:,} rows, 21 columns)")
    click.echo(f"{'=' * 60}\n")


def _create_staging_no_pk(conn):
    """Create staging table without primary key for faster COPY."""
    conn.execute(f"""
        CREATE TABLE {STAGING_TABLE_NAME} (
            user_id BIGINT,
            page_views INTEGER NOT NULL DEFAULT 0,
            sessions INTEGER NOT NULL DEFAULT 0,
            email_opens INTEGER NOT NULL DEFAULT 0,
            email_clicks INTEGER NOT NULL DEFAULT 0,
            push_sends INTEGER NOT NULL DEFAULT 0,
            engagement_score DOUBLE PRECISION,
            churn_risk DOUBLE PRECISION,
            lifetime_value DOUBLE PRECISION,
            open_rate DOUBLE PRECISION,
            click_rate DOUBLE PRECISION,
            audience_segment VARCHAR(50),
            lifecycle_stage VARCHAR(50),
            acquisition_source VARCHAR(50),
            preferred_platform VARCHAR(50),
            content_affinity VARCHAR(50),
            is_subscriber BOOLEAN NOT NULL DEFAULT FALSE,
            is_active BOOLEAN NOT NULL DEFAULT FALSE,
            has_mobile_app BOOLEAN NOT NULL DEFAULT FALSE,
            last_seen_at TIMESTAMP WITH TIME ZONE,
            last_email_at TIMESTAMP WITH TIME ZONE
        )
    """)


def _run_atomicity_check(conn, config, swap_fn):
    """Run concurrent reader during swap and return (swap_time, counts, errors)."""
    reader_conn = psycopg.connect(config.conninfo, autocommit=True)
    counts = []
    errors = []
    stop = threading.Event()

    def read_loop():
        while not stop.is_set():
            try:
                c = reader_conn.execute(
                    f"SELECT count(*) FROM {TABLE_NAME}"
                ).fetchone()[0]
                counts.append(c)
            except Exception as e:
                errors.append(str(e))
            time.sleep(0.001)

    reader_thread = threading.Thread(target=read_loop)
    reader_thread.start()
    time.sleep(0.05)

    swap_time = swap_fn()

    time.sleep(0.05)
    stop.set()
    reader_thread.join(timeout=5)
    reader_conn.close()

    return swap_time, counts, errors


def _print_correctness(conn, config, staging_config, counts, errors):
    """Verify and print correctness results."""
    row_ok = verify_row_count(conn, TABLE_NAME, config.row_count)
    sample_ok = verify_sample_data(conn, TABLE_NAME, staging_config, sample_size=1000)
    atomicity_ok = len(errors) == 0 and all(c == config.row_count for c in counts)

    status = "PASS" if (row_ok and sample_ok and atomicity_ok) else "FAIL"
    click.echo(f"  Correctness:     {'✓' if status == 'PASS' else '✗'} {status}")
    if not row_ok:
        click.echo("    - Row count mismatch!")
    if not sample_ok:
        click.echo("    - Sample data mismatch!")
    if not atomicity_ok:
        click.echo(
            f"    - Atomicity failed! Errors: {errors}, Unexpected counts: {set(counts) - {config.row_count}}"
        )
    click.echo(
        f"  Reader observations: {len(counts)} reads, all saw {config.row_count:,} rows: {atomicity_ok}"
    )
    return status


def _run_swap_benchmark(conn, config: Config) -> dict:
    """Run the atomic swap benchmark with streaming COPY. Returns timing dict."""
    click.echo("Phase 1a: Atomic Swap (streaming COPY FROM STDIN)")
    click.echo("-" * 40)

    # Step 1: Populate main table (simulates yesterday's data)
    click.echo("  Loading initial data into main table...")
    drop_table(conn, TABLE_NAME)
    create_table(conn, TABLE_NAME)
    drop_table(conn, STAGING_TABLE_NAME)
    initial_load = bulk_load(conn, TABLE_NAME, generate_rows(config))
    click.echo(f"  Initial load:    {initial_load:.1f}s")

    # Step 2: Load staging table via streaming COPY
    click.echo("  Loading staging table via streaming COPY...")
    _create_staging_no_pk(conn)
    staging_config = Config(
        row_count=config.row_count,
        seed=config.seed + 1,
        host=config.host,
        port=config.port,
        dbname=config.dbname,
        user=config.user,
        password=config.password,
    )
    load_time = bulk_load(conn, STAGING_TABLE_NAME, generate_rows(staging_config))
    click.echo(f"  COPY load:       {load_time:.1f}s")

    # Step 3: Create indexes on staging
    click.echo("  Creating indexes on staging...")
    index_time = create_indexes(conn, STAGING_TABLE_NAME)
    click.echo(f"  Index creation:  {index_time:.1f}s")

    # Step 4: Atomic swap with concurrent reader
    click.echo("  Testing atomicity with concurrent reader...")
    swap_time, counts, errors = _run_atomicity_check(
        conn, config, lambda: atomic_swap(conn, TABLE_NAME, STAGING_TABLE_NAME)
    )

    click.echo(f"  Swap (RENAME):   {swap_time * 1000:.3f}ms")
    click.echo(f"  Total:           {load_time + index_time + swap_time:.1f}s")

    status = _print_correctness(conn, config, staging_config, counts, errors)

    return {
        "load_time": load_time,
        "index_time": index_time,
        "swap_time": swap_time,
        "total_time": load_time + index_time + swap_time,
        "correctness": status,
    }


def _run_csv_swap_benchmark(conn, config: Config) -> dict:
    """Run the atomic swap benchmark with CSV file COPY. Returns timing dict."""
    click.echo("\nPhase 1b: Atomic Swap (CSV file COPY)")
    click.echo("-" * 40)

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = CSV_DIR / "staging_data.csv"

    # Step 1: Ensure main table exists with data
    click.echo("  Ensuring main table has data...")
    drop_table(conn, TABLE_NAME)
    create_table(conn, TABLE_NAME)
    drop_table(conn, STAGING_TABLE_NAME)
    initial_load = bulk_load(conn, TABLE_NAME, generate_rows(config))
    click.echo(f"  Initial load:    {initial_load:.1f}s")

    # Step 2: Generate CSV file
    staging_config = Config(
        row_count=config.row_count,
        seed=config.seed + 1,
        host=config.host,
        port=config.port,
        dbname=config.dbname,
        user=config.user,
        password=config.password,
    )
    click.echo("  Generating CSV file...")
    csv_time, csv_size_mb = generate_csv(generate_rows(staging_config), csv_path)
    click.echo(f"  CSV generation:  {csv_time:.1f}s ({csv_size_mb:.0f} MB)")

    # Step 3: Load staging table from CSV
    click.echo("  Loading staging table from CSV file...")
    _create_staging_no_pk(conn)
    load_time = bulk_load_from_csv(conn, STAGING_TABLE_NAME, csv_path)
    click.echo(f"  COPY from CSV:   {load_time:.1f}s")

    # Step 4: Create indexes on staging
    click.echo("  Creating indexes on staging...")
    index_time = create_indexes(conn, STAGING_TABLE_NAME)
    click.echo(f"  Index creation:  {index_time:.1f}s")

    # Step 5: Atomic swap with concurrent reader
    click.echo("  Testing atomicity with concurrent reader...")
    swap_time, counts, errors = _run_atomicity_check(
        conn, config, lambda: atomic_swap(conn, TABLE_NAME, STAGING_TABLE_NAME)
    )

    click.echo(f"  Swap (RENAME):   {swap_time * 1000:.3f}ms")
    click.echo(f"  Total (excl CSV gen): {load_time + index_time + swap_time:.1f}s")
    click.echo(
        f"  Total (incl CSV gen): {csv_time + load_time + index_time + swap_time:.1f}s"
    )

    status = _print_correctness(conn, config, staging_config, counts, errors)

    # Clean up CSV
    csv_path.unlink(missing_ok=True)

    return {
        "csv_time": csv_time,
        "csv_size_mb": csv_size_mb,
        "load_time": load_time,
        "index_time": index_time,
        "swap_time": swap_time,
        "total_time_excl_csv": load_time + index_time + swap_time,
        "total_time_incl_csv": csv_time + load_time + index_time + swap_time,
        "correctness": status,
    }


def _run_merge_benchmark(conn, config: Config, overlap_ratios: list[float]) -> dict:
    """Run merge benchmarks for different overlap ratios."""
    click.echo("\nPhase 2: Merge (Upsert)")
    click.echo("-" * 40)

    results = {}
    for ratio in overlap_ratios:
        label = f"{int(ratio * 100)}% overlap"
        click.echo(f"  Running merge with {label}...")

        # Reset table
        drop_table(conn, TABLE_NAME)
        create_table(conn, TABLE_NAME)
        bulk_load(conn, TABLE_NAME, generate_rows(config))

        # Run merge
        merge_rows = generate_merge_rows(config, ratio, config.row_count)
        merge_time = merge_upsert(conn, TABLE_NAME, merge_rows, config.batch_size)

        # Verify — use same math as generate_merge_rows to avoid float drift
        overlap_count = int(config.row_count * ratio)
        new_count = config.row_count - overlap_count
        expected_count = config.row_count + new_count
        row_ok = verify_row_count(conn, TABLE_NAME, expected_count)

        status = "PASS" if row_ok else "FAIL"
        click.echo(f"  {label}:  {merge_time:.1f}s  {'✓' if row_ok else '✗'} {status}")

        results[ratio] = {"merge_time": merge_time, "correctness": status}

    return results


@click.command()
@click.option("--rows", default=16_000_000, help="Number of rows to generate")
@click.option("--seed", default=42, help="Random seed for reproducibility")
@click.option("--host", default="localhost", help="Postgres host")
@click.option("--port", default=5499, help="Postgres port")
@click.option(
    "--skip-swap", is_flag=True, help="Skip Phase 1a (streaming swap benchmark)"
)
@click.option("--skip-csv", is_flag=True, help="Skip Phase 1b (CSV swap benchmark)")
@click.option("--skip-merge", is_flag=True, help="Skip Phase 2 (merge benchmark)")
def main(rows, seed, host, port, skip_swap, skip_csv, skip_merge):
    """Run the RETL swap vs merge benchmark."""
    config = Config(row_count=rows, seed=seed, host=host, port=port)

    _print_header(rows)

    conn = psycopg.connect(config.conninfo, autocommit=True)

    try:
        swap_results = None
        csv_results = None
        merge_results = None

        if not skip_swap:
            swap_results = _run_swap_benchmark(conn, config)

        if not skip_csv:
            csv_results = _run_csv_swap_benchmark(conn, config)

        if not skip_merge:
            merge_results = _run_merge_benchmark(conn, config, [1.0, 0.8, 0.5])

        # Summary
        click.echo(f"\n{'=' * 60}")
        click.echo("  Summary")
        click.echo(f"{'=' * 60}")

        if swap_results:
            click.echo(f"  Streaming swap total:    {swap_results['total_time']:.1f}s")
            click.echo(
                f"  Streaming swap (rename): {swap_results['swap_time'] * 1000:.3f}ms"
            )

        if csv_results:
            click.echo(
                f"  CSV file size:           {csv_results['csv_size_mb']:.0f} MB"
            )
            click.echo(f"  CSV generation:          {csv_results['csv_time']:.1f}s")
            click.echo(f"  CSV COPY load:           {csv_results['load_time']:.1f}s")
            click.echo(
                f"  CSV swap total (excl gen): {csv_results['total_time_excl_csv']:.1f}s"
            )
            click.echo(
                f"  CSV swap total (incl gen): {csv_results['total_time_incl_csv']:.1f}s"
            )

        if swap_results and csv_results:
            speedup = swap_results["load_time"] / csv_results["load_time"]
            click.echo(
                f"  CSV vs streaming COPY:   {speedup:.1f}x {'faster' if speedup > 1 else 'slower'}"
            )

        base_time = None
        if swap_results:
            base_time = swap_results["total_time"]
        elif csv_results:
            base_time = csv_results["total_time_excl_csv"]

        if merge_results and base_time:
            for ratio, data in merge_results.items():
                label = f"{int(ratio * 100)}% overlap"
                speedup = data["merge_time"] / base_time
                click.echo(
                    f"  Merge ({label}): {data['merge_time']:.1f}s ({speedup:.1f}x slower than swap)"
                )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
