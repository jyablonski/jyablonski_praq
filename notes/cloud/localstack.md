# Integration Testing with LocalStack

## Overview

LocalStack is a Docker container that emulates AWS services locally, allowing you to run integration tests against realistic AWS APIs without hitting real infrastructure or incurring costs.

> Note: LocalStack also has a Snowflake emulator offering now, but this doc focuses on AWS.

## Core Concept

The basic pattern is:

1. Run LocalStack as a container exposing port 4566
1. Redirect your AWS SDK calls to hit `localhost:4566` instead of real AWS
1. Seed test data, run your code, assert on outcomes

## Setup

### Running LocalStack

```bash
# standalone
docker run -d -p 4566:4566 localstack/localstack

# or via docker-compose
```

```yaml
# docker-compose.yml
services:
  localstack:
    image: localstack/localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,sqs,secretsmanager
```

Port 4566 is the unified edge endpoint that routes to all emulated services internally.

### Pointing Your Code at LocalStack

Option 1: Environment variable (cleanest)

As of late 2023, boto3 respects `AWS_ENDPOINT_URL` as a global override:

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
```

Your existing `boto3.client("s3")` calls work without code changes.

Option 2: Thin factory wrapper

For older SDK versions or finer control:

```python
import os
import boto3

def get_client(service_name, kwargs):
    endpoint = os.getenv('AWS_ENDPOINT_URL')
    if endpoint:
        kwargs['endpoint_url'] = endpoint
    return boto3.client(service_name, kwargs)
```

Option 3: Explicit client configuration

```python
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)
```

LocalStack doesn't validate credentials by default, so any values work.

## Service Parity

Not all services are equally well-supported.

High parity (reliable):

- S3 - basic operations, some edge cases around lifecycle/versioning
- SQS - solid
- DynamoDB - good
- SNS - basic pub/sub
- Secrets Manager, SSM Parameter Store

Medium parity (happy path works):

- Lambda - runs code but execution environment differs
- IAM - policies exist but enforcement often incomplete
- Step Functions - basic flows

Lower parity (use cautiously):

- Glue - catalog okay, jobs/crawlers less so
- Athena - limited
- Kinesis - basic produce/consume, scaling behavior differs
- Newer/complex services (EKS, Redshift, Lake Formation) - spotty

Important caveat: LocalStack often accepts API calls without erroring even when behavior doesn't match production. Tests may pass locally but fail in prod due to consistency, error handling, rate limiting, or IAM differences.

## Example: Testing an S3 ETL Function

### Production Code

```python
# etl.py
import boto3
import json

def process_file(bucket: str, input_key: str, output_key: str) -> int:
    s3 = boto3.client('s3')
    
    response = s3.get_object(Bucket=bucket, Key=input_key)
    records = json.loads(response['Body'].read())
    
    active_records = [r for r in records if r.get('status') == 'active']
    
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(active_records)
    )
    
    return len(active_records)
```

Note: no test-specific code, just standard boto3 usage.

### Test Code

```python
# test_etl.py
import boto3
import pytest
import json
from etl import process_file

@pytest.fixture(scope='session')
def s3_client():
    """Client pointed at LocalStack."""
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )

@pytest.fixture
def test_bucket(s3_client):
    """Create a bucket for tests, clean up after."""
    bucket_name = 'test-bucket'
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name
    
    # cleanup
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
    s3_client.delete_bucket(Bucket=bucket_name)

def test_process_file_filters_active_records(s3_client, test_bucket, monkeypatch):
    # redirect production code to localstack
    monkeypatch.setenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
    
    # arrange
    input_data = [
        {'id': 1, 'status': 'active'},
        {'id': 2, 'status': 'inactive'},
        {'id': 3, 'status': 'active'},
    ]
    s3_client.put_object(
        Bucket=test_bucket,
        Key='input.json',
        Body=json.dumps(input_data)
    )
    
    # act
    count = process_file(test_bucket, 'input.json', 'output.json')
    
    # assert
    assert count == 2
    
    response = s3_client.get_object(Bucket=test_bucket, Key='output.json')
    output_data = json.loads(response['Body'].read())
    
    assert len(output_data) == 2
    assert all(r['status'] == 'active' for r in output_data)

def test_process_file_handles_empty_input(s3_client, test_bucket, monkeypatch):
    monkeypatch.setenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
    
    s3_client.put_object(
        Bucket=test_bucket,
        Key='empty.json',
        Body=json.dumps([])
    )
    
    count = process_file(test_bucket, 'empty.json', 'output.json')
    
    assert count == 0
```

### Running Tests

```bash
# start localstack
docker run -d -p 4566:4566 localstack/localstack

# run tests
pytest test_etl.py -v
```

## Key Patterns

1. Use fixtures for setup/teardown

Create resources (buckets, queues, tables) in fixtures and clean them up after tests. Scope appropriately - `session` for expensive setup, `function` for test isolation.

2. Keep production code clean

Use environment variables or dependency injection to make endpoint configurable. Don't litter source code with `if testing:` blocks.

3. Seed realistic data

Put your test data in the state you need before calling production code. Assert on the final state of AWS resources, not just return values.

4. Test failure modes too

Seed bad data, missing keys, malformed files. Verify your code handles S3 errors appropriately.

## Limitations to Keep in Mind

- LocalStack accepts calls that real AWS would reject (permissions, validation)
- Eventual consistency behavior differs
- Error messages and codes may not match exactly
- Performance characteristics are completely different
- Some service features are simply not implemented

For critical paths, supplement LocalStack tests with a staging environment hitting real AWS.
