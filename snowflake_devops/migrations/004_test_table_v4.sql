-- liquibase formatted sql

-- changeset jyablonski:004
CREATE OR REPLACE TABLE test_table_v4 (
  custKey NUMBER DEFAULT NULL,
  orderDate DATE DEFAULT NULL,
  orderStatus VARCHAR(100) DEFAULT NULL,
  price VARCHAR(255)
);

-- rollback DROP TABLE test_table_v4;