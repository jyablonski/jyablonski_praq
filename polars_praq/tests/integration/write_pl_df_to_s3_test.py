import os

import boto3
import pytest

from polars_praq.utils import write_pl_df_to_s3

# from tests.mock_aio import mock_aio_aws

# copied this mostly from https://github.com/aio-libs/aiobotocore/issues/755#issuecomment-1693741237


@pytest.mark.parametrize("file_type", ["parquet", "csv"])
def test_write_pl_df_to_s3(file_type, pl_df_color_fixture, mock_aws):
    s3_bucket = "test-bucket"
    s3_path = "test-path"

    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=s3_bucket)

    write_pl_df_to_s3(
        df=pl_df_color_fixture,
        s3_bucket=s3_bucket,
        s3_path=s3_path,
        file_type=file_type,
    )

    s3_objects = list(conn.Bucket(s3_bucket).objects.all())
    assert len(s3_objects) == 1
    assert s3_objects[0].key == f"{s3_path}.{file_type}"


def test_write_pl_df_to_s3_bad_file_type(pl_df_color_fixture, mock_aws):
    s3_bucket = "test-bucket"
    s3_path = "test-path"
    file_type = "json"

    with pytest.raises(ValueError) as exc_error:
        write_pl_df_to_s3(
            df=pl_df_color_fixture,
            s3_bucket=s3_bucket,
            s3_path=s3_path,
            file_type=file_type,
        )

    assert str(exc_error.value) == "Please select 'csv' or 'parquet' for `file_type`"


def test_write_pl_df_to_s3_aws_creds(pl_df_color_fixture, mock_aws):
    s3_bucket = "test-json-bucket"
    s3_path = "test-path"
    file_type = "parquet"
    aws_creds = {
        "access_key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "access_token": os.environ.get("AWS_SESSION_TOKEN"),
    }

    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=s3_bucket)

    results = write_pl_df_to_s3(
        df=pl_df_color_fixture,
        s3_bucket=s3_bucket,
        s3_path=s3_path,
        file_type=file_type,
        aws_creds=aws_creds,
    )

    s3_objects = list(conn.Bucket(s3_bucket).objects.all())
    assert len(s3_objects) == 1
    assert s3_objects[0].key == f"{s3_path}.{file_type}"
    assert results == None


def test_write_pl_df_to_s3_aws_creds_missing_key(pl_df_color_fixture, mock_aws):
    s3_bucket = "test-json-bucket"
    s3_path = "test-path"
    file_type = "parquet"
    aws_creds = {
        "access_key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
    }

    with pytest.raises(KeyError) as exc_error:
        write_pl_df_to_s3(
            df=pl_df_color_fixture,
            s3_bucket=s3_bucket,
            s3_path=s3_path,
            file_type=file_type,
            aws_creds=aws_creds,
        )

    assert (
        str(exc_error.value)
        == "'Missing one of `access_key`, `access_token`, or `secret_key` in aws_creds'"
    )
