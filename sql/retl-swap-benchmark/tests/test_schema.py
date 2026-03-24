import psycopg

from benchmark.config import Config
from benchmark.schema import create_table, get_columns, TABLE_NAME, STAGING_TABLE_NAME


def test_create_table_creates_with_correct_columns(db_conn, config):
    create_table(db_conn, TABLE_NAME)

    cols = db_conn.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position",
        [TABLE_NAME],
    ).fetchall()
    col_names = [r[0] for r in cols]

    expected = get_columns()
    assert col_names == [c[0] for c in expected]


def test_create_staging_table(db_conn, config):
    create_table(db_conn, STAGING_TABLE_NAME)

    count = db_conn.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = %s",
        [STAGING_TABLE_NAME],
    ).fetchone()[0]
    assert count == 1


def test_create_table_has_primary_key(db_conn, config):
    create_table(db_conn, TABLE_NAME)

    pk = db_conn.execute(
        """
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary
        """,
        [TABLE_NAME],
    ).fetchall()
    assert [r[0] for r in pk] == ["user_id"]
