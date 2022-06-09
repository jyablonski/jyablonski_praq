from datetime import datetime
import hashlib
import json
import time

import awswrangler as wr
from faker import Faker
import pandas as pd

# quick script to store fake data to dynamodb every 5 seconds

fake = Faker()
starttime = time.time()
while True:
    name = fake.name()
    scrape_ts = datetime.now()
    name_hash_pk = hashlib.md5((name + str(scrape_ts)).encode("utf-8")).hexdigest()

    # hash concat with current timestamp for pk bc there might be 2 ppl who have the same exact name
    dynamo_payload = {
        "name_hash_pk": name_hash_pk,
        "name": name,
        "scrape_ts": scrape_ts,
    }

    # first dump then loads - have to convert datetime obj to string then load everything back to dict
    # in order to store to dynamo db
    wr.dynamodb.put_items(
        items=[json.loads(json.dumps(dynamo_payload, default=str))],
        table_name="jacob_test_table",
    )
    print(f"Storing {name} to dynamodb at {scrape_ts}")
    time.sleep(5 - ((time.time() - starttime) % 5))
