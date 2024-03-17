from datetime import datetime
import os

import redis

# https://github.com/redis/redis-py/blob/master/docs/examples/connection_examples.ipynb
redis_uri = f"rediss://default:{os.environ.get('REDIS_PW')}@{os.environ.get('REDIS_HOST')}:17842"
redis_client = redis.from_url(url=redis_uri, decode_responses=True)


redis_client.set(name="key", value="hello world", ex=900)
redis_client.set("int1", 3)
redis_client.set("float4", 3.5)


# get ttl on an object
redis_client.ttl("key")

# delete a value
redis_client.delete("key")

# Convert to a bytes, string, int or float first
redis_client.set("bool1", True)
redis_client.set("timestamp1", datetime.now())

key = redis_client.get("key")

print("The value of key is:", key)

# returns a bytes object, ahve to decode it into utf-8 to get str or whatever
key = redis_client.get("float4")

# returns None on cache miss
key = redis_client.get("float4")

redis_client.ttl("key")

redis_client.ping()
# batch up writes to optimize round trip calls
pipe = redis_client.pipeline()
pipe.set("foo", 5)
pipe.set("bar", 18.5)
pipe.set("blee", "hello world!")
pipe.execute()


dict_data = {
    "employee_name": "Adam Adams",
    "employee_age": 30,
    "position": "Software Engineer",
}

redis_client.mset(dict_data)

redis_client.mget("employee_name", "employee_age", "position", "non_existing")

redis_client.rpush("a", "1", "2", "3")
redis_client.lrange("a", 0, 5)

redis_client.delete("a")
