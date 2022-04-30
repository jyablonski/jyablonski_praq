import os
import pandas as pd
import boto3
import awswrangler as wr
from datetime import datetime

from sqlalchemy import exc, create_engine


def sql_connection(rds_schema: str):
    """
    SQL Connection function connecting to my postgres db with schema = nba_source where initial data in ELT lands
    Args:
        None
    Returns:
        SQL Connection variable to schema: nba_source in my PostgreSQL DB
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


def write_to_sql(con, table_name: str, df: pd.DataFrame, table_type: str):
    """
    SQL Table function to write a pandas data frame in aws_dfname_source format
    Args:
        data: The Pandas DataFrame to store in SQL
        table_type: Whether the table should replace or append to an existing SQL Table under that name
    Returns:
        Writes the Pandas DataFrame to a Table in Snowflake in the {nba_source} Schema we connected to.
    """
    try:
        if len(df) == 0:
            print(f"{table_name} is empty, not writing to SQL")
        elif df.schema == "Validated":
            df.to_sql(
                con=con,
                name=f"aws_{table_name}_source",
                index=False,
                if_exists=table_type,
            )
            print(
                f"Writing {len(df)} {table_name} rows to aws_{table_name}_source to SQL"
            )
        else:
            print(f"{table_name} Schema Invalidated, not writing to SQL")
    except BaseException as error:
        print(f"SQL Write Script Failed, {error}")
        return error


aws_conn = sql_connection("s3_ingestion_prac")

bucket_name = "jacobsbucket97"


def get_s3_files(bucket: str):
    try:
        s3_resource = boto3.resource("s3")
        bucket = s3_resource.Bucket(name=bucket)
        s3_keys = list(s3_object.key for s3_object in bucket.objects.all())
        print(f"Returning {len(s3_keys)} s3 files")
        return s3_keys
    except BaseException as e:
        print(f"Error Occurred, {e}")
        raise e


s3_keys = get_s3_files(bucket_name)


def execute_reingestion(conn, s3_files):
    try:
        for i in s3_files:
            if "validated" in i:
                if (
                    len(i.split("/")) == 4
                ):  # the string should match this schema and have 4 unique parts, if not then dont ingest
                    data_type = i.split("/")[0]
                    file_name = i.split("/")[3]
                    df = wr.s3.read_parquet(path=f"s3://{bucket_name}/{i}")
                    df["file_name"] = file_name
                    df["upload_time"] = datetime.now()
                    df.schema = "Validated"
                    write_to_sql(conn, data_type, df, "append")
    except BaseException as e:
        print(f"Error Occurred, {e}")
        raise e


# took 4 mins 30 seconds to re-upload ~ 1 month of data.
execute_reingestion(aws_conn, s3_keys)
aws_conn.dispose()
