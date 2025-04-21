--liquibase formatted sql

-- changeset jyablonski9:20250421_test_table_name
CREATE OR REPLACE TABLE test_table_name (
  id INTEGER
);

-- rollback DROP TABLE test_table_name;
