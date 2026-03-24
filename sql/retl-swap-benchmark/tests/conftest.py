import pytest
import psycopg

from benchmark.config import Config


@pytest.fixture(scope="session")
def config():
    return Config(row_count=1_000)


@pytest.fixture(scope="session")
def db_conn(config):
    conn = psycopg.connect(config.conninfo, autocommit=True)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_tables(db_conn):
    """Drop all user_analytics tables before each test."""
    db_conn.execute("DROP TABLE IF EXISTS user_analytics CASCADE")
    db_conn.execute("DROP TABLE IF EXISTS user_analytics_staging CASCADE")
    db_conn.execute("DROP TABLE IF EXISTS user_analytics_old CASCADE")
    yield
    db_conn.execute("DROP TABLE IF EXISTS user_analytics CASCADE")
    db_conn.execute("DROP TABLE IF EXISTS user_analytics_staging CASCADE")
    db_conn.execute("DROP TABLE IF EXISTS user_analytics_old CASCADE")
