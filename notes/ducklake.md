# Ducklake

[Blog Post](https://duckdb.org/2025/05/27/ducklake.html)

Ducklake is a Data Lakehouse format that utilizes a standard SQL Database to manage all metadata, instead of doing it via files in S3. The actual data being stored is still in open formats like Parquet.

## Historical Data Lakehouse Context

Apache Iceberg and Delta Lake introduced ACID transactions to data lakes, allowing for many data producers to update data in a consistent and safe way in their data lakes. These brought some form of sanity back to making changes to tables while still operating in blob storage.

- They use a series of JSON and Avro files to define schemas, snapshots, and historical Parquet files to support features like time travel and schema evolution

To improve this metadata management, the concept of a catalog service to sit on top of the files was introduced.

- The catalog typically manages all table folder names, and keeps pointers to the latest version of each table, which require transaction guarantees to update

But, a lot of this metadata still has to live in S3 files which continues to be very wasteful

- For example, every single root file in Iceberg contains all existing snapshots complete with schema information,
- For every single change, a new file is written that contains the complete history
- Lots of hacky solutions are introduced to workaround manipulating many small files in order to read the correct data you're looking for
- Making small changes to data is not simple and requires complex cleanup procedures
- Entire companies exist and are still being started to solve this problem of managing fast-changing data

One of the biggest pain points of Iceberg and Delta Lake is the involved sequence of file IO that is required to run the smallest query

- Following the catalog and file metadata path requires many separate sequential HTTP requests.
- While caching can be used to alleviate some of these problems, this adds additional complexity and is only effective for “hot” data.

## Why Ducklake Fits Better

Using an actual database to manage this metadata makes a lot more sense at small and large volumes of data

- We can still take advantage of the “endless” capacity and “infinite” scalability of blob stores for storing the actual table data in open formats like Parquet
- But now, we can much more efficiently and effectively manage the metadata needed to support changes in a database
- This is exactly what Bigquery and Snowflake do under the hood in their proprietary formats

Ducklake acknowledges 2 simple truths:

- Storing data files in open formats on blob storage is a great idea for scalability and to prevent lock-in
- Managing metadata is a complex and interconnected data management task best left to a database management system.

Ducklake moves all metadata into a SQL Database for both catalog and table data.

- This is defined as a series of relational tables and pure-SQL transactions that describe data operations like schema creation, modification, and the addition, deletion, and updating of data.
- Advanced database concepts like views, nested types, schema evolution are all supported.
- Constraints and referential integrity are once again supported, so no more things like duplicate snapshot IDs
- There are no Avro or JSON files. There is no additional catalog server or additional API to integrate with. It’s all just SQL.

DuckLake data files in the external storage systems are immutable, it never requires modifying files in place or re-using file names.

- This means we can still scale infinitely in storage
- An arbitrary number of compute nodes are querying and updating the catalog database and then independently reading and writing from storage. DuckLake can scale infinitely regarding compute.
- Finally, the catalog database needs to be able to run only the metadata transactions requested by the compute nodes. But this data volume is orders of magnitude lower than the actual data changes
- A PostgreSQL-backed DuckLake will already be able to scale to hundreds of terabytes and thousands of compute nodes.

In order to read from a DuckLake table, a single query is sent to the catalog database, which performs the schema-based, partition-based and statistics-based pruning to essentially retrieve a list of files to be read from blob storage. 

- There are no multiple round trips to storage to retrieve and reconstruct metadata state.
- Fewer moving parts, there arent dozens of S3 reads that need to happen on metadata files that live in blob storage

DuckLake is also able to improve the two biggest performance problems of data lakes: small changes and many concurrent changes.

- For small changes, DuckLake will dramatically reduce the number of small files written to storage. There is no new snapshot file with a tiny change compared to the previous one, there is no new manifest file or manifest list.

In DuckLake, table changes consist of two steps: staging the data files (if any) to storage, and then running a single SQL transaction in the catalog database.

- This greatly reduces the time spent in the critical path of transaction commits, there is only a single transaction to run.
- Essentially, DuckLake supports as many table changes as the catalog database can commit. Even the venerable Postgres can run thousands of transactions per second.
- DuckLake snapshots are just a few rows added to the metadata store, allowing for many snapshots to exist at the same time. There is no need to proactively prune snapshots.


## Setup in DuckDB

``` sql
ATTACH 'ducklake:metadata.ducklake' AS my_ducklake;
USE my_ducklake

CREATE TABLE my_ducklake.demo (i INTEGER);
INSERT INTO my_ducklake.demo VALUES (42), (43);

-- We can see that a single Parquet file has been created that contains the two rows.

FROM my_ducklake.demo;

FROM glob('metadata.ducklake.files/*');

DELETE FROM my_ducklake.demo WHERE i = 43;
FROM my_ducklake.demo;

-- A second file with -delete in the name has appeared, this is also a Parquet file that contains the identifiers of the deleted rows.

FROM ducklake_snapshots('my_ducklake');

FROM my_ducklake.demo AT (VERSION => 2);

FROM ducklake_table_changes('my_ducklake', 'main', 'demo', 2, 3);
```

## Metadata Deepdive

``` sql
INSERT INTO demo VALUES (42), (43);

BEGIN TRANSACTION;
  -- some metadata reads skipped here
  INSERT INTO ducklake_data_file VALUES (0, 1, 2, NULL, NULL, 'data_files/ducklake-8196...13a.parquet', 'parquet', 2, 279, 164, 0, NULL, NULL);
  INSERT INTO ducklake_table_stats VALUES (1, 2, 2, 279);
  INSERT INTO ducklake_table_column_stats VALUES (1, 1, false, NULL, '42', '43');
  INSERT INTO ducklake_file_column_statistics VALUES (0, 1, 1, NULL, 2, 0, 56, '42', '43', NULL)
  INSERT INTO ducklake_snapshot VALUES (2, now(), 1, 2, 1);
  INSERT INTO ducklake_snapshot_changes VALUES (2, 'inserted_into_table:1');
COMMIT;
```

We see a single coherent SQL transaction that:

- Inserts the new Parquet file path
- Updates the global table statistics (now has more rows)
- Updates the global column statistics (now has a different minimum and maximum value)
- Updates the file column statistics (also record min/max among other things)
- Creates a new schema snapshot (#2)
- Logs the changes that happened in the snapshot

Ducklake can be installed via the `ducklake` extension w/ DuckDB.