# Test

`gh-ost -config gh-ost_config.json`


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