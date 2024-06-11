import json
import boto3
import pytest
from moto import mock_aws
from sqs.sqs_generator import (
    send_sqs_message,
)


@mock_aws
def test_send_message_success():
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = sqs.create_queue(QueueName="my-queue")["QueueUrl"]

    send_sqs_message(sqs, queue_url, "test message")

    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert len(messages["Messages"]) == 1
    assert messages["Messages"][0]["Body"] == "test message"


@mock_aws
def test_send_message_with_non_string_message():
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = sqs.create_queue(QueueName="my-queue")["QueueUrl"]

    message = {"key": "value"}

    send_sqs_message(sqs, queue_url, message)

    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert len(messages["Messages"]) == 1
    assert messages["Messages"][0]["Body"] == json.dumps(message)


@mock_aws
def test_send_message_queue_does_not_exist():
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/nonexistent-queue"

    with pytest.raises(Exception):
        send_sqs_message(sqs, queue_url, "test message")


@mock_aws
def test_send_message_other_exception():
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = sqs.create_queue(QueueName="my-queue")["QueueUrl"]

    with pytest.raises(Exception):
        with patch.object(
            sqs, "send_message", side_effect=Exception("Some other error")
        ):
            send_sqs_message(sqs, queue_url, "test message")
