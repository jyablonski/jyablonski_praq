# Cassandra

Apache Cassandra is a distributed NoSQL database built in 2010, written in Java, and designed for high availability, fault tolerance, and horizontal scalability. It's columnar oriented which is different from row-oriented databases. It's often used for:

- Massive write and read throughput
- Multi-region availability
- No single point of failure
- Great for time series, logs, IoT data, or analytics at massive scale
- Not great for complex transactions or ad-hoc relational queries

It's core characteristics include:

- Distributed / Peer-to-peer where all nodes are equal, and there's no concept of a mster or slave nodes.
- Data is divided into partitions using a hash of the primary key of each record
- Data is replicated across multiple nodes for high availability
- Eventually consistent
- Data is stored in tables, but each row can have different columns

Database concepts:

- Keyspace is a top level namespace, like a database in a RDBMS. Also defines replication strategy and factor
- Tables go in a keyspace
- Partition key determines which node a row lives on
- Clustering key defines row ordering within a partition
- Replication factor is how many copies of the data we have across nodes. RF=3 means 3 copies of data
- `ONE`, `QUORUM`, `ALL` define how many nodes must acknowledge a read/write which Balances availability vs consistency.
  - `ONE` means one replica needs to acknowledge which means fast performance, but lower consistency
  - `QUORUM` means majority of replicas must respond, a more balanced solution
  - `ALL` means all replicas must respond. Strong consistency, but less available in node is down and slower performance
  - This is defined at query time by the consumer. It's not set a database / keyspace / table level at all
  - Thus, a lot of drivers or connections allow you to define a default consistency per session or connection. It defaults to `ONE`

Usecases:

1. Logging / Messaging
1. User Profile / Personalization Stores
1. Shopping carts / e-Commerce Inventory
1. Recommendation EDngines

Downsides / Tradeoffs:

1. No ACID Transactions
1. Harder to model relational data, you need query-based data modeling where you design tables based on the read queries you expect to make
1. Joins and aggreagations are limited, you typically need denormalization

How writes work:

1. Compute the hash of the partition key to determine which node(s) to store the data on
1. Write goes to multiple nodes depending on the replication factor
1. Optionally acknowledge based on chosen consistency level

How reads work:

1. Compute partition key to determine which node(s) to query
1. Nodes return data, coordinator merges the results
1. Optionally repair inconsistencies found during reads

## Production Scaling

- Small cluster: 3 nodes, RF=3, 8 cores, 32 GB RAM, SSDs. Handles modest traffic.
- Medium cluster: 5–8 nodes, RF=3, 16 cores, 64 GB RAM, SSDs. Handles tens of millions of writes/reads per day.
- Large cluster: 12+ nodes, multi-region replication, tuned compaction and caching. Handles hundreds of millions to billions of writes/reads per day.

## Consistency

As a consumer, here's a guide for choosing different consistency levels when making queries

| Consistency Level (CL) | When to Use | Pros | Cons / Trade-offs | Example Use Cases |
| ---------------------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------- |
| ONE | Fast operations where availability is more important than consistency | Very low latency; works even if some replicas are down | Reads may be stale; not suitable for critical transactional data | Logging events, click counters, telemetry, temporary caches |
| QUORUM | Balanced approach where correctness matters but some availability is acceptable | Ensures majority of replicas agree; tolerates some node failures; reasonably consistent | Slower than ONE; may have higher latency in multi-region clusters | User profiles, orders, ticket reservations, general CRUD operations |
| ALL | When absolute correctness is required and stale data is unacceptable | Guarantees full consistency across all replicas | High latency; fails if any replica is down; low availability | Financial transactions, inventory systems, critical data updates |
| Other notes | Read and write CLs can differ to tune consistency vs availability | Following the R + W > RF rule can achieve strong consistency without ALL | Needs careful design and understanding of replication factor | Writes at ONE, reads at QUORUM for near-consistent reads with fast writes |

## ScyllaDB

Because Java is dogshit a drop-in replacement for Cassandra called ScyllaDB was purpose built in C++ for performance. It has much higher throughput and lower latency on the exact same hardware because of true multithreaded capabilities, asynchronous design, and CPU core sharding.

- It's designed to use 100% of CPU cores, memory, and network efficiently.
- Supports CQL and can often be used with existing Cassandra drivers
