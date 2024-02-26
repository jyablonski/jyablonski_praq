import duckdb


def setup_aws_creds(
    conn: duckdb.DuckDBPyConnection,
    access_key: str,
    secret_key: str,
    aws_region: str = "us-east-1",
) -> None:
    conn.execute(
        f"""
        INSTALL httpfs;
        LOAD httpfs;
        SET s3_region='{aws_region}';
        SET s3_access_key_id='{access_key}';
        SET s3_secret_access_key='{secret_key}';
    """
    )
    return None


def setup_postgres(
    conn: duckdb.DuckDBPyConnection,
    username: str,
    password: str,
    host: str,
    database: str,
    duck_db_alias: str = "jacob_db",
) -> None:
    conn.execute(
        f"""
        INSTALL postgres;
        LOAD postgres;
        ATTACH 'dbname={database} user={username} password={password} host={host}' AS {duck_db_alias} (TYPE postgres);
    """
    )
    return None


def setup_tpch(
    conn: duckdb.DuckDBPyConnection,
) -> None:
    conn.execute(
        f"""
        INSTALL tpch;
        LOAD tpch;
        CALL dbgen(sf = 1);
    """
    )
    return None
