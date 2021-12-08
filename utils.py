import os
import boto3
from sqlalchemy import exc, create_engine
import logging


def get_owner(parameter: str) -> str:
    print(f"The owner is {parameter}!")
    return parameter


def get_ssm_parameter(parameter_name: str) -> str:
    """
    Function to grab parameters from SSM

    note: withdecryption = false will make pg user not work bc its a securestring.
        ignored for String and StringList parameter types

    Args:
        parameter_name (string) - name of the parameter you want

    Returns:
        parameter_value (string)
    """
    try:
        ssm = boto3.client("ssm")
        resp = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return resp["Parameter"]["Value"]
    except BaseException as error:
        print(f"SSM Failed, {error}")
        df = []
        return df


def aws_connection(schema: str):
    try:
        connection = create_engine(
            f"postgresql+psycopg2://"
            + os.environ.get("RDS_USER")
            + ":"
            + os.environ.get("RDS_PW")
            + "@"
            + os.environ.get("IP")
            + ":"
            + "5432"
            + "/"
            + os.environ.get("RDS_DB"),
            connect_args={
                "options": "-csearch_path={nba_source}"
            },  # defining schema to connect to
            echo=False,
        )
        logging.info(f"SQL Connection to {schema} Successful")
        print(f"SQL Connection to {schema} Successful")
        return connection
    except exc.SQLAlchemyError as e:
        logging.info(f"SQL Connection to {schema} Failed, Error: {e}")
        print(f"SQL Connection to {schema} Failed, Error: {e}")
        return e
