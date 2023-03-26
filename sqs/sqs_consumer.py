from datetime import datetime, timedelta
import json
import os
from typing import List

import boto3
import botocore

client = boto3.client("sqs")


def get_messages_from_queue(
    client: botocore.client,
    queue_url: str,
) -> List[dict]:
    df = []
    messages = []

    while True:
        resp = client.receive_message(
            QueueUrl=queue_url, AttributeNames=["All"], MaxNumberOfMessages=10
        )

        # check to see if there's messages, if not then exit the loop
        try:
            messages.extend(resp["Messages"])
        except KeyError:
            print("There were no SQS Messages, breaking out")
            break

        # process the messages, add them to the df that we return
        for msg in messages:
            print(msg)
            try:
                msg_body = json.loads(msg["Body"])
            except json.JSONDecodeError:
                msg_body = json.loads(msg["Body"].replace("'", '"'))
                # msg2=json.loads(msg_body)
            # msg_timestamp = datetime.fromtimestamp(int(msg['Attributes']['SentTimestamp']) / 1000)

            df.append(msg_body)

        # delete the messages from the queue that we just grabbed.
        entries = [
            {"Id": msg["MessageId"], "ReceiptHandle": msg["ReceiptHandle"]}
            for msg in resp["Messages"]
        ]

        resp = client.delete_message_batch(QueueUrl=queue_url, Entries=entries)

        if len(resp["Successful"]) != len(entries):
            raise RuntimeError(
                f"Failed to delete messages: entries={entries!r} resp={resp!r}"
            )

    return df


queue_url = f"jacobs-first-sqs"
df = get_messages_from_queue(client, queue_url)
