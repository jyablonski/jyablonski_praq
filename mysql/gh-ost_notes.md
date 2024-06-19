# gh-ost

## How to use gh-ost to perform a Partition Migration

Story - I want to add Partitioning to a Large MySQL Table. If you just run `alter table partition by xxx` it will lock the table for literal days. This is why we want to use 0 downtime migrations, which involves creating a new table with the changes we want, backfilling it, and then performing a quick naming swap for the new table we just created to become the "real" table, and we rename the old table to `sales_old` or something.

I've used Gh-ost in the past for other 0 downtime migrations like this, but if the Column you're partitioning by isn't included in the Primary Key Index on the table then you cannot add partitioning to it. Updating a Primary Key Index is not a cheap operation, and gh-ost can't run both migrations at once for you. We want to still use this tool because it copies the data for us over to a new table cleanly, and it reads from the binlog to capture any new data changes.  This is 100x easier than setting up manual triggers to perform this work yourself to ensure 0 data loss.

To "trick" gh-ost in this scenario, you can tell it to just add a new dummy column.  Then, right after we trigger the migration I'm immediately stopping it from running after it starts & creates the new table. From there, we manually add the partitioning to the new table while it has very few rows so the operation completes quick. Afterwards, as we backfill the table the rows will automatically fall into their appropriate partition.

Once the new partitioning scheme is applied, you can un-throttle the migration and set the chunk size to a higher number like 1000 and continue the gh-ost migration as normal. From here, everything proceeds like a normal gh-ost migration.

1. Start gh-ost Migration with a chunk-size of 1
2. After starting the migration and creating the gh-ost table with the `dummy_ghost_column`, immediately run the throttle command to temporarily pause it
3. *OPTIONAL* Run Drop Primary Key, add new Primary Key Statement if needed
4. Run the Alter Table Statement to add partitioning to the gh-ost table
5. Run the Alter Table Statement to drop the `dummy_ghost_column`
6. Run the un-throttle command to begin the gh-ost migration again
7. Run the chunk size command to set the chunk-size to a higher number



``` sh
## gh-ost Commands ##
gh-ost \
--user="ghost_user" \
--password="password" \
--host=localhost \
--database="test" \
--table="users" \
--verbose \
--alter="ADD COLUMN ghost_dummy_col INT NULL" \
--switch-to-rbr \
--allow-on-master \
--cut-over=default \
--exact-rowcount \
--initially-drop-ghost-table \
--panic-flag-file=/tmp/ghost.panic.flag \
--postpone-cut-over-flag-file=ghost.postpone.flag \
--chunk-size=1 \
--execute


## SQL Commands ##

# * OPTIONAL *
# run this if needed
alter table test._users_gho
DROP PRIMARY KEY, add PRIMARY KEY (id, store_id);

ALTER TABLE _users_gho
PARTITION BY LIST (store_id) (
    PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20),
    PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
    PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
    PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
    PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
    PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70),
    PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80),
    PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90),
    PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)
);

## gh-ost commands **

# view the status of the migration
echo status | nc -U /tmp/gh-ost.test.users.sock

# set the chunk size back to 1000
echo "chunk-size=1000" | nc -U /tmp/gh-ost.test.users.sock

# pasuse the migration
echo throttle | nc -U /tmp/gh-ost.test.users.sock

# unpause the migration
echo no-throttle | nc -U /tmp/gh-ost.test.users.sock
```

## Gahbage

The rest of this file is scratch notes 

`gh-ost -config gh-ost_config.json`

Use `faker/main.py` to load data into mysql here for testing if needed


``` sh
gh-ost \
--user="ghost_user" \
--password="password" \
--host=localhost \
--database="test" \
--table="users2" \
--verbose \
--alter='PARTITION BY LIST (store_id) (PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20), PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30), PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40), PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50), PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60), PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70), PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80), PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90), PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100))' \
--switch-to-rbr \
--allow-on-master \
--cut-over=default \
--exact-rowcount \
--initially-drop-ghost-table \
--panic-flag-file=/tmp/ghost.panic.flag \
--postpone-cut-over-flag-file=ghost.postpone.flag \
--execute
```

--alter="PARTITION BY LIST (store_id) (PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20), PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30), PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40), PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50), PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60), PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70), PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80), PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90), PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)" \


``` sql
select count(*) from test.users2;

CREATE TABLE users_partitioned (
    id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(255) NOT NULL,
    color VARCHAR(255) NOT NULL,
    salary INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, store_id),
    INDEX (store_id)
)
PARTITION BY LIST (store_id) (
    PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20),
    PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
    PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
    PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
    PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
    PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70),
    PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80),
    PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90),
    PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)
);

-- Step 2: Copy data from the existing table to the new table
INSERT INTO users2 (name, address, username, email, hire_date, status, color, salary, store_id, created_at)
SELECT name, address, username, email, hire_date, status, color, salary, store_id, created_at
FROM users;

explain analyze
select *
from users
where store_id in (11);

explain  analyze
select *
from users_partitioned
where store_id in (11);

explain
select *
from users
where store_id in (88);

explain
select *
from users_partitioned
where store_id in (88);


select count(*)
from users
where store_id in (11);


select count(*)
from users_partitioned
where store_id in (11);


CREATE TABLE users2 (
    id INT AUTO_INCREMENT,
    name varchar(255) not null,
    address varchar(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hire_date date NOT NULL,
    status varchar(255) not null,
    color varchar(255) NOT NULL,
    salary integer not null,
    store_id integer not null,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, store_id),
    INDEX (store_id)
);

ALTER TABLE users2
PARTITION BY LIST (store_id) (
    PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20),
    PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
    PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
    PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
    PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
    PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70),
    PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80),
    PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90),
    PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)
);

GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'mysql'@'%';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'mysql'@'%';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'mysql'@'%';
GRANT SUPER, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'mysql'@'%';

CREATE USER 'ghost_user'@'%' IDENTIFIED BY 'password';

GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replicator'@'%';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium2'@'%';
GRANT SUPER, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'ghost_user'@'%';
GRANT ALL PRIVILEGES ON test.* TO 'ghost_user'@'%';


alter table users2
PARTITION BY LIST (store_id) (PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20), PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30), PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40), PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50), PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60), PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70), PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80), PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90), PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100))




```


``` sh
gh-ost \
--user="ghost_user" \
--password="password" \
--host=localhost \
--database="test" \
--table="users2" \
--alter="ADD COLUMN ghost_dummy_col INT NULL" \
--cut-over=default \
--exact-rowcount \
--concurrent-rowcount \
--default-retries=120 \
--serve-socket-file=/tmp/gh-ost.sock \
--panic-flag-file=/tmp/gh-ost.panic.flag \
--initially-drop-ghost-table \
--initially-drop-socket-file \
--initially-drop-old-table \
# --switch-to-rbr \
# --allow-on-master \
--execute


gh-ost \
--user="ghost_user" \
--password="password" \
--host=localhost \
--database="test" \
--table="users" \
--verbose \
--alter="ADD COLUMN ghost_dummy_col INT NULL" \
--switch-to-rbr \
--allow-on-master \
--cut-over=default \
--exact-rowcount \
--initially-drop-ghost-table \
--panic-flag-file=/tmp/ghost.panic.flag \
--postpone-cut-over-flag-file=ghost.postpone.flag \
--chunk-size=1 \
--execute
```



``` sql
truncate table test.users_partitioned;

INSERT INTO test.users_partitioned (name, address, username, email, hire_date, status, color, salary, store_id, created_at)
SELECT name, address, username, email, hire_date, status, color, salary, store_id, created_at
FROM test.users;


explain
select *
from users
where store_id in (88);

explain
select *
from users_partitioned
where store_id in (88);

FLUSH PRIVILEGES;

GRANT SUPER, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'root'@'%';
show slave status;
show replica status;
```


```
gh-ost \
--user="ghost_user" \
--password="password" \
--host=localhost \
--database="test" \
--table="users" \
--verbose \
--alter="PARTITION BY LIST (store_id) (
  PARTITION p0 VALUES IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
  PARTITION p1 VALUES IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20),
  PARTITION p2 VALUES IN (21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
  PARTITION p3 VALUES IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
  PARTITION p4 VALUES IN (41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
  PARTITION p5 VALUES IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
  PARTITION p6 VALUES IN (61, 62, 63, 64, 65, 66, 67, 68, 69, 70),
  PARTITION p7 VALUES IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80),
  PARTITION p8 VALUES IN (81, 82, 83, 84, 85, 86, 87, 88, 89, 90),
  PARTITION p9 VALUES IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)
)" \
--switch-to-rbr \
--allow-on-master \
--cut-over=default \
--exact-rowcount \
--initially-drop-ghost-table \
--panic-flag-file=/tmp/ghost.panic.flag \
--postpone-cut-over-flag-file=ghost.postpone.flag \
--chunk-size=1 \
--execute
```