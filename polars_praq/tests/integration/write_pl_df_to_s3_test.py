from collections.abc import Awaitable, Callable, Iterator
from dataclasses import dataclass
from typing import TypeVar

import aiobotocore
import aiobotocore.endpoint
import botocore
import boto3
import pytest
from moto import mock_aws

from polars_praq.utils import write_pl_df_to_s3

# copied this mostly from https://github.com/aio-libs/aiobotocore/issues/755#issuecomment-1693741237
# there's an issue with using moto to mock s3fs, and everyone is just fkn spiderman pointing at eachother
# that it's someone else's problem to go fix yeet bby
T = TypeVar("T")
R = TypeVar("R")


@dataclass
class _PatchedAWSReponseContent:
    """Patched version of `botocore.awsrequest.AWSResponse.content`"""

    content: bytes | Awaitable[bytes]

    def __await__(self) -> Iterator[bytes]:
        async def _generate_async() -> bytes:
            if isinstance(self.content, Awaitable):
                return await self.content
            else:
                return self.content

        return _generate_async().__await__()

    def decode(self, encoding: str) -> str:
        assert isinstance(self.content, bytes)
        return self.content.decode(encoding)


class PatchedAWSResponse:
    """Patched version of `botocore.awsrequest.AWSResponse`"""

    def __init__(self, response: botocore.awsrequest.AWSResponse) -> None:
        self._response = response
        self.status_code = response.status_code
        self.content = _PatchedAWSReponseContent(response.content)
        self.raw = response.raw
        if not hasattr(self.raw, "raw_headers"):
            self.raw.raw_headers = {}


def _factory(
    original: Callable[[botocore.awsrequest.AWSResponse, T], Awaitable[R]]
) -> Callable[[botocore.awsrequest.AWSResponse, T], Awaitable[R]]:
    async def patched_convert_to_response_dict(
        http_response: botocore.awsrequest.AWSResponse, operation_model: T
    ) -> R:
        return await original(PatchedAWSResponse(http_response), operation_model)  # type: ignore[arg-type]

    return patched_convert_to_response_dict


aiobotocore.endpoint.convert_to_response_dict = _factory(aiobotocore.endpoint.convert_to_response_dict)  # type: ignore[assignment]
# Use patch_async_botocore_moto in your test


# https://github.com/aio-libs/aiobotocore/issues/755
@mock_aws
@pytest.mark.parametrize("file_type", ["parquet"])
def test_write_pl_df_to_s3_parameterized(file_type, pl_df_color_fixture):
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
