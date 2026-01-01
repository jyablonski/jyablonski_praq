# Napkin Math

Napkin math is a core skill in system design interviews. It shows that you can reason about scale, cost, performance, and feasibility quickly—before writing code or choosing tools.

| Unit | Power of 10 | Bytes (approx) |
| ---- | ----------- | --------------------- |
| KB | 10³ | 1,000 |
| | 10⁴ | 10,000 |
| | 10⁵ | 100,000 |
| MB | 10⁶ | 1,000,000 |
| | 10⁷ | 10,000,000 |
| | 10⁸ | 100,000,000 |
| GB | 10⁹ | 1,000,000,000 |
| | 10¹⁰ | 10,000,000,000 |
| | 10¹¹ | 100,000,000,000 |
| TB | 10¹² | 1,000,000,000,000 |
| | 10¹³ | 10,000,000,000,000 |
| | 10¹⁴ | 100,000,000,000,000 |
| PB | 10¹⁵ | 1,000,000,000,000,000 |

| Description | Value | Approx |
| ------------------------ | -------------------------- | -------- |
| 1 Mbps | 10^6 bits/sec = 125 KB/sec | |
| 1 Gbps | 10^9 bits/sec = 125 MB/sec | |
| TCP packet size | ~1.5 KB | |
| Ethernet frame | 1500 bytes | ~1.5 KB |
| HTTP request size (JSON) | ~1–10 KB | |
| Image upload | ~100 KB – 5 MB | |
| Video chunk (HLS/DASH) | ~2–5 MB per 10 sec | |

Other constants

- 1 day = 86,400 sec ~ 10^5

- 1 month = ~30 days

- 1 year = ~10^7 sec (approx.)

- 10^3 = 1,000

- 10^6 = 1,000,000 (1 million)

- 10^9 = 1,000,000,000 (1 billion)

- 10^12 = 1,000,000,000,000 (1 trillion)

- The Exponent is how many zeroes to add

- 1 KB ~ 10^3 bytes

- 10 KB ~ 10^4 bytes

- KB, MB, GB etc all go to 1,024 bytes, but this is approximately equal to 10^3 or 1000 so just use that instead for quick math

## Scenarios

### Scenario 1

1. 100 million users
1. 10 KB (10^4) per user profile

Total storage needed would be 10^4 * 10^8 = 10^12 bytes, or 1 TB storage for user profiles

### Scenario 2

App has 500M users, each user has 20 KB profile.

500M users = 5 * 10^8
Each user = 20 * 10^3 bytes

Total storage = 20 * 10^3 * 5 * 10^8 = 10^12 = 1 TB

### Scenario 3

Your service returns 100 KB of JSON per request, handles 10,000 QPS.

100 KB = 10^5 bytes
10,000 QPS = 10^4 requests/sec

Total data/sec = 10^5 * 10^4 = 10^9 bytes/sec = ~1 GB/sec

### Scenario 4

10M daily active users, each does 20 writes/day

10M = 10^7 users

- 1M = 10^6
- 10M = 10^7

20 writes / user = 2 * 10^1

total writes per day = 2 * 10^1 * 10^7 = 2 * 10^8 = 200M writes / day

total writes per second = 2 * 10^8 / 10^5 = 2 * 10^3 or 2000 writes / second

- there are 86,400 seconds in a day, whihc can be rounded up to 10^5 (100,000) for napkin math on these problems

## Postgres Facts

The number of reads + writes that OLTP Databases like Postgres can handle varies wildly depending on hardware, configuration, workfload, and schema design.

- For reads, it can typically handle 1000 - 10000 per second
- reads are heavily affected by indexing and query complexity,
- For writes, it can typically handle 500 - 3000 per second
- writes are affected by WAL, transaction size, # of indexes, and replication. all of these add latency to write commits

WAL (Write-Ahead Logging) and replication have a big impact on PostgreSQL write performance, especially when you have read replicas and logical replication for CDC (Change Data Capture).

- WAL is a sequential log of all changes (writes) made to the database.
- Every change (INSERT, UPDATE, DELETE) is first written to the WAL before being applied to the data files.
- This ensures durability and crash recovery: if a crash happens, PostgreSQL can replay the WAL to restore data consistency.

WAL affects Write Performance

- Writing to WAL is typically very fast on SSDs
- However, committing a transaction usually waits for WAL to be flushed (fsync) to disk to guarantee durability (unless you configure async commit).
- This fsync is the major bottleneck for write latency.

This is compounded when you enable logical replication

- Logical replication reads WAL records and streams the changes (in logical format) to subscribers.
- This adds CPU and IO overhead on the primary: WAL has to be kept longer (cannot be recycled) until all subscribers receive the changes, and the system must decode WAL entries into logical changes

Physical vs. logical replication are two different ways PostgreSQL replicates data from a primary (master) to replicas (standbys). They serve different use cases and have different trade-offs.

- Physical replication copies the exact bytes from WAL on the primary database and sends them to the replica database

- The replicas are read-only and are typically used for better scaling your read workloads, and failover and high-availability setups

- TLDR the replica can read raw binary bytes from the WAL and apply the database changes using them

- Logical replication involves reading WAL changes and decoding them into logical changes like `INSERT into table x`

- Used when subscribers cannot understand physical replication raw binary bytes

- Subscribers can have different schemas or even different PostgreSQL versions.

- Supports more flexibile replication

- More CPU intensive

```sql
-- 10kb per user
CREATE TABLE users_light (
  id UUID PRIMARY KEY,                                -- 16 bytes
  username VARCHAR(50),                               -- ~50 bytes
  email VARCHAR(100),                                 -- ~100 bytes
  bio TEXT,                                            -- ~2 KB average
  profile_image_url VARCHAR(255),                     -- ~255 bytes
  preferences JSONB,                                  -- ~3 KB average
  created_at TIMESTAMP,                               -- 8 bytes
  updated_at TIMESTAMP                                -- 8 bytes
);

-- ~20 kb per user
CREATE TABLE users_heavy (
  id UUID PRIMARY KEY,                                -- 16 bytes
  username VARCHAR(100),                              -- ~100 bytes
  email VARCHAR(255),                                 -- ~255 bytes
  bio TEXT,                                            -- ~4 KB average
  profile_image_base64 TEXT,                          -- ~5 KB average
  preferences JSONB,                                  -- ~4 KB average
  social_links JSONB,                                 -- ~2 KB average
  settings JSONB,                                     -- ~2 KB average
  audit_log TEXT,                                     -- ~1 KB average
  created_at TIMESTAMP,                               -- 8 bytes
  updated_at TIMESTAMP                                -- 8 bytes
);

```

## Web Server Performance

Python better for fast prototyping or if the team only has familiarity with Python.

- Python also has more libraries

Go is better for high throughput (10,000+ requests per second (RPS)) and systems that require high performance

1. Basic Web Server - 10-100k RPS for static content. 1k-10k for dynamic content, 100-1k for database-heavy content
1. Go (Gin/Echo framework): 15,000 - 30,000 req/sec. 5-15 ms latency. Go uses 2-3x less memory than Python
1. FastAPI (with Uvicorn): 8,000 - 15,000 req/sec. 20-50 ms latency
1. FastAPI (async): 10,000 - 18,000 req/sec. 10-25 ms latency

gRPC Go servers have nearly 50-80% higher throughput than REST.

- 2-3x lower latecy
- gRPC protobuf messages are 30-50% smaller than JSON
- Significant network savings for large payloads
- Much better performance because it's a binary protocol which gets to send significantly fewer bytes per request than JSON
- Also utilizes HTTP/2 Multiplexing to support multiple streams per connection and have better resource utilization
- Benefits are not as significant for CRUD applications w/ heavy database usage
- Limited flexibility to support Frontends as browsers don't support gRPC, requires additional setup and more complex solutions like a gRPC Gateway middleman

## Storage Performance

1. Redis - between 100k and 1 million WPS. 0.1 - 1ms latency
1. SSD Storage - 10-100k random WPS. 0.1 - 1ms latency
1. HDD Storage - 100-1000 random WPS. 5 - 15ms latency
