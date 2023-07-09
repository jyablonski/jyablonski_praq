# Traditional OLTP Databases
[Neat Cheatsheet of PostgreSQL commands](https://gist.github.com/rgreenjr/3637525)

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


# Audit Triggers
![image](https://user-images.githubusercontent.com/16946556/233234508-75fff4d9-0158-4320-b233-7fb26d9a021d.png)

`select * from information_schema.triggers;`

```
CREATE TABLE IF NOT EXISTS public.orders (
	id serial primary key,
	item varchar not null,
	price double precision not null, 
);

drop table public.orders;
CREATE TABLE IF NOT EXISTS public.orders (
	id serial primary key,
	item varchar not null,
	price double precision not null, 
	created timestamp default current_timestamp
);

drop table public.orders_audit;
CREATE TABLE IF NOT EXISTS public.orders_audit (
	id serial primary key,
	order_id integer not null,
	item varchar not null,
	price double precision not null, 
	created timestamp default current_timestamp,
	audit_type varchar not null,
	created_audit timestamp default current_timestamp
);

CREATE OR REPLACE FUNCTION orders_audit_trigger_function()
RETURNS trigger AS $body$
BEGIN
   if (TG_OP = 'INSERT') then
       INSERT INTO orders_audit (
		   order_id,
           item,
           price,
           created,
           audit_type,
           created_audit
       )
       VALUES(
		   NEW.id,
           NEW.item,
           NEW.price,
           NEW.created,
           'INSERT',
           CURRENT_TIMESTAMP
       );
             
       RETURN NEW;
   elsif (TG_OP = 'UPDATE') then
       INSERT INTO orders_audit (
		   order_id,
           item,
           price,
           created,
           audit_type,
           created_audit
       )
       VALUES(
		   OLD.id,
           NEW.item,
           NEW.price,
           OLD.created,
           'UPDATE',
           CURRENT_TIMESTAMP
       );
             
       RETURN NEW;
   elsif (TG_OP = 'DELETE') then
       INSERT INTO orders_audit (
		   order_id,
           item,
           price,
           created,
           audit_type,
           created_audit
       )
       VALUES(
		   OLD.id,
           OLD.item,
           OLD.price,
		   OLD.created,
           'DELETE',
           CURRENT_TIMESTAMP
       );
        
       RETURN OLD;
   end if;
     
END;
$body$
LANGUAGE plpgsql;


drop trigger if exists orders_audit_trigger on public.orders;
create orders_audit_trigger
after insert or update or delete on public.orders
for each row execute function orders_audit_trigger_function();

INSERT INTO public.orders(
	item, price)
	VALUES ('Nvidia RTX 4090', 1999.99);

INSERT INTO public.orders(
	item, price)
	VALUES ('AMD 6900 XT', 999.99);
	
update public.orders set price = 1995.99 where item = 'Nvidia RTX 4090';

delete from public.orders where id = 3;
```

# One to Many & Many to Many relationships
[Stackoverflow]

![image](https://github.com/jyablonski/python_aws/assets/16946556/affac983-849d-4e09-8fc9-127e3088fb71)
