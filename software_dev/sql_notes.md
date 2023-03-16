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


## Partitioning
Partitioning in OLTP Databases is a feature used to speed up select queries.  Indexing is commonly used for this purpose as well to avoid full table scans, but typically is used on much more granular columns. 

Partitioning physically splits the data up into queryable chunks.  If your table is commonly queried upon using date filters then partitioning can be a good strategy to boost performance.

In Postgres, you have to add the `partition by range (scrape_date)` attribute onto the table.

You then create physical subtables referencing the parent table, and you pass in the range of values 
- These subtables are commonly broken down by months or years.
- The range `for values from ('2023-01-01') to ('2023-12-31')` is referring to the column `scrape_date` in the table.
- When created the partioned table, the lower end is inclusive and the upper end is exclusive.  That's why the create table partitions go from Jan 1 to Jan 1 while the insert queries use `BETWEEN` and reference Dec 31.
- When people go to query this data, they will still reference the parent table.  Depending on the query, it will decide which partitions it has to go grab data from.

```
-- 2.7 million records
create table nba_source.reddit_test_partitioning
(like nba_source.aws_reddit_comment_data_source)
partition by range (scrape_date);

-- 2.2 million records
create table nba_source.reddit_test_partitioning_2022
partition of nba_source.reddit_test_partitioning
for values from ('2022-01-01') to ('2023-01-01');

-- 0.5 million records
create table nba_source.reddit_test_partitioning_2023
partition of nba_source.reddit_test_partitioning
for values from ('2023-01-01') to ('2024-01-01');

insert into nba_source.reddit_test_partitioning_2022 (
	select * from nba_source.aws_reddit_comment_data_source
	where scrape_date between '2022-01-01' and '2023-12-31');
	
insert into nba_source.reddit_test_partitioning_2023 (
	select * from nba_source.aws_reddit_comment_data_source
	where scrape_date between '2023-01-01' and '2023-12-31');

select * from nba_source.reddit_test_partitioning where scrape_date <= '2023-01-01' limit 100;
```

![image](https://user-images.githubusercontent.com/16946556/225410579-59569e37-011a-4a64-8ef8-726ff629345f.png)
