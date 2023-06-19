# Trino
Trino is an open source distributed ANSI SQL Compliant query engine designed to query large datasets and datalakes.  Commonly used to query columnar oriented data formats like ORC or Parquet, as well as capabilities to query formats such as Hive and Apache Iceberg.

Forked off of Presto in 2019, and rebranded as Trino in December 2020.  Facebook "open sourced" Presto but still wanted it fully under their control, thus the reason for the Trino fork.

![image](https://github.com/jyablonski/python_aws/assets/16946556/56026562-99e6-49f7-ba47-312d1cc393b1)


## Internal Components
1. The Coordinator
   1. Responsible for parsing, analyzing, planning, optimizing, and scheduling a query submitted by a client.
   2. Interacts with the service provider interface to obtain available tables, statistics, and other information needed to carry out its tasks.


2. Worker Nodes
   1. Responsible for executing the tasks fed to them by the scheduler.  
   2. These tasks process rows from data sources which produce results that are returned back to the coordinator and ultimately back to the client.

## Presto
Presto was built by Facebook in 2012.

Used my multiple companies such as Netflix, Amazon (AWS Athena is built off of Presto).