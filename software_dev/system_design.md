# System Design
Hot Reads

## Tools
1. Relational Database
2. Key Value Store
3. Caching Store
4. Pub sub / Queuing
5. Load Balancer
6. Columnar Store (Cassandra)
7. Logging

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
