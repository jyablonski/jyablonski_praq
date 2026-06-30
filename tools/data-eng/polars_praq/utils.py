import os
import tempfile

import polars as pl
import s3fs


def write_pl_df_to_s3(
    df: pl.DataFrame,
    s3_bucket: str,
    s3_path: str,
    file_type: str = "parquet",
    aws_creds: dict[str, str] | None = None,
) -> None:
    file_type = file_type.lower()

    if file_type not in ("csv", "parquet"):
        raise ValueError("Please select 'csv' or 'parquet' for `file_type`")

    if aws_creds and not all(
        key in aws_creds for key in ["access_key", "secret_key", "access_token"]
    ):
        raise KeyError(
            "Missing one of `access_key`, `access_token`, or `secret_key` in aws_creds"
        )

    fs = (
        s3fs.S3FileSystem(
            key=aws_creds["access_key"],
            secret=aws_creds["secret_key"],
            token=aws_creds["access_token"],
        )
        if aws_creds
        else s3fs.S3FileSystem()
    )

    destination = f"s3://{s3_bucket}/{s3_path}.{file_type}"

    # creating a local temp file for polars to write the file to
    # before it sends it off to s3. without this, it returns a
    # warnign to you?
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        print(f"Temporary file path: {temp_file_path}")

        try:
            if file_type == "parquet":
                df.write_parquet(temp_file_path)
            elif file_type == "csv":
                df.write_csv(temp_file_path)

            # Now upload the file to S3
            with open(temp_file_path, "rb") as local_file:
                with fs.open(destination, mode="wb") as s3_file:
                    s3_file.write(local_file.read())

        finally:
            os.remove(temp_file_path)  # Clean up the temporary file

    return None


# if __name__ == "__main__":
#     # https://docs.pola.rs/user-guide/io/cloud-storage/
#     # read parquet
#     df = pl.read_parquet(
#         "s3://jyablonski-nba-elt-prod/reddit_comment_data/validated/year=2024/month=02/reddit_comment_data-2024-02-27.parquet"
#     )

#     write_pl_df_to_s3(
#         df=df,
#         s3_bucket="jyablonski97-devsss",
#         s3_path="jacob-polars-test",
#         file_type="parquet",
#     )
