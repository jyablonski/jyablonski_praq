import os
import pytest
import pytest_mock
import sqlite3
import pandas as pd
import numpy as np
import boto3
import moto
from datetime import datetime, timedelta
from faker import Faker

from dynamodb_prac.new_proj import *


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


# this creates an s3 client where u can create a bucket and then test with.
@pytest.fixture(scope="function")
def s3(aws_credentials):
    with moto.mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


class MyModel(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def save(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket="mybucket", Key=self.name, Body=self.value)


@pytest.fixture
def setup_database():
    """Fixture to set up an empty in-memory database"""
    conn = sqlite3.connect(":memory:")
    yield conn


# Moto only works when two conditions are met:
# The logic to be tested is executed inside a Moto-context
# The Moto-context is started before any boto3-clients (or resources) are created
@pytest.fixture(scope="function")
def moto_dynamodb():
    with moto.mock_dynamodb():
        dynamodb = boto3.resource("dynamodb")
        dynamodb.create_table(
            TableName="jacobs_pytest_table",
            KeySchema=[{"AttributeName": "name_hash_pk", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "name_hash_pk", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield dynamodb


# @pytest.fixture
# def faker_object():
#     fake = Faker()
#     return fake
