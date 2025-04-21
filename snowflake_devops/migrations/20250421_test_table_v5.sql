-- liquibase formatted sql

-- changeset jyablonski:20250421_test_table_v5
CREATE OR REPLACE TABLE test_table_v5 (
  custKey NUMBER DEFAULT NULL,
  orderDate DATE DEFAULT NULL,
  orderStatus VARCHAR(100) DEFAULT NULL,
  price VARCHAR(255)
);

-- rollback DROP TABLE test_table_v5;