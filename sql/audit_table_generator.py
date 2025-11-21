import os

import pandas as pd
from sqlalchemy import text as sql_text
from sqlalchemy.engine.base import Connection

from jyablonski_common_modules.sql import create_sql_engine


def build_audit_table(
    table: str,
    schema: str,
    connection: Connection,
):
    """
    Build audit table and trigger for a given table.
    Now with schema-qualified references to avoid issues when moving schemas.
    """
    try:
        table_cols_df = pd.read_sql_query(
            sql=sql_text(
                f"""
            select column_name, data_type
            from information_schema.columns
            where table_schema = '{schema}' and table_name = '{table}'"""
            ),
            con=connection,
        )
        table_cols_df["col_statement"] = (
            table_cols_df["column_name"] + " " + table_cols_df["data_type"]
        )

        table_cols_create_statement = ", ".join(
            [col for col in table_cols_df["col_statement"]]
        )

        connection.execute(
            sql_text(
                f"""
        create table if not exists {schema}.{table}_audit(
            audit_id serial primary key,
            {table_cols_create_statement},
            audit_type varchar not null,
            audit_created_at timestamp default current_timestamp
        );"""
            )
        )
        print(f"Built Table {schema}.{table}_audit")

        table_cols = ", ".join([col for col in table_cols_df["column_name"]])

        table_cols_new = ", ".join(
            [f"NEW.{col}" for col in table_cols_df["column_name"]]
        )
        table_cols_update = table_cols_new.replace("NEW.id", "OLD.id").replace(
            "NEW.created", "OLD.created"
        )
        table_cols_old = ", ".join(
            [f"OLD.{col}" for col in table_cols_df["column_name"]]
        )

        audit_trigger_create_function = f"""
            CREATE OR REPLACE FUNCTION {schema}.{table}_audit_trigger_function()
            RETURNS trigger AS $body$
            BEGIN
            if (TG_OP = 'INSERT') then
                INSERT INTO {schema}.{table}_audit (
                    {table_cols},
                    audit_type,
                    audit_created_at
                )
                VALUES(
                    {table_cols_new},
                    'INSERT',
                    CURRENT_TIMESTAMP
                );
                        
                RETURN NEW;
            elsif (TG_OP = 'UPDATE') then
                INSERT INTO {schema}.{table}_audit (
                    {table_cols},
                    audit_type,
                    audit_created_at
                )
                VALUES(
                    {table_cols_update},
                    'UPDATE',
                    CURRENT_TIMESTAMP
                );
                        
                RETURN NEW;
            elsif (TG_OP = 'DELETE') then
                INSERT INTO {schema}.{table}_audit (
                    {table_cols},
                    audit_type,
                    audit_created_at
                )
                VALUES(
                    {table_cols_old},
                    'DELETE',
                    CURRENT_TIMESTAMP
                );
                    
                RETURN OLD;
            end if;
                
            END;
            $body$
            LANGUAGE plpgsql;"""
        connection.execute(sql_text(f"{audit_trigger_create_function}"))

        audit_trigger_attach_function = f"""
        drop trigger if exists {table}_audit_trigger on {schema}.{table};

        create trigger {table}_audit_trigger
        after insert or update or delete on {schema}.{table}
        for each row execute function {schema}.{table}_audit_trigger_function();
        """
        connection.execute(sql_text(f"{audit_trigger_attach_function}"))

        print(f"Built Audit Trigger {table}_audit_trigger on {schema}.{table}")

        return audit_trigger_create_function

    except BaseException as e:
        raise e


if __name__ == "__main__":
    engine = create_sql_engine(
        database=os.environ.get("RDS_DB"),
        schema="nba_source",
        user=os.environ.get("RDS_USER"),
        password=os.environ.get("RDS_PW"),
        host=os.environ.get("IP"),
        port=17841,
    )
    connection = engine.connect()

    silver_tables = ["ml_tonights_games"]

    for table in silver_tables:
        print(f"\n--- Processing {table} in silver schema ---")
        build_audit_table(table=table, schema="silver", connection=connection)

    gold_tables = ["feature_flags", "incidents", "rest_api_users", "user_predictions"]

    for table in gold_tables:
        print(f"\n--- Processing {table} in gold schema ---")
        build_audit_table(table=table, schema="gold", connection=connection)
