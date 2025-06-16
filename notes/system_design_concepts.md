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




# Common Elements

Using an API gateway to route requests to various services rather than having the frontend directly call your microservices offers numerous benefits:

### 1. **Centralized Control and Management**
- **Single Entry Point**: An API gateway acts as a single entry point for all client requests, simplifying the architecture and making it easier to manage and secure.
- **Security**: Centralizes security features such as authentication, authorization, rate limiting, and SSL termination, reducing the attack surface and simplifying the enforcement of security policies.

### 2. **Traffic Management**
- **Load Balancing**: Distributes incoming traffic across multiple instances of your microservices, improving availability and reliability.
- **Rate Limiting and Throttling**: Protects backend services from being overwhelmed by too many requests, ensuring better performance and stability.

### 3. **Performance Optimization**
- **Caching**: Can cache responses from services to reduce load and latency for frequently requested data.
- **Compression**: Compresses responses to reduce the amount of data transferred, speeding up communication with clients.

### 4. **Protocol Transformation**
- **Protocol Handling**: Translates between different protocols (e.g., HTTP, WebSocket, gRPC), allowing services to use the protocols most suited to their needs while presenting a unified interface to clients.

### 5. **Simplified Client Interface**
- **API Aggregation**: Combines multiple service calls into a single API call, reducing the number of requests the client needs to make and simplifying the client-side code.
- **Version Management**: Handles API versioning, allowing multiple versions of the API to coexist and facilitating smooth transitions between API versions.

### 6. **Improved Developer Experience**
- **Consistency**: Provides a consistent API for all services, making it easier for frontend developers to interact with the backend.
- **Documentation and Discovery**: Often integrates with tools to automatically generate API documentation, making it easier for developers to understand and use the available APIs.

### 7. **Security Enhancements**
- **Authentication and Authorization**: Centralizes authentication and authorization, ensuring that all requests are properly authenticated and authorized before reaching the services.
- **Data Validation**: Validates incoming requests and responses to ensure they meet the required formats and constraints, enhancing security and stability.

### 8. **Service Discovery and Flexibility**
- **Service Discovery**: Integrates with service discovery mechanisms to dynamically route requests to the appropriate service instances, supporting scalability and flexibility.
- **Flexible Routing**: Routes requests based on various criteria (e.g., URL paths, request headers, or user roles), allowing for more complex and customizable routing logic.

### 9. **Monitoring and Analytics**
- **Centralized Logging**: Aggregates logs from multiple services, providing a unified view of all incoming and outgoing traffic.
- **Metrics and Monitoring**: Collects metrics and provides monitoring capabilities, helping to identify performance bottlenecks and other issues more easily.

### Conclusion

An API gateway offers significant benefits over direct frontend-to-microservice communication by providing centralized management, improved security, performance optimization, and a simplified client interface. It enables better scalability, reliability, and maintainability of a microservices architecture, making it an essential component in modern distributed systems.


## WebSockets

WebSockets provide a persistent TCP style connection between client and server allowing for real time bidirectional communication with support for web browsers. They're initiated by an "upgrade" protocol on an existing TCP Connection to change L7 protocols.

- It allows either the client or the server to push data to the other without being prompted by a new request


1. Client initiates WebSocket handshake over HTTP (with a backing TCP connection)
2. Connection upgrades to WebSocket protocol, WebSocket takes over the TCP connection
3. Both client and server can send binary messages to each other over the connection
4. The connection stays open until explicitly closed

WebSockets just allow you to effectively have a channel where you can send binary packets to the server from the client and vice versa. This means you'll need some way of defining what it is your client and server are exchanging.

- JSON messages are a great option here

WebSockets come up in system design interviews when you need high-frequency, persistent, bi-directional communication between client and server. 

- Real time applications, games etc
- Chat applications
- Live sports or stock tickers
- Collaborative editing (Google Docs)

WebSockets are powerful, but the infra required to support them can be expensive and the overhead of stateful connections (especially at scale) will require significant accommodations in your design.

## WebRTC

WebRTC enables direct peer-to-peer communication between browsers without requiring an intermediary server for the data exchange. It's the only application level protocol that uses UDP

- Perfect for collaborative apps like document editors, video/audio calling, and conferencing applications

Most clients dont allow inbound connections for peer to peer type use cases for security reasons.

The WebRTC standard includes two methods to work around these restrictions:

- STUN: "Session Traversal Utilities for NAT" is a protocol and a set of techniques like "hole punching" which allows peers to establish publically routable addresses and ports. As hacky as it sounds it's a standard way to deal with NAT traversal and it involves repeatedly creating open ports and sharing them via the signaling server with peers.
- TURN: "Traversal Using Relays around NAT" is effectively a relay service, a way to bounce requests through a central server which can then be routed to the appropriate peer.

There's effectively 4 steps to a WebRTC connection:

1. Clients connect to a central signaling server to learn about their peers.
2. Clients reach out to a STUN server to get their public IP address and port.
3. Clients share this information with each other via the signaling server.
4. Clients establish a direct peer-to-peer connection and start sending data.

WebRTC is an absolute pain to get right and even the best implementations still suffer connection losses. It truly is a niche solution.

## Load Balancing

For scaling, we have two options: bigger servers (vertical scaling) or more servers (horizontal scaling).

- Modern hardware is very powerful, vertical scaling is definitely easiest
- The most common pattern you'll see is horizontal scaling though, which means you must setup your servers to be horizontally scalable
- This means no in-memory caches on the servers themselves, using remote databases like Postgres + Redis as the source of truth etc

With client-side load balancing, the client itself decides which server to talk to. Usually this involves the client making a request to a service registry or directory which contains the list of available servers.

- The client will need to periodically poll or be pushed updates when things change.
- Client-side load balancing can be very fast and efficient. Since the client is making the decision, it can choose the fastest server without any additional latency
- Redis is a good example of this wherew you can ask for the different shards and the client can pick the one it wants to write to

Layer 4 load balancers operate at the transport layer (TCP/UDP). They make routing decisions based on network information like IP addresses and ports, without looking at the actual content of the packets.

- The effect of a L4 load balancer is as-if you randomly selected a backend server and assumed that TCP connections were established directly between the client and that server.
- Great for WebSockets or other protocols that dont require persistent connections

Layer 4 load balancers have some key characteristics, they:

- Maintain persistent TCP connections between client and server.
- Are fast and efficient due to minimal packet inspection.
- Cannot make routing decisions based on application data.
- Are typically used when raw performance is the priority.

Layer 7 load balancers operate at the application layer, understanding protocols like HTTP. They can examine the actual content of each request and make more intelligent routing decisions.

- They receive an application-layer request (like an HTTP GET) and forward that request to the appropriate backend server.
- They're are great for HTTP-based traffic which means basically everything besides WebSockets

Layer 7 load balancers have some key characteristics, they:=

- Terminate incoming connections and create new ones to backend servers.
- Can route based on request content (URL, headers, cookies, etc.).
- More CPU-intensive due to packet inspection.
- Provide more flexibility and features.
- Better suited for HTTP-based traffic.

While load balancers play a key role in distributing load and traffic, they are also responsible for monitoring the health of backend servers. If a server loses power or crashes, the load balancer stops routing traffic to it until it recovers.

- To do this, load balancers use health checks. Health checks are a way for the load balancer to determine if a server is healthy. They can be configured to check the server at different intervals and with different protocols.
- Load Balancer might make a health check request to the backend server every 60 seconds to ensure it's getting a 200 response so it knows it's okay to route traffic to that server

Load Balancing Algorithms are used to distribute traffic:


- Round Robin: Requests are distributed sequentially across servers
- Random: Requests are distributed randomly across servers
- Least Connections: Requests go to the server with the fewest active connections
- Least Response Time: Requests go to the server with the fastest response time
- IP Hash: Client IP determines which server receives the request (useful for session persistence)

Round Robin and Random are typically appropriate to use.


Light travels through fiber optic cables at about 2/3 the speed of light in a vacuum, which is approximately 200,000 km/s. This means a round trip between New York and London (about 5,600 km) has a theoretical minimum latency of around 56ms just from the physics of signal propagation, before adding any processing time. This physical constraint is why geographic distribution is essential for low-latency applications.

- In order to address this problem, we need to return to data locality. Across all of computing, we're going to have highest performance when the data is as close as possible to the computations we need to do.

This is where Content Delivery Networks (CDNs) come in. The goal of a CDN is to reduce latency by using a network of servers strategically located around the world in what are known as edge locations.

- If those edge locations are nearby and can answer a client's request, then the client is going to get lightning fast response times.
- This is only enabled via caching. We're essentially setting up caches on all of these edge locations to serve content to users faster
- This is especially effective for static content like images, videos, and other assets.
- Using a CDN as a cache for e.g. search results on Facebook allows us to both minimize latency and reduce the load on backend servers.

Regional Partitioning is splitting data by geographic region so that each region’s data is stored and processed closer to where it’s needed, improving performance and scalability.

- Uber for example could split up sections of the US into Northeast, Southwest etc, give each one its own database, host those databases in regional data centers in the area to maximize performance when users make requests in those locations
- This reduces latency, localizes failures, and scales independently by region.
- But, this has tradeoffs and introduces complexity and global consistency is much more difficult, and cross region queries become harder

When dealing with failed requests, timeouts, and re-tries, retry with exponential backoff is typically the go-to.

- If a request fails, try again 10 seconds -> 30 seconds -> 2 minutes later etc
- can cap it at 2 minutes which is capped exponential backoff
- Jitter can be introduced which introduces some randomness to the backoff so you dont have millions of clients all trying their backoff requests at the same time if you had some service interruption
- https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/

Idempotent APIs are critical for payment processing systems to ensure customers aren't double charged or anything like that.
