# System Design
Hot Reads

## Tools
1. Relational Database
   1. The go-to choice for many use cases.  
   2. Versatile, stores structured data, allows various forms of OLTP and OLAP needs.
   3. Can store many different types of structured data in different tables.
   4. Allows you to configure complex data relationships.
   5. ACID Compliance
      1. Atomic - Transactions are all or nothing.  If it fails, nothing gets committed.
      2. Consistent - Database is always in a consistent state.  Data integrity is maintained, constraints don't fail etc.
      3. Isolated - Concurrent Transactions do not affect each other; they process 1 at a time.
      4. Durable - Transaction that are committed are permanent.  Enforced via WAL or the BinLog, which enables Admins to recover the database in the event of system failure etc.
   6. Examples: Postgres, MySQL
2. Key Value Store
   1. Effective at storing unstructured data quickly.
   2. Scales well, designed for horizontal scalability.  Designed for large number of read + write operations across distributed systems.
   3. Pairs well w/ things like Lambda Functions
   4. Easy to implement Caching
   5. Examples: DynamoDB, MongoDB
3. Caching Store
   1. Used to improve the performance, reduce latency, and increase responsiveness of existing Applications.
   2. General idea is data can be stored in this Caching Store in-memory and then be accessed by applications much more quickly than if the Application had to go to an actual Database or other memory store for it.
   3. Primarily works in-memory, which is why it's so fast.
      1. Because it's in-memory, there's a limit of how much data can be stored in a Caching Store.
   4. Has a Time-to-live (TTL) feature which describes how long to keep the data cached for.  There are also methods and ways to invalidate the cache and reset things.
   5. Commonly used in web applications, databases, and REST APIs.
   6. Examples: Redis, Memcached
4. Queuing Services
   1. Great for building de-coupled Applications
   2. Say you have events happening that you want to record, but don't necessarily want to process right away
   3. First-in-first-out (FIFO) is a principle that allows consumers of these queuing services to process the messages in-order of when they were created.
   4. Dead Letter Queues allow messages that fail to be consumed for whatever reason to be stored separately so that the message isn't lost.
   5. With Queueing Services, messages can only be consumed once.
   6. Examples: AWS SQS
5. Pub Sub
   1. Mechanism to build publisher / subscriber patterns in distributed systems.
   2. Message Producers (publishers) send messages to a central broker where they are stored in a log-based format, and message consumers (subscribers) read from those logs to consume the messages at their own pace.
   3. As opposed to Queuing Services, messages are *not* removed from the log when they are consumed.  Instead, they have a TTL and are deleted after that TTL expires (typically 7 days).
   4. Messages are stored in a log-based format in what are known as Topics.
   5. Allow for high scalability and performance, often used in a distributed system format with multiple brokers for performance & failover redundancy.
   6. Common use cases include real time data processing, notifications & alerts, or decoupled microservices similar to Queueing Services.
   7. Examples: Apache Kafka, AWS SNS
6. Load Balancer
   1. Distribute incoming traffic to multiple servers or resources to ensure optimal perfromance, high availability, and reliability of a system or application.
   2. Continuously monitors the health of the destination servers to make sure requests aren't routed to an unhealthy server.
   3. Uses a pre-defined algorithm (Round Robin, least connections etc) to determine which server should handle the request.
   4. Different kinds of load balancers for HTTP or UDP/TCP Traffic etc.
   5. Ensures that client requests are routed to same server to ensure session data isn't lost.
   6. Common use cases include web applications, database servers, or microservices.
   7. Examples: Nginx, AWS ELB
7. Columnar Store (Cassandra)
8. Logging
   1. Elasticsearch / Opensearch
      1. Enables a search and analytics engine to query the logs and analyze large volumes of structured or unstructured data
      2. Stores data in a searchable index format allowing for complex queries and analysis.
      3. Allows for high availbility & scalability
      4. Can be built as a distributed system w/ multiple shards (aka servers) that hold the same data, enabling redundancy & high availbility.
   2. Cloudwatch
      1. Stores logs as JSON-formatted events, providing simple, quick search capabilities
      2. Integrates directly w/ all AWS Services like EC2, Lambda, ECS etc.

## CAP Theorem
CAP theorem is a fundamental principle in distributed systems that describes the trade-offs and constraints when designing and implementing distributed databases & systems. 

The three components of the CAP theorem are as follows:

1. **Consistency (C)**:
   - Consistency in the context of the CAP theorem means that all nodes in a distributed system have a consistent view of the data at all times. In other words, if a piece of data is updated, all subsequent reads will reflect that update.

2. **Availability (A)**:
   - Availability means that the system remains operational and responsive, even in the presence of failures. Every non-failing node in the system must respond to requests, ensuring that the system is available for use.

3. **Partition tolerance (P)**:
   - Partition tolerance refers to the system's ability to continue functioning and providing consistent responses even in the face of network partitions, where some nodes can't communicate with each other due to network failures.

According to the CAP theorem, in a distributed system, you can only achieve two out of the three properties—Consistency, Availability, and Partition tolerance. It's not possible to simultaneously achieve all three. This theorem has significant implications for designing and managing distributed databases and systems.

Here are the three possible combinations under the CAP theorem:

- **CA**: Prioritizes Consistency and Availability, sacrificing Partition tolerance. In the event of a node failure, the system will sacrifice availability to ensure consistency.
  
- **CP**: Prioritizes Consistency and Partition tolerance, sacrificing Availability. In the event of a node failure, the system will sacrifice availability to maintain a consistent view of the data.
  
- **AP**: Prioritizes Availability and Partition tolerance, sacrificing Consistency. The system will remain available and responsive even during network partitions, potentially resulting in temporary inconsistencies in the data until it's able to be corrected.


## Interview Tips
1. Ask clarifying questions
2. Get a general about broad numbers & scale
   1. How many users / requests / orders etc do we expect
      1. 100,000 active users per month
      2. 23,000 per week
      3. 3,300 per day
      4. ~2,400 users during peak hrs (7am - 9pm)
3. Auto scaling automatically to meet demand at peak hrs and then scale down during periods of low traffic
Hot reads




Example
Read heavy platform - twitter
Write heavy platform - ticket design system (ticketmaster)
