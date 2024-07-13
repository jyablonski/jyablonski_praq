from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine.base import Connection

from jyablonski_common_modules.sql import sql_connection


def create_and_load_temp_table(
    conn: Connection, df: pd.DataFrame, temp_table_name: str, target_table_name: str
) -> None:
    """
    Function to create a temporary table with the same schema as the target
    SQL table, and will load the DataFrame into the temporary table. This
    temporary table will be used to merge the data into the target table
    via the `merge_dataframe_into_postgres` Function.

    Args:
        conn (Connection): SQLAlchemy connection object.

        df (pd.DataFrame): Pandas DataFrame to load into the temporary table.

        temp_table_name (str): Name of the temporary table.

        target_table_name (str): Name of the target table.

    Returns:
        None, but creates and loads the temporary table in Postgres.

    Raises:
        ValueError: If there is a schema mismatch between the DataFrame
            and the target table. It will list what the missing columns are
            and whether they are in the DataFrame or the target table.
    """
    print(f"Creating Temp Table {temp_table_name}")
    conn.execute(
        text(
            f"""
        CREATE TEMP TABLE {temp_table_name} AS
        SELECT * FROM {target_table_name} LIMIT 0"""
        )
    )

    target_columns = pd.read_sql(
        text(f"SELECT * FROM {temp_table_name} LIMIT 0"), conn
    ).columns.tolist()
    df_columns = df.columns.tolist()

    # this section is exclusively for error handling
    if set(target_columns) != set(df_columns):
        missing_in_target = [col for col in df_columns if col not in target_columns]
        missing_in_df = [col for col in target_columns if col not in df_columns]

        error_message = "Schema Mismatch between DataFrame and Target Table:\n"
        if missing_in_target:
            error_message += (
                f"Columns in DataFrame but not in Target Table: {missing_in_target}\n"
            )
        if missing_in_df:
            error_message += (
                f"Columns in Target Table but not in DataFrame: {missing_in_df}\n"
            )

        raise ValueError(error_message)

    print(f"Loading into Temp Table {temp_table_name}")
    df.to_sql(name=temp_table_name, con=conn, if_exists="append", index=False)

    return None


def merge_temp_table_into_target(
    conn: Connection,
    temp_table_name: str,
    target_table_name: str,
    primary_keys: list[str],
    timestamp_cols: list[str],
) -> None:
    """
    Merge data from the temporary table into the target table using the
    `MERGE` statement in Postgres. This command is available in
    Postgres Version 15+ or higher.

    The function will not update the rows if the non-primary key columns
    and the mutable timestamp column(s) are the same.

    Args:
        conn (Connection): SQLAlchemy connection object.

        temp_table_name (str): Name of the temporary table.

        target_table_name (str): Name of the target table.

        primary_keys (list[str]): List of 1 or more primary key columns
            found in both the DataFrame and the target table.

        timestamp_cols (list[str]): List of timestamp columns. *IMPORTANT*
            This function assumes the first timestamp column is immutable
            such as `created_at` and any subsequent timestamp cols are
            mutable such as `updated_at`.

    Returns:
        None, but performs the Merge operation in Postgres.

    Raises:
        ValueError: If there is a schema mismatch between the DataFrame
            and the target table
    """
    # Fetch columns from the temporary table to dynamically generate the SQL parts
    columns = pd.read_sql(
        sql=text(f"SELECT * FROM {temp_table_name} LIMIT 0"), con=conn
    ).columns.tolist()

    missing_columns = [
        col for col in primary_keys + timestamp_cols if col not in columns
    ]
    if missing_columns:
        raise ValueError(
            f"Missing Columns {missing_columns}, Please double check \
            the Columns in `primary_keys` and `timestamp_cols` are in \
            the DataFrame and Target Table."
        )

    target_id = "target"
    source_id = "source"

    # matching source to target based on 1 or more primary keys
    match_condition = " AND ".join(
        [f"{target_id}.{key} = {source_id}.{key}" for key in primary_keys]
    )

    # if matched, then update every column except the primary key
    # and the immutable timestamp col
    update_clause = ", ".join(
        [
            f"{col} = {source_id}.{col}"
            for col in columns
            if col not in timestamp_cols[0] and col not in primary_keys
        ]
    )

    # building the insert statement
    insert_columns = ", ".join(columns)
    insert_values = ", ".join([f"{source_id}.{col}" for col in columns])

    # if the non primary key + timestamp columns are the same, then dont update the rows
    columns_to_compare = [
        col for col in columns if col not in primary_keys + timestamp_cols
    ]
    match_condition_unchanged = " AND ".join(
        [f"{target_id}.{col} = {source_id}.{col}" for col in columns_to_compare]
    )

    # this statement doesnt return any rows, so we cant capture
    # the results of the merge here
    print(f"Merging into {target_table_name}")
    merge_statement = f"""
            MERGE INTO {target_table_name} AS {target_id}
            USING {temp_table_name} AS {source_id}
            ON {match_condition}
            WHEN MATCHED AND {match_condition_unchanged} THEN
                DO NOTHING
            WHEN MATCHED THEN
                UPDATE SET {update_clause}
            WHEN NOT MATCHED THEN
                INSERT ({insert_columns})
                VALUES ({insert_values});"""
    try:
        conn.execute(text(merge_statement))
    except BaseException as e:
        print(
            f"Error occurred while Merging: {e} Full Merge Statement: \
              \n {merge_statement}"
        )
        raise e

    return None


def merge_dataframe_into_postgres(
    conn: Connection,
    df: pd.DataFrame,
    target_table_name: str,
    primary_keys: list[str],
    timestamp_cols: list[str],
):
    """
    Primary Function that combines the `create_and_load_temp_table` and
    `merge_temp_table_into_target` functions to merge a DataFrame into a
    Postgres Table.

    Args:
        conn (Connection): SQLAlchemy connection object.

        df (pd.DataFrame): DataFrame to load into the temporary table.

        target_table_name (str): Name of the target table.

        primary_keys (list[str]): List of 1 or more primary key columns
            found in both the DataFrame and the target table.

        timestamp_cols (list[str]): List of timestamp columns. *IMPORTANT*
            This function assumes the first timestamp column is immutable
            such as `created_at` and any subsequent timestamp cols are
            mutable such as `updated_at`.

    Returns:
        None, but performs the Merge operation in Postgres.
    """
    temp_table_name = f"temp_{target_table_name}"

    create_and_load_temp_table(
        conn=conn,
        df=df,
        temp_table_name=temp_table_name,
        target_table_name=target_table_name,
    )
    merge_temp_table_into_target(
        conn=conn,
        temp_table_name=temp_table_name,
        target_table_name=target_table_name,
        primary_keys=primary_keys,
        timestamp_cols=timestamp_cols,
    )

    return None


# Example usage:
if __name__ == "__main__":
    engine = sql_connection(
        database="postgres",
        schema="source",
        user="postgres",
        pw="postgres",
        host="localhost",
    )
    modified_at = datetime.now(timezone.utc)

    data = {
        "customer_id": [1, 2, 3, 4],
        "customer_name": [
            "Johnny Allstar",
            "Aubrey Plaza",
            "John Wick",
            "Tester McTesterson",
        ],
        "customer_email": [
            "johnny@allstar.com",
            "customer2@example.com",
            "john@wick.com",
            "tester@mctesterson.com",
        ],
        "created_at": [
            "2023-01-01 01:00:00",
            "2023-01-01 01:00:00",
            "2023-01-01 01:00:00",
            modified_at,
        ],
        "updated_at": [modified_at, modified_at, modified_at, modified_at],
    }
    df = pd.DataFrame(data)
    target_table_name = "customers"
    primary_keys = ["customer_id"]
    timestamp_cols = ["created_at", "updated_at"]

    with engine.begin() as conn:
        merge_dataframe_into_postgres(
            conn=conn,
            df=df,
            target_table_name=target_table_name,
            primary_keys=primary_keys,
            timestamp_cols=timestamp_cols,
        )
