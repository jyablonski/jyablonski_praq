from datetime import datetime, timedelta
import json
import os
import random

import boto3
import botocore
from faker import Faker

# dont do str(dict) to get a dict ready to send.  use json.dumps for double quotes.

client = boto3.client("sqs")
faker = Faker()


# check this
def send_sqs_message(
    client: botocore.client,
    sqs_queue: str,
    message: str,
) -> None:
    try:
        if not isinstance(message, str):
            message = json.dumps(message)
            print(message)

        print(f"Sending message to queue {sqs_queue}")
        client.send_message(
            QueueUrl=sqs_queue,
            MessageBody=message,
            DelaySeconds=123,
            MessageAttributes={},
            MessageSystemAttributes={},
        )

        pass

    except BaseException as e:
        print(f"Error Occurred while writing to {sqs_queue}, {e}")
        raise e


def generate_fake_data(faker: Faker):
    payload = {
        "id": faker.unique.random_int(),
        "title": faker.email(),
        "release_year": faker.date_between(start_date="-105y", end_date="today").year,
        "country": faker.country(),
        "genres": random.choice(["Horror", "Comedy", "Action"]),
        "actors": faker.name(),
        "directors": faker.name(),
        "composers": faker.name(),
        "screenwriters": faker.name(),
        "cinematographer": faker.name(),
        "production_companies": faker.street_name(),
    }
    print(f"Generating payload {payload['id']}")
    return payload


queue = f"jacobs-graphql-agent-sqs"
message = generate_fake_data(faker)
# message_str = str(message)

send_sqs_message(client, queue, message)
