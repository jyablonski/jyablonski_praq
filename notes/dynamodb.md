# DynamoDB

[Video](https://www.youtube.com/watch?v=HaEPXoXVf2k&ab_channel=AmazonWebServices)

DynamoDB is a fully managed, serverless NoSQL database service by AWS, designed for high-performance applications with low-latency reads and writes. It stores data in tables, where each item must have a partition key attribute, and can contain any number of additional attributes. DynamoDB supports both key-value and document-style data models, with flexible, schema-less records.

Core Concepts:

- It stores data in tables similar to SQL
- An item in a table is a single record, similar to a row in SQL
- An attribute is a field within an item.
- A primary key is used to distribute data across partitions
- A sort key can be set to allow range queries like ==, <, >, between, contains, in, top / bottom n values etc
- Secondary global index enable queries with different partition or sort keys
- Secondary local index shares the same partition key, but has a different sort key
- Scales horizontally very easily, and it auto scales automatically depending on your actual traffic
- There is no concept of joins in NoSQL which is the whole point, the solution doesn't support that in order to optimize for low latency, fast response times, and horizontally partitioned storage
- NoSQL does not mean non-relational
- RDBMS are still relevant.
- Use NoSQL for OLTP at scale, use SQL for OLAP or OLTP when scale isn't as critical

Downsides compared to SQL:

- Limited data model flexibility, you have to know 100% of your query patterns up front
- More complex data modeling than relational databases
- Expensive for large workloads if not designed efficiently
- Bad for any kind of heavy analytics or reporting

Advanced Features:

- DAX is an in memory cahcing layer that provides even faster response times for read-heavy workloads
- DynamoDB streams are able to pickup all write operations on a table and can enable CDC type workflows for things like a Lambda picking up all recent DynamoDB writes and sending them to ElasticSearch etc

When to not use Dynamodb:

- When you have complex query patterns, because DynamoDB is not optimized for complex joins and subqueries
- When your use case involves multi-table transactions
- When you have a complex data model - making a ton of secondary indexes is not a good thing

Partition keys work to uniquely identify an item by:

- Building an unordered hash index for each record
- Using that hash index to determine what physical node or partition to store that given item
- This enables massive horizontal scaling by the ability to shard data across many machines
- This enables access in constant time to any item no matter how large the dataset is
- When applied with a sort key, the data is also sorted by the sort key to enable faster reads when the sort key is utilized in queries
- Partitions are also three-way replicated
    - If you make an eventually consistent read, the read will go either the primary or the replica nodes
    - If you make a strongly consistent read, the read will go to the primary node
- You should create tables where the partition key has a large number of distinct values and those values are requested uniformly as random as possible, to avoid any single partition from getting overloaded
    - Good Example: customerId, deviceId
    - Bad Example: status, gender
    - Bad partition key will lead to a hot access pattern where a majority of requests are hitting only a single partition of data

Good Sort Keys enable a lot of the magic w/ DynamoDB

- Enables efficient query patterns
- Allows you to leverage range queries
- Good sort key example: orders and orderitems
- Bad sort keys will lead t

Local Secondary Indexes allow you to re-sort the data in the partitions

- You set these up when you want to enable a different kind of access pattern
- But, these must always to use the same partition key as the table. It's a way to re-sort the data but not re-group the data
- These are strongly consistent

Global Seconary Indexes allow you to re-group the data in a table by setting a new partition key

- These are eventually consistent
- If you're writing data into the table faster than the GSI can keep things updated, then eventually you're going to get backed up and writes will be throttled until it catches up

Best Practices:

- Start out with 1 table. Building multiple tables or even dozens of table for an application is not a good idea

Composite keys (also called compound primary keys) are used to uniquely identify an item using two attributes instead of one

- They help enable hierarchy relationships so you can model your data in 1 table, rather than in multiple tables which would require many more reads
- Reduces query complexity