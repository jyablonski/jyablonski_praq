from datetime import datetime, timezone
import json
import logging
import os

import awswrangler as wr
from faker import Faker
from faker.providers import internet
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    handlers=[logging.StreamHandler()],
)

logging.info("Starting Fake Data Lambda Generator ...")

fake = Faker()
fake.add_provider(internet)

# Create a mapping of data types to corresponding faker methods and parameters
FAKER_METHODS = {
    "name": fake.name,
    "address": fake.address,
    "username": fake.user_name,
    "email": fake.email,
    "hire_date": lambda: fake.date_between(start_date="-3y", end_date="today"),
    "status": lambda: np.random.choice(
        ["Full Time", "Part Time", "Per Diem"], p=[0.50, 0.30, 0.20]
    ),
    "color": lambda: fake.color_name(),
    "salary": lambda: int(round(np.random.uniform(50000, 250000) / 500, 0) * 500),
    "store_id": lambda: np.random.randint(1, 1000),
    "ipv4_private": fake.ipv4_private,
    "text": fake.text,
    "date_of_birth": fake.date_of_birth,
    "ssn": fake.ssn,
    "phone_number": fake.phone_number,
    "credit_card_number": fake.credit_card_number,
    "company": fake.company,
    "company_email": fake.company_email,
}


def make_fake_data(num: int = 5000, schema: dict = None) -> pd.DataFrame:
    """Generate a fake dataset based on the provided schema.

    Args:
        num (int): The number of rows to generate.
        schema (dict): A dictionary defining the columns and their types.

    Returns:
        pd.DataFrame: A DataFrame containing the generated fake data.
    """
    if schema is None:
        # Default schema if none is provided
        schema = {
            "name": "name",
            "address": "address",
            "username": "username",
            "email": "email",
            "hire_date": "hire_date",
            "status": "status",
            "color": "color",
            "salary": "salary",
            "store_id": "store_id",
        }

    # Generate fake data based on the provided schema
    df = [
        {col: FAKER_METHODS[data_type]() for col, data_type in schema.items()}
        for _ in range(num)
    ]

    df = pd.DataFrame(df)
    df.insert(0, "id", range(1, len(df) + 1))  # Insert ID column at the start
    df["created_at"] = datetime.now(
        timezone.utc
    )  # Add a created_at column with current timestamp

    return df


def lambda_handler(event, context):
    """AWS Lambda handler function."""
    logging.info("Beginning Execution")
    num_rows = int(event.get("num_rows", 100))
    custom_schema = {
        "name": "name",
        "email": "email",
        "hire_date": "hire_date",
        "salary": "salary",
        "status": "status",
        "company": "company",
        "credit_card_number": "credit_card_number",
        "phone_number": "phone_number",
    }

    fake_data = make_fake_data(num=num_rows, schema=custom_schema)
    logging.info("Generated Data, continuing w/ S3 Write")

    s3_path = os.environ.get(
        "S3_PATH", "s3://jyablonski-nba-elt-prod/fake_data/test.parquet"
    )

    wr.s3.to_parquet(df=fake_data, path=s3_path, index=False)

    logging.info("Finished Execution")
    return {
        "statusCode": 200,
        "body": json.dumps(f"Fake data generated and written to {s3_path}"),
    }
