from datetime import datetime, timedelta

import boto3
import botocore

import pandas as pd

today = datetime.now()
client = boto3.client("cloudwatch")

# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-metrics.html#rds-cw-metrics-instance
# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Statistics-definitions.html


def get_rds_metrics(client, rds_server: str, period: int, start_time: datetime):
    print(f"start_time is {start_time}, end_time is {(start_time - timedelta(days=1))}")
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "cpu_utilization",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "CPUUtilization",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "freeable_memory",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "FreeableMemory",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "db_connections",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "DatabaseConnections",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "write_iops",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "WriteIOPS",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "read_iops",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "ReadIOPS",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "deadlocks",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "Deadlocks",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "network_throughput",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "NetworkThroughput",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "read_latency",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "ReadLatency",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
            {
                "Id": "write_latency",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "WriteLatency",
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": rds_server}
                        ],
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            },
        ],
        StartTime=(start_time - timedelta(days=1)).timestamp(),
        EndTime=start_time.timestamp(),
    )
    df = pd.DataFrame(response["MetricDataResults"])
    df = df.explode(["Timestamps", "Values"]).reset_index()
    df["database"] = rds_server
    df = df.drop(["index", "Id", "StatusCode"], axis=1)

    print(f"Acquired {len(df)} Records, returning DataFrame")
    return df


metrics = get_rds_metrics(client, "jacobs-rds-server", 60, today)
