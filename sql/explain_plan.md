# SQL EXPLAIN
Databases use Query Optimizer Engines to devise a plan for each query it receives.

No where clause - then you must query all records in the table.

## Postgres
`explain select * from table1;`

Structure of a query plan consists of plan nodes.  Nodes at the bottom of the tree are scan nodes; they return raw records from the table.  
- Multiple scan nodes: sequential scans, index scans, and bitmap index scans.
- Joining, aggregating, sorting will have additional scan nodes to perform these operations.

`EXPLAIN` returns 1 line for each node in the plan tree.
- The first line has the total estimated execution cost for the plan.
- `Merge Left Join  (cost=1925.56..2262.63 rows=16889 width=302)`
  - Estimated Start up Cost, this is the time expended before the output phase can begin.
  - Extimated Total Cost (node might get stopped short here bc of something like `LIMIT 25;` at the end of a query).
  - Estimated number of rows output by this plan node.
  - Estimated average width of rows output by this plan node (in bytes).
  - `The costs are measured in arbitrary units determined by the planner's cost parameters `
  - Number of rows can be deceiving bc we are often filtering queries down using the `WHERE` clause.

### Cost Calculation
- `SELECT relpages, reltuples FROM pg_class WHERE relname = 'tenk1';`
- `you will find that tenk1 has 358 disk pages and 10000 rows. The estimated cost is computed as (disk pages read * seq_page_cost) + (rows scanned * cpu_tuple_cost). By default, seq_page_cost is 1.0 and cpu_tuple_cost is 0.01, so the estimated cost is (358 * 1.0) + (10000 * 0.01) = 458.`

### Adding a Where Clause
- `EXPLAIN SELECT * FROM tenk1 WHERE unique1 < 7000;`
```
 Seq Scan on tenk1  (cost=0.00..483.00 rows=7001 width=244)
   Filter: (unique1 < 7000)
```
- When applying a `WHERE` clause, a Filter row will now appear in the plan.  This plan node checks the condition for each row it scans, and only outputs the ones that pass the condition.
- The estimate number of rows decreased to 7001 because of the `WHERE` clause.  The scan still has to visit all 10,000 rows, so the cost hasn't decreased. It actually went up a bit because the CPU now has extra operations to calculate to check that `WHERE` condition.
  - This estimate is random bc it takes from a randomized sample of the table, so it will vary everytime you run `EXPLAIN`.

### Adding a Restrictive Where Clause
- `EXPLAIN SELECT * FROM tenk1 WHERE unique1 < 100;`

```
 Bitmap Heap Scan on tenk1  (cost=5.07..229.20 rows=101 width=244)
   Recheck Cond: (unique1 < 100)
   ->  Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0)
         Index Cond: (unique1 < 100)
```
- 2 Step plan: child plan node visits an index to find locatino of rows matching the index condition, and then the upper plan node fetches those rows from the table.  Fetching the rows separately here is more expensive than reading them sequentially, but bc we're not visiting all the pages of the table, it's cheaper than a sequential scan.

- `EXPLAIN SELECT * FROM tenk1 WHERE unique1 < 100 AND stringu1 = 'xxx';`
```
 Bitmap Heap Scan on tenk1  (cost=5.04..229.43 rows=1 width=244)
   Recheck Cond: (unique1 < 100)
   Filter: (stringu1 = 'xxx'::name)
   ->  Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0)
         Index Cond: (unique1 < 100)
```
- The added condition `stringu1 = 'xxx'` reduces the output row estimate, but not the cost bc we still have to visit all the same rows.  The index is only on the `unique1` column.  So it filters the results returned after grabbing them via the index.

- `EXPLAIN SELECT * FROM tenk1 WHERE unique1 = 42;`
```
 Index Scan using tenk1_unique1 on tenk1  (cost=0.29..8.30 rows=1 width=244)
   Index Cond: (unique1 = 42)
```
- These are very simple query plans when you're just selecting 1 row.  

- `EXPLAIN SELECT * FROM tenk1 ORDER BY unique1;`
```
 Sort  (cost=1109.39..1134.39 rows=10000 width=244)
   Sort Key: unique1
   ->  Seq Scan on tenk1  (cost=0.00..445.00 rows=10000 width=244)
```
- When you start using `ORDER BY`, sort steps come up.  

- `EXPLAIN SELECT * FROM tenk1 ORDER BY four, ten LIMIT 100;`
```
 Limit  (cost=521.06..538.05 rows=100 width=244)
   ->  Incremental Sort  (cost=521.06..2220.95 rows=10000 width=244)
         Sort Key: four, ten
         Presorted Key: four
         ->  Index Scan using index_tenk1_on_four on tenk1  (cost=0.29..1510.08 rows=10000 width=244)
```
- Incremental sorts return tuples before the entire result set has been returned, which helps for optimizations with `LIMIT` queries.

### Join Plans
```
EXPLAIN SELECT *
FROM tenk1 t1, tenk2 t2
WHERE t1.unique1 < 10 AND t1.unique2 = t2.unique2;
```

```
 Nested Loop  (cost=4.65..118.62 rows=10 width=488)
   ->  Bitmap Heap Scan on tenk1 t1  (cost=4.36..39.47 rows=10 width=244)
         Recheck Cond: (unique1 < 10)
         ->  Bitmap Index Scan on tenk1_unique1  (cost=0.00..4.36 rows=10 width=0)
               Index Cond: (unique1 < 10)
   ->  Index Scan using tenk2_unique2 on tenk2 t2  (cost=0.29..7.91 rows=1 width=244)
         Index Cond: (unique2 = t1.unique2)

```



## Explain Analyze
`EXPLAIN ANALYZE SELECT * FROM TABLE;`

This is used to actually execute the query and return exact costs + row counts from the query, and it compares them to the estimate.