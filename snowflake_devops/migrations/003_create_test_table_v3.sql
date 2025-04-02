-- changeset jyablonski:003
CREATE OR REPLACE TABLE test_table_v3 (
  custKey NUMBER DEFAULT NULL,
  orderDate DATE DEFAULT NULL,
  orderStatus VARCHAR(100) DEFAULT NULL,
  price VARCHAR(255)
);

-- rollback DROP TABLE test_table_v3;