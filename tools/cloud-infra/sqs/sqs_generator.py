from datetime import datetime, timedelta
import json
import os
import random

import boto3
import botocore
from faker import Faker

# botocore.exceptions.QueueDoesNotExist
# dont do str(dict) to get a dict ready to send.  use json.dumps for double quotes.

client = boto3.client("sqs")
faker = Faker()


# should create a separate function to create an sqs queue and not include it in this function logic
def send_sqs_message(
    client: botocore.client,
    sqs_queue: str,
    message: str,
    create_new_queue: bool = False,
) -> None:
    try:
        if not isinstance(message, str):
            message = json.dumps(message)
            print(message)

        print(f"Sending message to queue {sqs_queue}")
        client.send_message(
            QueueUrl=sqs_queue,
            MessageBody=message,
            DelaySeconds=0,
            MessageAttributes={},
            MessageSystemAttributes={},
        )

        pass

    except client.exceptions.QueueDoesNotExist as error:
        if create_new_queue:
            print(f"Queue {sqs_queue} does not exist, creating it ...")
            client.create_queue(QueueName=sqs_queue)

            print(f"Sending message to queue {sqs_queue}")
            client.send_message(
                QueueUrl=sqs_queue,
                MessageBody=message,
                DelaySeconds=0,
                MessageAttributes={},
                MessageSystemAttributes={},
            )
            return None
        else:
            raise error
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


if __name__ == "__main__":
    queue = f"tesresadasds"
    message = generate_fake_data(faker)
    # message_str = str(message)

    # QueueDoesNotExist: An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the SendMessage operation: The specified queue does not exist for this wsdl version.
    send_sqs_message(client, queue, message, create_new_queue=True)
