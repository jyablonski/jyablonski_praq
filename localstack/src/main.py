from datetime import datetime

import boto3
import json


def lambda_handler(event, context):
    if event is not None:
        print(f"event is {event}")

    print(f"Hello world! at {datetime.now()}")
    return event
