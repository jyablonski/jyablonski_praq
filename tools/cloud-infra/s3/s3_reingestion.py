import os

import awswrangler as wr
import boto3
import pandas as pd
from sqlalchemy import exc, create_engine
from sqlalchemy.engine.base import Engine

possible_buckets = [
    "adv_stats",
    "boxscores",
    "injury_data",
    "odds",
    "opp_stats",
    "pbp_data",
    "reddit_comment_data",
    "reddit_data",
    "schedule",
    "shooting_stats",
    "stats",
    "transactions",
    "twitter_data",
    "twitter_tweepy_data",
]


def sql_connection(rds_schema: str) -> Engine:
    """
    SQL Connection function to define the SQL Driver + connection variables needed to connect to the DB.
    This doesn't actually make the connection, use conn.connect() in a context manager to create 1 re-usable connection
    Args:
        rds_schema (str): The Schema in the DB to connect to.
    Returns:
        SQL Connection variable to a specified schema in my PostgreSQL DB
    """
    RDS_USER = os.environ.get("RDS_USER")
    RDS_PW = os.environ.get("RDS_PW")
    RDS_IP = os.environ.get("IP")
    RDS_DB = os.environ.get("RDS_DB")
    try:
        connection = create_engine(
            f"postgresql+psycopg2://{RDS_USER}:{RDS_PW}@{RDS_IP}:5432/{RDS_DB}",
            connect_args={"options": f"-csearch_path={rds_schema}"},
            # defining schema to connect to
            echo=False,
        )
        print(f"SQL Connection to schema: {rds_schema} Successful")
        return connection
    except exc.SQLAlchemyError as e:
        print(f"SQL Connection to schema: {rds_schema} Failed, Error: {e}")
        return e


def write_to_sql(con, table_name: str, df: pd.DataFrame, table_type: str) -> None:
    """
    SQL Table function to write a pandas data frame in aws_dfname_source format
    Args:
        con (SQL Connection): The connection to the SQL DB.
        table_name (str): The Table name to write to SQL as.
        df (DataFrame): The Pandas DataFrame to store in SQL
        table_type (str): Whether the table should replace or append to an existing SQL Table under that name
    Returns:
        Writes the Pandas DataFrame to a Table in Snowflake in the {nba_source} Schema we connected to.
    """
    try:
        if len(df) == 0:
            print(f"{table_name} is empty, not writing to SQL")
        else:
            df.to_sql(
                con=con,
                name=f"aws_{table_name}_source",
                index=False,
                if_exists=table_type,
            )
            print(
                f"Writing {len(df)} {table_name} rows to aws_{table_name}_source to SQL"
            )
    except BaseException as error:
        print(f"SQL Write Script Failed, {error}")


class PrefixException(Exception):
    pass


def reprocess_bucket(bucket: str, prefix: str, conn: Engine):
    try:
        if prefix.endswith("/"):
            raise PrefixException(
                "Please Remove the trailing / on the prefix parameter"
            )
        s3_resource = boto3.resource("s3")
        s3_keys = list(
            f"{bucket}/{i.key}"
            for i in s3_resource.Bucket(bucket).objects.filter(Prefix=f"{prefix}/")
        )  # make sure it ends with /
        # s3_keys = s3_keys[:3]
        for i in s3_keys:
            print(f"Reading in {i}, storing to SQL ...")
            df = wr.s3.read_parquet(f"s3://{i}")
            write_to_sql(conn, prefix, df, "append")

    except BaseException as e:
        print(f"Error Occurred, {e}")


# took 4 mins 30 seconds to re-upload ~ 1 month of data.
conn = sql_connection("s3_ingestion_prac")
reprocess_bucket("jacobsbucket97", "boxscores", conn)
