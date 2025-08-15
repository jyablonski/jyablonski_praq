# Redis

Redis is an in-memory data store designed for high performance applications. Because all data lives in RAM and not on disk, 100% of reads and writes are extremely fast.

It manages memory management through a concept called TTL (time-to-live). It's a per-key expiration time in Redis which defines how long each key should live before being automatically deleted.

- It's measured in seconds
- The purpose is to ensure memory doesn't grow indefinitely 
- Various strategies such as:
    - Fixed TTL (expire after x seconds)
    - Sliding TTL (refresh the TTL every time a key is accessed)
    - Randomized TTL to avoid thundering herd problem where many keys expire simultaneously

It supports:

- Optional persistence by saving snapshots to disk so data isn't lost if Redis restarts
- Various data structures like lists, sets, sorted sets, geospatial indexes etc.
- Can be vertically scaled for single-node setups
- Can be setup as a Redis Cluster for horizontal scaling, multiple nodes, high availability
    - Some tradeoffs here though - some ommands like MGET, MSET, SUNION, ZUNIONSTORE, etc. only work if all keys are in the same hash slot.
    - Adding or removing nodes requires resharding hash slots which can temporarily affect performance
    - Your client library must be cluster-aware and handle `MOVED` or `ASK` redirections appropriately

Example usecases:

1. Cache Layer
2. Rate Limiting
3. Leaderboard
4. PubSub Messaging
5. Job Queues
6. User Session Store

## Standard Redis Size

A standard Redis node depends on the workload, but for general purposes:

| Component | Typical Specs                                                                                             |
| --------- | --------------------------------------------------------------------------------------------------------- |
| CPU       | 4–8 vCPUs (Redis is single-threaded for command execution, but networking and I/O use event-driven async) |
| RAM       | Enough to hold all your dataset in memory, plus overhead (e.g., 16–64 GB common)                          |
| Disk      | Only needed for persistence (RDB snapshots or AOF logs), usually SSD                                      |
| Network   | High throughput and low latency, preferably 10 Gbps for large deployments                                 |

- Redis is extremely fast because it’s in-memory.
- On a modern 4–8 vCPU node:
    - Single-threaded commands: 100k–200k simple read/write ops/sec (like `GET`/`SET`) per core.
    - Multi-core doesn’t increase throughput per key, but can handle multiple connections in parallel.
- With pipelining (sending multiple commands at once), throughput can exceed 1M ops/sec for simple commands.

## Example Commands

``` sh
# Start Redis CLI
redis-cli

# Set a value
SET user:100 "Jacob"

# Get a value
GET user:100
# -> "Jacob"

# Increment a counter
INCR pageviews

# Use a list
LPUSH tasks "task1"
LPUSH tasks "task2"
LRANGE tasks 0 -1
# -> ["task2", "task1"]
```

## Diagram

``` mermaid
flowchart LR
    %% Users / clients
    Users[Users / Clients] --> LB[Load Balancer]

    %% Microservice instances
    LB --> MS1[Microservice Instance 1]
    LB --> MS2[Microservice Instance 2]
    LB --> MS3[Microservice Instance 3]

    %% Redis node
    MS1 --> Redis[Redis Node]
    MS2 --> Redis
    MS3 --> Redis

```

- Redis lets multiple instances of a microservice share temporary data.
- Example: Ticketmaster has many servers handling ticket requests. Redis stores temporary ticket holds so all servers see the same information.
- Without Redis, each server would only know its own memory, so they couldn’t coordinate ticket availability.
