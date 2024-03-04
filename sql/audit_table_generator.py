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

bb = build_audit_table(table="rest_api_users", schema="nba_prod", connection=connection)


text_file = open("audit.txt", "w")
n = text_file.write(bb)
text_file.close()


# didnt finish this mfer
def build_audit_table_mysql(
    table: str,
    schema: str,
    connection: Connection,
) -> tuple[str, str]:
    try:
        cursor = connection.cursor()

        # Get column names and data types
        cursor.execute(
            f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
            """
        )
        table_cols = cursor.fetchall()

        # Construct CREATE TABLE statement
        # col_statements = [
        #     f"{col_name} {data_type}" for col_name, data_type in table_cols
        # ]
        # table_cols_create_statement = ", ".join(col_statements)

        # cursor.execute(
        #     f"""
        #     CREATE TABLE IF NOT EXISTS {schema}.{table}_audit (
        #         audit_id INT AUTO_INCREMENT PRIMARY KEY,
        #         {table_cols_create_statement},
        #         audit_type VARCHAR(10) NOT NULL,
        #         audit_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        #     )
        #     """
        # )
        # print(f"Built Table {schema}.{table}_audit")

        # Construct trigger function
        table_cols_str = ", ".join([col_name for col_name, _ in table_cols])
        table_cols_new = ", ".join([f"NEW.{col_name}" for col_name, _ in table_cols])
        table_cols_old = ", ".join([f"OLD.{col_name}" for col_name, _ in table_cols])

        audit_trigger_create_function = f"""
            drop trigger if exists {table}_audit_insert_trigger;
            
            create trigger {table}_audit_insert_trigger
            after insert
            on {table}
            for each row
            insert into {table}_Audit (
                {table_cols_str},
                audit_type,
                audit_created_at
            )
            values (
                {table_cols_new},
                'INSERT',
                CURRENT_TIMESTAMP
            );

            """
        cursor.execute(audit_trigger_create_function)
        print(f"Created Trigger {table}_audit_insert_trigger")

        audit_trigger_update_function = f"""
            drop trigger if exists {table}_audit_update_trigger;
            
            create trigger {table}_audit_update_trigger
            after update
            on {table}
            for each row
            insert into {table}_Audit (
                {table_cols_str},
                audit_type,
                audit_created_at
            )
            values (
                {table_cols_new},
                'UPDATE',
                CURRENT_TIMESTAMP
            );

            """
        cursor.execute(audit_trigger_update_function)
        print(f"Created Trigger Function {table}_audit_trigger_function")

        audit_trigger_delete_function = f"""
            drop trigger if exists {table}_audit_delete_trigger;
            
            create trigger {table}_audit_delete_trigger
            after delete
            on {table}
            for each row
            insert into {table}_Audit (
                {table_cols_str},
                audit_type,
                audit_created_at
            )
            values (
                {table_cols_old},
                'DELETE',
                CURRENT_TIMESTAMP
            );

            """
        cursor.execute(audit_trigger_delete_function)
        print(f"Created Trigger Function {table}_audit_trigger_function")

        connection.commit()
        cursor.close()

        return (
            audit_trigger_create_function,
            audit_trigger_update_function,
            audit_trigger_delete_function,
        )

    except Exception as e:
        connection.rollback()
        raise e
