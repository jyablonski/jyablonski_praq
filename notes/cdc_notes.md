# Change Data Capture (CDC)
Change Data Capture is a practice that involves using a transaction log to read changes in a database in the form of inserts / updates / deletes and send these changes to another database.
    * The purpose is because if we have an OLTP database where events are being stored to, we don't want to also be doing OLAP type actions on that database to bog it down.
    * You keep your OLTP database and send the new data changes to a secondary OLAP database, typically a data warehouse.
    * You're able to continuously send over these new records and not have to wait for daily batch updates once a day.  Downstream analytics can derive insights faster.
    * Typically the WAL (Write Ahead Log) is used; this is a transaction log that tracks all inserts/updates/deletes made on a database and it is a feature that has to be enabled by a system admin.
  
# How to Implement it

## Airbyte

### Method 1
Airbyte - using Logical Replication.  [Video](https://www.youtube.com/watch?v=NMODvLgZvuE&ab_channel=Airbyte)
    * You turn on the WAL and create a `pg_create_logical_replication('slot1', 'pgoutput');` as well as a `CREATE PUBLICATION pub1 FOR ALL TABLES;` which is used connect with in Airbyte UI
    * Can run this sync every 30 mins, every 5 mins etc.
    * This saves the metadata in the changed rows and sends them to your destination.

### Method 2
Can also use Airbyte to store changed rows to Snowflake.  [Article](https://airbyte.com/tutorials/postgresql-database-to-snowflake)\
    * This saves the changed records into temporary files in an S3 bucket which Snowflake subscribes to and uses Snowpipe to load in those files as they appear in the bucket with their `COPY INTO` commands.


## Debezium & Kafka
CDC Configuration with Debezium + Kafka involves using Debezium to subscribe to the Posgres WAL so it can be constantly reading changed records, and then it publishes those changes to a Kafka Topic.  You then have some kind of subscriber to that specific Kafka Topic which reads in those changes as they happen and ingests them into whatever system the subscriber is on.
    * Messages are buffered so either you can send loads of them every 5 / 30 mins or whatever, or trigger a batch upload after every 100 messages or something.
    * Snowflake can connect to a Kafka topic as an internal stage and then pipe the results into a Snowflake table.  [Article](https://docs.snowflake.com/en/user-guide/kafka-connector-overview.html)
      * This solution uses a virtual warehouse so compute resources are used for this step ($$$).
    * Messages are deleted once they have been uploaded into a Snowflake Table.