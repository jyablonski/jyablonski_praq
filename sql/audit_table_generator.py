from datetime import datetime
import os

import pandas as pd
from sqlalchemy import exc, create_engine, text as sql_text
from sqlalchemy.engine.base import Connection, Engine


def sql_connection(
    rds_schema: str,
    RDS_USER: str = os.environ.get("RDS_USER"),
    RDS_PW: str = os.environ.get("RDS_PW"),
    RDS_IP: str = os.environ.get("IP"),
    RDS_DB: str = os.environ.get("RDS_DB"),
) -> Engine:
    """
    SQL Connection function to define the SQL Driver + connection variables needed to connect to the DB.
    This doesn't actually make the connection, use conn.connect() in a context manager to create 1 re-usable connection

    Args:
        rds_schema (str): The Schema in the DB to connect to.

    Returns:
        SQL Connection variable to a specified schema in my PostgreSQL DB
    """
    try:
        connection = create_engine(
            f"postgresql+psycopg2://{RDS_USER}:{RDS_PW}@{RDS_IP}:5432/{RDS_DB}",
            connect_args={"options": f"-csearch_path={rds_schema}"},
            # defining schema to connect to
            echo=False,
            isolation_level="AUTOCOMMIT",
        )
        print(f"SQL Engine for schema: {rds_schema} Successful")
        return connection
    except exc.SQLAlchemyError as e:
        print(f"SQL Engine for schema: {rds_schema} Failed, Error: {e}")
        return e


schema = "nba_prod"
table = "rest_api_users"


def build_audit_table(
    table: str,
    schema: str,
    connection: Connection,
):
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
            CREATE OR REPLACE FUNCTION {table}_audit_trigger_function()
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
        for each row execute function {table}_audit_trigger_function();
        """
        connection.execute(sql_text(f"{audit_trigger_attach_function}"))

        print(f"Built Audit Trigger {table}_audit_trigger")

        return audit_trigger_create_function

    except BaseException as e:
        raise e


engine = sql_connection("nba_prod")

connection = engine.connect()

bb = build_audit_table(
    table="user_predictions", schema="nba_prod", connection=connection
)


text_file = open("audit.txt", "w")
n = text_file.write(bb)
text_file.close()
