import os

# pip install --upgrade snowflake-sqlalchemy
# if using sqlalchemy > v2.0, you ahve to wrap sql queries in `text()` ???
from sqlalchemy import create_engine, text, Connection


def create_snowflake_conn(
    user: str,
    password: str,
    account: str,
    database: str,
    schema: str,
    warehouse: str | None = None,  # optional, but useful to include
    role: str | None = None,  # optional
):
    url = f"snowflake://{user}:{password}@{account}/{database}/{schema}"

    if warehouse:
        url += f"?warehouse={warehouse}"
        if role:
            url += f"&role={role}"
    elif role:
        url += f"?role={role}"

    engine = create_engine(url=url)
    conn = engine.connect()
    return conn


def pull_file_cols(
    conn: Connection,
    s3_prefix: str,
    file_format: str = "production.test_schema.parquet_format_tf",
    s3_stage: str = "TEST_SCHEMA.NBA_ELT_STAGE_PROD",
) -> list[tuple[str]]:
    if not s3_prefix.endswith(".parquet"):
        raise ValueError("Only Parquet files are supported")

    query = f"""\
        SELECT * FROM TABLE(
            INFER_SCHEMA(
                LOCATION=>'@{s3_stage}/{s3_prefix}',
                FILE_FORMAT=>'{file_format}',
                IGNORE_CASE=>TRUE)
            );"""

    results = conn.execute(text(query)).fetchall()

    return results


def generate_table_ddl(schema: str, table: str, col_results: list[tuple[str]]):
    col_lines = []
    for col in col_results:
        col_name = col[0]
        data_type = col[1]
        col_lines.append(f"{col_name} {data_type}")

    col_lines.append("metadata_filename VARCHAR NULL")
    col_lines.append("metadata_ingest_time TIMESTAMP NULL")

    col_definitions = ",\n".join(col_lines)

    return f"CREATE OR REPLACE TABLE {schema}.{table} (\n{col_definitions}\n);"


conn = create_snowflake_conn(
    user=os.environ.get("SNOWFLAKE_USER"),
    password=os.environ.get("SNOWFLAKE_PASSWORD"),
    account=os.environ.get("SNOWFLAKE_ACCOUNT"),
    database="production",
    schema="source",
)


results = pull_file_cols(
    conn=conn,
    s3_prefix="boxscores/validated/year=2025/month=04/boxscores-2025-04-01.parquet",
)

table_ddl = generate_table_ddl(
    schema="source",
    table="jacobs_test_table",
    col_results=results,
)

if __name__ == "__main__":
    conn = create_snowflake_conn(
        user=os.environ.get("SNOWFLAKE_USER"),
        password=os.environ.get("SNOWFLAKE_PASSWORD"),
        account=os.environ.get("SNOWFLAKE_ACCOUNT"),
        database="production",
        schema="source",
    )

    results = pull_file_cols(
        conn=conn,
        s3_prefix="boxscores/validated/year=2025/month=04/boxscores-2025-04-01.parquet",
    )

    table_ddl = generate_table_ddl(
        schema="source",
        table="jacobs_test_table",
        col_results=results,
    )

    print(table_ddl)
