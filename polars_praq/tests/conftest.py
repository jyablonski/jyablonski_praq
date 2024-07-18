from datetime import datetime
import os

import boto3
from moto import mock_aws
import polars as pl
import pytest

from .mock_aio import mock_aio_aws


@pytest.fixture(autouse=True)
def pl_df_color_fixture():
    test_df = pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "sale_price": [4.0, 5.0, 6.0, 7.0, 8.0],
            "color": ["red", "red", "green", "blue", "green"],
            "created_at": [
                datetime(2022, 1, 1),
                datetime(2022, 1, 2),
                datetime(2022, 1, 3),
                datetime(2022, 1, 4),
                datetime(2022, 1, 5),
            ],
        }
    )

    return test_df


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture()
def mock_aws(monkeypatch):
    with mock_aio_aws(monkeypatch):
        yield
