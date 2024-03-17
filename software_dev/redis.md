# Redis
Redis, which stands for **RE**mote **DI**ctionary **S**erver, is an open-source, in-memory data structure store. It is often referred to as a data structure server because it supports various data types such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, and geospatial indexes with radius queries.

Here are some key features and aspects of Redis:

1. **In-Memory Database**: Redis primarily stores data in memory, making it extremely fast for read and write operations. However, it also supports persistence options, allowing data to be saved to disk for durability.

2. **Key-Value Store**: Redis stores data using a key-value pair model, where each piece of data (value) is associated with a unique identifier (key). This makes data retrieval fast and efficient.

3. **Support for Data Structures**: Redis is not limited to storing simple strings; it supports a wide range of data structures, such as strings, lists, sets, sorted sets, hashes, bitmaps, hyperloglogs, and geospatial indexes. This versatility allows developers to choose the most appropriate data structure for their use case.

4. **High Performance**: Due to its in-memory nature and efficient data structures, Redis is known for its high performance and low latency. It can handle a large number of operations per second, making it suitable for use cases requiring real-time data processing.

5. **Pub/Sub Messaging**: Redis includes support for publish/subscribe messaging, allowing clients to subscribe to channels and receive messages published to those channels in real-time. This feature is useful for building real-time applications, chat systems, and message brokers.

6. **Lua Scripting**: Redis allows users to execute Lua scripts directly on the server, enabling complex operations to be performed atomically and efficiently.

7. **Clustering and High Availability**: Redis supports clustering and high availability configurations, allowing it to scale horizontally across multiple nodes while providing fault tolerance and data redundancy.

8. **Multi-Language Support**: Redis provides client libraries for various programming languages, making it easy to integrate with applications written in languages such as Python, Java, Node.js, Ruby, and more.

Overall, Redis is widely used as a caching mechanism, message broker, real-time analytics engine, and as a backend for applications requiring fast data access and processing. Its simplicity, performance, and versatility make it a popular choice for a wide range of use cases in modern software development.

## Expiration + Eviction Policies
In Redis, expiration and eviction policies are mechanisms used to manage the lifecycle of data stored in memory. These mechanisms ensure that Redis remains efficient and responsive, especially when dealing with large datasets that exceed available memory. Let's delve into each of these aspects:

### Expiration (TTL)

Expiration in Redis refers to setting a time limit on how long a key-value pair should be retained in memory. Once the expiration time is reached, Redis automatically removes the key-value pair from the dataset. This feature is particularly useful for implementing cache expirations, session timeouts, and temporary data storage.  

By default, a key that's set with no TTL will remain in memory indefinitely until it's explicitly removed by a client via the `DEL` command, or replaced by another key.

You can set expiration for keys using the `EXPIRE`, `EXPIREAT`, or `PEXPIRE` commands. Here's a brief overview:

- **EXPIRE key seconds**: Set a key's time-to-live in seconds.
- **EXPIREAT key timestamp**: Set a key's expiry time as a UNIX timestamp.
- **PEXPIRE key milliseconds**: Set a key's time-to-live in milliseconds.

For example:
```redis
> SET mykey "Hello"
OK
> EXPIRE mykey 10  # Set expiration time to 10 seconds
(integer) 1
```

### Eviction Policies

Eviction policies come into play when Redis runs out of memory and needs to make space for new data. When the maximum memory limit is reached, Redis employs eviction policies to determine which keys to remove from the dataset to free up memory.

Redis supports several eviction policies:

1. **No Eviction (default)**: Redis returns an error when memory limit is exceeded, preventing any further write operations until memory is freed.

2. **AllKeysLRU**: Redis evicts the least recently used (LRU) keys across all namespaces (i.e., databases) to make space for new data.

3. **Voluntary TTL**: Redis evicts keys with an associated time-to-live (TTL) set by the user using expiration commands (`EXPIRE`, `EXPIREAT`, `PEXPIRE`). Keys with shorter TTLs are evicted first.

4. **Volatile LRU**: Similar to AllKeysLRU, but only keys with an associated TTL are considered for eviction.

5. **Volatile TTL**: Redis evicts keys with an associated TTL, preferring keys with shorter TTLs.

6. **Random**: Redis selects keys randomly for eviction.

The eviction policy can be set in the Redis configuration file (`redis.conf`) or modified dynamically using the `CONFIG SET` command.

For example:
```redis
> CONFIG SET maxmemory-policy allkeys-lru
OK
```

It's essential to choose the right eviction policy based on your application's requirements. For instance, if you're using Redis primarily as a cache, the LRU-based policies may be suitable. However, if you're storing transient data with specific TTLs, the Volatile policies might be more appropriate.

Understanding expiration and eviction policies helps optimize Redis performance and ensures efficient memory management in your applications.

## Aiven + Grafana Cloud
Used Aiven to create a Redis Instance + connected to it locally in the `redis/main.py` file as well as Grafana Cloud for a high level overview of the instance.

![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/da8211c0-ecca-49d6-85ff-c3097cb58bd8)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/30f9cbd7-4799-456e-8f47-8202fe0cba36)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/bc7063a3-4bec-4ded-a317-734bc2aa8801)