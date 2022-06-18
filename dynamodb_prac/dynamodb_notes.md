# Dynamodb

Use Dynamodb over SQL because it's schemaless.  You only define the Primary Key for the table and its data type, and then you can upload JSON documents into the Dynamodb table.

Under the hood it's a partitioned B-Tree data structure.

If you store something to dynamodb you can immediately read it back and have guarantees what you store will never get lost.

Requires you to do most of the data querying within your application, hence it's not as flexible as SQL.

Can manage structured or semistructured data.

Used for general purposes applications and/or web to store and fetch document data.

There are no joins or group bys, so your scalability in dynamodb is much more predictable.  Can handle many requests at once without sacrificing performance.

Indexes are offered to help increase scale even more.

Less storage efficient than RDS, but this shouldn't really be a concern.

NoSQL Databases scale horizontally by splitting data into segments and performing the query in each of those segments.

Less flexibility than SQL Databases bc of the limited ways you can store and query the data.

Still, you probably don't need to go with a NoSQL solution unless you know what you're doing, you need the scalability, or you need key/value pair lookups.  

You absolutely need to know your data access patterns in advance before exploring this solution.

## Pricing
Provisioned
    - used for predictable / normal workloads.
    - You define the write / read compute resources up front.
    - Free tier is 25 / 25 of provisioned capacity.

Pay Per Request
    - used for unpredictable workloads.
    - It will scale up and down as needed.


## Database Cheat Sheet
SQL (Postgres, MySQL, etc): Relational (I NEED TO DO JOINS)
NoSQL (Mongo, DocumentDb): Non Relational (I NEED TO STORE/SEARCH/PARSE BLOBS)
Key Value (Redis, Dynamodb): Non Relational, fast (I NEED TO STORE KEY VALUE PAIRS)
Data Warehouse (Snowflake, Redshift): Relational (I NEED TO RUN SOME BIG QUERIES w/ MPP and massive compute resources)