import boto3

client = boto3.client("rds")

response = client.create_db_snapshot(
    DBSnapshotIdentifier="jacobs-rds-snapshot-2023-01-24",
    DBInstanceIdentifier="jacobs-rds-server",
)