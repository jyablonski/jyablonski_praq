import os

import polars as pl
import s3fs


def write_pl_df_to_s3(
    df: "pl.DataFrame",
    s3_bucket: str,
    s3_path: str,
    file_type: str = "parquet",
    aws_creds: dict[str, str] | None = None,
) -> None:
    file_type = file_type.lower()

    if file_type not in ("parquet", "csv"):
        raise ValueError("Please select 'parquet' or 'csv' for `file_type`")

    if not isinstance(df, pl.DataFrame):
        raise TypeError("Input `df` must be a Polars DataFrame (`pl.DataFrame`)")

    if aws_creds:
        fs = s3fs.S3FileSystem(
            key=aws_creds["access_key"],
            secret=aws_creds["secret_key"],
            token=aws_creds["access_token"],
        )
    else:
        fs = s3fs.S3FileSystem()

    destination = f"s3://{s3_bucket}/{s3_path}.{file_type}"

    with fs.open(destination, mode="wb") as f:
        print(f"Writing DataFrame to {destination}")

        if file_type == "parquet":
            df.write_parquet(file=f)
        elif file_type == "csv":
            df.write_csv(file=f)

    return None


if __name__ == "__main__":
    # https://docs.pola.rs/user-guide/io/cloud-storage/
    # read parquet
    df = pl.read_parquet(
        "s3://jyablonski-nba-elt-prod/reddit_comment_data/validated/year=2024/month=02/reddit_comment_data-2024-02-27.parquet"
    )

    write_pl_df_to_s3(
        df=df,
        s3_bucket="jyablonski97-devsss",
        s3_path="jacob-polars-test",
        file_type="parquet",
    )
