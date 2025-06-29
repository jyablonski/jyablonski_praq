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
- Scales horizontally

Downsides compared to SQL:

- Limited query flexibility
- More complex data modeling than relational databases
- Expensive for large workloads if not designed efficiently
- Bad for any kind of heavy analytics or reporting

Advanced Features:

- DAX is an in memory cahcing layer that provides even faster response times for read-heavy workloads
- DynamoDB streams enable CDC type workflows, which enable workflows like a Lambda picking up all recent DynamoDB writes and sending them to ElasticSearch etc

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