# Chapter 1 Foundations of Data Systems
Systems should be Reliable, Scalable, and Maintainable.

Find out the proper percentiles to optimize performance / latency for.  It might make sense to optimize the 95th percentile to maximize customer satisfaction + sales, but 99.9% would be too expensive and not worthwhile.

Service Level Objectives (SLO) and Service Level Agreements (SLA) define the expected performance and availability of a serivce. 
    * Service is considered up if it has median response time of less than 200ms and 99th percentile under 1 second.

It's hard to scale architectures.  If your load is x and the new load is 10x then the original architecture might not hold up.
    * Elastic systems can automatically scale in & out to match this load and continue operating at peak performance.  
    * Others have to be manually adjusted by a human and are slower to change and generally more error prone.
    * Scaling out to multiple systems introduces a shit ton of complexity, so try to stick to single machine processes until you're forced to make it distributed.

Maintainability - there's a cost to maintenance, fixing bugs, keeping systems operational, and investigating failures.  
    * Make systems that focus on operability, simplicity, and evolvability.
      * Operability - Easily view the health of the system, keep software up to date, establish good practices for testing + deployment.
      * Simplicity - manage the complexity, don't have hidden assumptions, reuse code instead of reimplementing it multiple times.

# Chapter 2 Data Models and Query Languages
Data Models - Relational vs Documents

SQL is very popular for relational which is consisted of tables of columns and rows.  It has better support for joins and many-to-many and many-to-one relationships.

NoSQL offers different benefits from the relational model.
    * Offers greater scalability (both distributed computing, and not having to be locked by ACID transactions).
    * Generally more open source than historically with company's like Oracle and Snowflake in the SQL space.
    * Specialized query operations different from those with the relational model.
    * Schemaless freedom that you don't get with relational model.

SQL historically had issues with XML + JSON and the schemaless nature of these data formats, which made NoSQL formats more enticing.  Nowadays that's not the case, and both frameworks are moving closer to supporting the same features more or less.

## Many-to-One and Many-to_Many Relationships
These relationships fit in SQL but are hard to implement in NoSQL.

Relational DB the query optimizer automatically figures out which parts of the query to execute in which order, creating the "access path" for you.  SQL is a declarative language so we just define the pattern of data we want and what conditions must be met, but not HOW to do it.  That's the query optimizer's job.  This format also allows parallel processing to be easily implemented across multiple machines.

`Schema on read` means the structure of the data is only interpreted when the data is read, so is essentially schemaless when you store it.

`Schema on write` means the structure of the data is defined when you store it.  Think `CREATE TABLE sales as day DATE, sales INT, owner CHAR` etc.

Schema changes screw a lot of things up and both approaches have their upside + downside.
    * For schema on read, you may have a schema change that you never know about because you don't enforce it.
    * For schema on write, your code may fail when a new column appears.

## Graph-like Data Models
SQL can handle many to many relationships, NoSQL has a hard time, so if you want the NoSQL and have a lot of many to many relationships think about using graph data models.

Graph consists of vertices (nodes or entities) and edges (the relationships).
    * Social graphs - verticies are people with the edges being the people they're friends with.
    * Web graphs - verticies are pages, and the edges are the HTML links to other pages.

Graphs can also link data that aren't typically associated with each other.

Graph Models typically don't enforce a schema for the data they store, so it can easily adapt to changing business requirements.

# Chapter 3 Storage and Retrieval
Indexes are used to basically store a small amount of metadata about how to query the data you want.  They slow down writes, but improve query times.  So you usually shouldn't index everything.  Know your query patterns before hand.

RAM is generally orders of magnitude faster and more performant for reading data from than reading from disk.  This is why caches are so fast & used so often.

In-memory Databases are fast not only because they read from RAM, but because most of them are designed to never have to write to disk in the first place and they have the luxury of removing all of that overhead out of data structures used in the Application or Tool.

Advantages of storing data on disk vs RAM:
- Disk is more durable (data contents are not lost if power is turned off)
- Disk is a lower cost per GB than RAM

As RAM becomes cheaper, the cost per GB argument slowly erodes.

Data Warehouses use column-oriented storage where the data isn't stored in rows together, but instead the data is stored where all of the values from each column are stored together.  This allows much faster analytical queries so long as you avoid `select *`.

It doesn't matter which columns are stored in which order when working in column-oriented storage.

Column-oriented storage also benefits from compressing the data.  Instead of storing the data as-is someplace, it compresses the data into a lower level format to save on storage space.  The data is for all purposes still "correct", it's just stored in a different format.
- This leads to performance benefits during query execution.  When data is pulled in a compressed format and sent over to the CPU for processing, there are efficiency gains because more data can fit in memory and be sent to the CPU, making use of more efficient CPU cycles.

# Chapter 4 Encoding and Evolution
Staged rollout - server side technique when you update a very large application base so only a few nodes at a time get the new version.  In client side apps this won't work, bc you can't really force the client to update.
    * Old and new versions of code and releases might co-exist at the same time.
    * Backwards Compatibility - Newer code can read data written by older code
    * Forward Compatibility - Older code can read data written by newer code.

Encoding - when you want to send data over a network, you have to encode it as some kind of self-contained sequence of bytes.  You can't use your personal PCs internal pointers anymore where the data sits in memory, which is why this sequence of bytes look different than what we're used to.
    * Serialization - Turning in memory objects into a series of bytes to store it or transmit it somewhere.
    * Deserialization - Turning an unreadable series of bytes into an object you can interact with in memory.
      * Takes time for the CPU to deserialize the bytes.
    * Python example - `pickle` library
      * Stores in memory objects as a sequence of bytes.
      * It becomes difficult to share these things across programming languages.

File Types
    * XML used to be used a lot but it's very verbose and complicated
    * JSON used a lot bc it's natively supported by web browsers, can distinguish numbers and strings but precision (float values etc) can get fkd up.
      * Uses a lot of space compared to binary formats.
    * CSV used a lot but everything is represented as strings

## Binary Encoding
Protocol buffers are binary encoding libraries that require a schema for any data encoded.  Comes with a code generation tool in your respective programming language to create the classes + schemas for you.  Array / list fields - `repeated` object type.
    * Lightweight and compact bc field names are ommitted from the encoded data.
    * Schema is a valid form of documentation to see what the message is made up of.

Avro is similar but different to protobufs, it has a schema and has 2 versions for humans to read and machines to read.

Service Oriented Architecture - decomposing a large application into smaller services by area of functionality so they request things they need from each other.
    * Goal is to make application easier to change and maintain by making each service independently deployable and evolvable.

Web Service - when HTTP is the protocol for talking to a service.

REST is a design philosophy to emphasize simple data formats, using URLs to identify resources, and using standard HTTP features for authentication and requests.
    * Commonly use JSON.

Remote Procedure Protocol (RPC) - make a request to a network service look the same as calling a function in a programming language
    * Flawed bc networks are inherently unpredictable.  
      * Can be unavailable, no internet, inconsistent response times, or timeout.

Message Broker - messages get sent to a queue or topic, and the broker ensures the message is delivered to one or more consumers or subscribers to that topic.
    * Rabbit MQ, Kafka etc.
    * Pub / Sub architecture.

# Chapter 5 Replication
If your data doesn't change over time then replication is easy, you copy data to every node once and you're done.  The problem becomes when your data changes and you have to still be doing replication.  

`Replicas` are nodes that store a copy of the database.  How do you ensure all of the data ends up on the replicas.  

`Leader Based Replication` is the most common strategy to solve this.
    * One of the replicas is designated to be the leader.  When clients want to write to the database, they send their request to the leader.
    * The other replicas are followers, and when the leader writes new data to its local storage it sends out the data change to all of these followers via a replication log and they each make the change accordingly.  
    * Writes are only accepted on the leader, however, reads can happen to either the leader or the follower.
    * Distributed message brokers like Kafka and RabbitMQ also use this.

## Asynchronous vs Synchronous Replication
Synchronous - the leader waits til it has received a success message from the replica that the write was successful before completing the actual update and making it visible to other clients.
    * Advantage is the follower is guaranteed to have an updated copy of the data consistent with the leader.  
    * Disadvantage is if the follower is unavailable (crashed or network issue) then the write cannot happen until follower is available again.
      * Any node that is down can cause the whole system can come to a halt.
      * Possible to have 1 synchronous node and the others async.  if this synchronous one fails, one of the async ones becomes synchronous. - `semi-synchronous`.

Asynchronous - the leader sends the data change but doesn't wait for a response from the follower.
    * Most commonly used.
    * leader can continue processing updates even if the followers fails.
    * Problems if user requests data too quickly after making a write.
    * `read-after-write consistency` is a guarantee that if the user reloads the page after a write, they will see the updates they submitted themselves.

Followers can take a few minutes to recover if they just failed and are waiting to get new changes from the leader, or if there are network problems between nodes.

New Followers - take a snapshot of leader's database, copy it to the new follower, and then the new follower reqeusts all new data changes that have happened since the snapshot.  Once it processes this backlog, the follwoer has caught up.

System has to continue working when a node fails.  
    * Follower - Each node knows the last trasnaction it processed before the fault occurred.
    * Leader - Much trickier.  One of the followers needs to be promoted to the leader and the clients need to be reconfigured to send writes to the new leader.  This is called `failover`.
      * Failover can happen manually or be triggered when the leader is known to have failed - crash, pwoer outage, network issue etc.  Most systems use a timeout process where if no message has responsed for 30+ seconds it's assumed to be dead.
    * New leader - Election process where leader is chosen by a majority of remaining replicas, or appointed by a previously elected controller node.  The new leader typically is the one that has the most up to date changes from the old leader.
    * Things get complicated if the old leader "comes back".  Also - if async replication, the new leader might not have gotten all the most recent changes before the last one went down.

Leader writes all write requests to a statement log to its followers.  Every INSERT, UPDATE, or DELETE statement is forwarded to the followers.
    * Nondeterministic stuff like now() or RAND() will not be the same value on every replica.
    * Autoincrementing fields might get fkd up.
    * stored procedures and UDFs might not be consistent.

## Write-ahead log (WAL)
An Append-only sequence of bytes containing all writes to the database.  Used in Postgres.  Tracks which bytes were changed in which disk blocks.  Different software versions between replicas can screw this up.

## Logical (row-based) log replication
An alternative where replication log is decoupled from the storage engine.  Sequence of records describing writes to a database where it has enough info to uniquely describe each row that was changed.  Easier to keep backwards compatible.  Easier for external systems to parse.

## Trigger based replication
Trigger lets you run custom application code when data changes occur in a database system.

## Multi Leader Replication
Typically used for massive scale operations with multiple datacenters.  One datacenter goes out -> you're still operational.  Internet goes out -> you're still operatinal.

I skipped a ton after this.

## Partitioning
Partitions in databases are called shards in MongoDB and Elasticsearch, and vnodes in Cassandra.  All the same concept.

Partitions are each piece of data belonging to one partition.  You want this for scalability, a large dataset can be distributed across multiple disks, and thus the query can be distributed across multiple processors.

Each record belongs to exactly one partition, but may still be stored on several different nodes for fault tolerance.

The goal is to evenly spread the data and query load.  However, if partitioning is unfair and skewed then this makes it a more inefficient process.  So you have to keep partitioning spread evenly, but you also want to distribute your data logically (putting similar stuff on the same partition so you only have to access 1/10 partitions for a specific query rather than loading all 10 in).


## Hot Spots
Consider you have a social media site, where 99.9% of users have less than x amount of followers and engagements.  But then think about how you would handle somebody like Taylor Swift, who has hundreds of millions of followers and who's posts generate orders of magnitude of more engagements than normal users.
- This scenario relates to a problem called Hot Spots
- These events can lead to a large number of writes or reads to the same key (user id of the celebrity) which leads to a skewed workload.
- Just have to find a way to horizontally scale the problem to multiple machines.
- As of 2023, there is no way data systems do this automatically.  Every Application is different; hot spots are an unusual but common problem and while challenging, there are ways of solving the problem.


# Chapter 7 Transactions

Lots of things can go wrong in data systems:

- Database software or hardware might fail
- App might crash
- Network interruptions
- Race conditions between clients

This is why they have to be fault tolerant, which is hard to implement properly.

Transactions have been used for decades to address these problems. They're a way of grouping reads and writes toether into a logical unit that are executed as one operation that either succeeds (commit) or fails (rollback). They come be default in many Relational SQL Databases nowadays.

NoSQL databases gained popularity in the late 2000s by incorporating replication and partitioning by default, but also abandoned transactions or offered a much weaker set of guarantees for them. They did this because for the sake of scalability they believed they needed to drop transactions.

The safety guarantees provided by transactions are often described the ACID.

- Atomic - All operations in the transaction successfully commit, or none of them do.
- Consistent - The database will always remain in a valid state before and after transactions. Constraints like primary keys and not null checks will always be checked
- Isolated - Transactions are executed independently frm one another and their intermediate states are not visible to each other. This prevents concurrency issues and maintains data consistency even as transactions are being processed simultaneously.
- Durable - Once transactions are committed, they will stay in the database even if there is a hardware fault or database crash.

Multi object transactions are ones that involve multiple statements inside 1 transaction. Typically only relational databases offer this

``` sql
BEGIN TRANSACTION;
UPDATE Accounts SET Balance = Balance - 100 WHERE AccountID = 1;
UPDATE Accounts SET Balance = Balance + 100 WHERE AccountID = 2;
COMMIT;
```

A lot of these concepts simply aren't implemented this way in other non-relational databases, so watch out. A lot of leader-based replication sharding solutions follow a best effort basis which basically means "the database will do what it can, and if it runs into an error then it wont do something that's already been done", leaving it to the application to recover from errors.

If two transactions don’t touch the same data, they can safely be run in parallel, because neither depends on the other. Concurrency or race condition issues only happen when one transaction is reading data that is being modfiied by another, or when they're both trying to modify the same data. These can be tricky bugs as they are difficult to reproduce.

Read committed data means that you only read data that has been committed to the database. When writing to the database, you will only overwrite data that has been committed.

- A dirty read is one where the data you're reading hasn't been committed to the database yet. That means there's a separate transaction that wrote data to the database, but hasn't committed or aborted the transaction yet. These scenarios must be prevented by the database.
- A dirty write is where the data being written is overwriting an uncommited value. Example: Alice books a reservation that is saved to the database but not committed, but then Bob swoops in and books the same reservation and it's saved to the database. The Application might have told both Alice and Bob that their reservation was successful, but only 1 record for Bob for it exists.

To counter these issues, Database often use row-level locks which mean to write that data, it must first acquire the row-level lock on that object, and hold that lock until the transaction is committed or aborted. If another transaction wants to come write to that same object, it must wait for the first trnasaction to give up the lock.

That's only for writes though. Reads shouldn't use the same row-level lock, because what if you have 1 long-running write transaction hogging up the resources ? This hurts response time for consumers. While the write transaction is ongoing, any other transactions that read the object are simply given the old value.

Snapshot Isolation means that every transaction reads from a consistent snapshot of the database where it sees all data that was committed in the database at the start of the transaction. Even if data is subsequently changed by another transaction, it will only see the old data at that particular point in time. This is used for heavy analytical queries and backups.

Readers never block writers, and writers never block readers. This allows databases to handle long running read queries at the same time they allow writes.

At the start of a transaction, the databases makes a list of all other transactions in progress so it can ignore them. Any writes made afterward are ignored, and any transactions with a later transaction id are ignored.

Left off page 242