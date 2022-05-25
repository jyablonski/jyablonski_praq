# Traditional OLTP Databases

# SQL Query w/ no Index
No indexes means the SQL DB has to do a `full table scan`.  This is the process of having all data sitting in disk objects called blocks. All columns of the data you request are then read INTO memory, and then each record is traversed in the entire dataset and only the ones you want filtered back to you are returned.
    * This is a costly operation, not only because of having to read the whole dataset but because of the disk -> memory transfer.
    * All queries with non-indexed tables has to do this.

# SQL Query w/ Index
Alongside the data in disk there is a `b-tree` table with only the column you've indexed.  This lookup table tells the DB where each record is, in the exact block and the exact index in the block it's in.
    * This `b-tree` can also be sorted in some specific way.
    * If you index on `first_name`, then that lookup can be sorted and if you want the name `Adam` you'll know that it's around the beginning of the dataset.
    * Looks like it does binary search in this case.  Start at the midpoint, do a > or < operation to see which way to go, and then traverse that half of the dataset.  and repeat.
    * This `b-tree` has to be STORED as well.  So there is some costs / implications there and you likely only want a handful of indexes.  But in general, this metadata is very useful when done correctly.
    * `UPDATING` or `INSERTING` records into these tables means the indexes have to be updated or completely re-calculated.


# Cloud Data Warehouses
### Micro-partitioning
Snowflake uses `micropartitioning` to deliver all of the advantages of static partitioning along with incorporating some index-type features.  

All data in snowflake aables are divided into micro-partitions, which are between 50-500 MB of uncompressed data, and groups of rows are mapped into these partitions in columnar fashion.  Metadata is also stored in each micro-partition, which includes 1) the range of values for each of the columns, 2) the number of distinct values, and 3) additional query optimization attributes.

This micro-partitioning is performed automatically and doesn't have to be maintained by users (but it can be).

The use case is if you want to query dates.  1 year of data from Jan - Dec 2021 and you only want to query January stuff, you would only have to search through 1/12 of the dataset.

Snowflake data is always stored compressed.

### Data Clustering
Data is normally stored or sorted along natural dimensions like time, or geographic regions (california etc).  Snowflake automatically collects clustering metadata as data is inserted or loaded into tables, then leverages that during querying to improve the performance.