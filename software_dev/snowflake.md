# Snowflake

## Micropartitions
[Article](https://select.dev/posts/introduction-to-snowflake-micro-partitions)

Snowflake stores data in a closed-source File Format in S3.  Files are stored uncompressed typically ranging between 50-250 MB.  

Snowflake does this to enable query-pruning, a concept which tries to arrange the micropartitions in a way so similar data is stored close together depending on your query pattern.
- If you have a table that everybody filters on the `created_date` column, then Snowflake can automatically avoid doing a full table scan because it knows it only has to query the micropartitions that fall under that `WHERE` clause condition.

Micropartitions have pre-calculated metadata assigned, with things like min and max date, number of records, and other things.  This is why `count(*)` is so fast and this metadata helps query-pruning as well.

You'll get better query performance if you select only the minmimum number of columns you need for the query, as Snowflake uses byte-range querying to grab the data from the micropartitions (aka if you do `select *` it has to do more work).

## Virtual Warehouses
Typical databasees revolve around a single server storing data & executing queries.  Snowflake separates the concept of compute and storage so all of your data is stored in S3, and you query it from individual compute warehouses.  

These warehouses start as 4 vCpu, 16 GB memory instances at the X-SMALL size.  They double in compute/performance resources as you move up from X-SMALL to SMALL, MEDIUM, and LARGE etc.

Warehouses are always off but automatically turned on when queries are executed.  They auto-suspend after a set amount of time (typically 3 or 5 minutes).  You'll continue paying for these warehouses until they're turned off.

You're charged a minimum of 60 seconds for warehouse use.  
- If you execute a query that runs for 5 seconds, you'll be charged for 60 seconds.
- If you execute a query that runs for 1 minute 30 seconds, you'll be charged for 1 minute 30 seconds.

Warehouses share an account-wide cache which caches query results within the last 24 hours (provided the queries are identical and the underlying data hasn't changed).

## Clustering Key
[Article](https://select.dev/posts/introduction-to-snowflake-clustering)
[Article 2](https://www.linkedin.com/pulse/clustering-key-design-101-snowflake-minzhen-yang/)

Snowflake offers the concept of Clustering Keys which are used to arrange micropartitions in a way so that similar data is stored close together in S3.  This is useful for performance reasons if you know your query patterns ahead of time and your current queries are taking a long time on larger tables.

This process happens naturally if you continously insert new records into a table with some form of a `inserted_at` timestamp column.  As new data comes in they will naturally go into new micropartitions and will be stored close together.

You can do this manually with 1 `clustering key` by recreating the table like below using an `ORDER BY` statement.
For transformations:
```
create or replace my_table as (
  with transformations as (
    ...
  )
  select *
  from transformations
  order by my_cluster_key
)
```

For already-created tables:
```
create or replace table sales as (
  select * from sales order by store_id
)
```

If you need to cluster the micropartitions together on 2 or more columns, then you have to use the actual Cluster Syntax.

```
-- you can cluster by one or more comma separated columns
alter table my_table cluster by (column_to_cluster_by, column_to_cluster_by);

-- or you can cluster by an expression
alter table my_table cluster by (substring(column_to_cluster_by, 5, 15));
```

## Query Profile
[Article](https://select.dev/posts/snowflake-query-profile)

## Internals
Managed OLAP DBMS written in C++.
- Shared-disk Architecture with aggressive compute-side local caching
- Entirely written from scratch
- Custom SQL Dialect
- Push-based Vectorized Query Processing
- Precompiled primitives
- No Buffer Pool
- PAX Columnar Storage
- Sort Merge(?) + Hash Joins

Flexible Compute
- When there's a large query, Snowflake will temporarily run portions of your query plan on additional worker nodes to accelerate performance.
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/33482546-9a86-4a1d-a9d4-6b3ab076d965)
- The professor seems to imply that it might be using "other customer's" idle Worker Nodes to do stuff like this
- I can see the benefit.  You're basically overcharging customers a bit, but the performance and reliability is so good that they're kinda fine with it

S3 is slower than local disk, and each I/O has higher CPU overhead because of HTTPS API calls.  But it supports fetching offsets from files, which enalbes DBMS to fetch headers and determine what portions of each file it needs.  Snowflake decided to invest heavily in its own caching layer to hide the costs of doing all these lookups to S3.
- Faster Query Performance, less calls to S3, win win for everybody

Snowflake Storage Format
- All data is stored in a proprietary data format - micropartion files.
- Immutable Files using PAX Storage Format, similar to Parquet
- Typically ~ 50-500 MB but ends up around 16 MB per File.
- Automatically re-clusers and re-arranges micropartitions based on query access patterns.  This is the Snowflake Cluster Key.  It presorts the data so you can figure out exactly what data you want to bring in for each query.
- You pay a little more to do this reclustering, but the reads can become much improved performance wise.