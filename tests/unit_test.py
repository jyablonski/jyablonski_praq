from datetime import datetime
import os
import pytest
import boto3
from botocore.exceptions import ClientError
import moto
import pandas as pd
import numpy as np
from faker import Faker

from dynamodb_prac.new_proj import *
from tests.utils import jacobs_http_function


def test_write_to_dynamodb(moto_dynamodb, faker):
    table_name = "jacobs_pytest_table"
    write_to_dynamodb(faker, table_name)
    table = wr.dynamodb.get_table(table_name=table_name)
    assert table.item_count == 1
