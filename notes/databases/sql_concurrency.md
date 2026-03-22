# Postgres Concurrency, Connections, and Index Maintenance

## How Postgres Handles Concurrent Requests

### Process-Per-Connection Model

Postgres uses a process-based architecture, not a thread-based one. When a client connects, the main `postmaster` process forks a new backend process dedicated to that connection. Each backend process has its own memory space and communicates with shared resources through shared memory and semaphores.

When 100 requests come in simultaneously:

- Each connection gets its own OS-level process
- Each process gets its own allocation of `work_mem` (default 4MB, used per sort/hash operation, and a single query can allocate multiple units of it)
- Each process maintains its own local buffer cache on top of the global `shared_buffers` pool
- The OS scheduler is responsible for time-slicing across all these processes

This means 100 concurrent connections translates to 100 backend processes competing for CPU, memory, I/O, and shared buffer access. The overhead per connection is roughly 5-10MB of resident memory at baseline, scaling up depending on query complexity.

### Connection Limits and Resource Pressure

The `max_connections` setting (default 100) caps how many simultaneous backends can exist. Each one costs:

- RSS memory for the process (baseline ~5-10MB, more under load)
- A slot in the `PGPROC` array in shared memory
- File descriptors for the socket and any open relations
- Participation in the lock table and snapshot management

At high connection counts (say 500+), the overhead isn't just memory. Lock contention, snapshot management, and `ProcArray` scans during visibility checks all degrade. This is why connection poolers like PgBouncer or pgcat exist -- they multiplex many application connections onto a smaller number of actual Postgres backends. A common pattern is 500+ application connections mapped to 20-50 actual database connections.

### MVCC: How Concurrent Reads and Writes Coexist

Postgres uses Multi-Version Concurrency Control. Rather than locking rows during reads, each transaction sees a snapshot of the database as of its start time. Writers create new row versions rather than overwriting in place.

When a row is updated:

1. The old tuple stays in the heap with its `xmax` set to the updating transaction's ID
1. A new tuple is written (possibly on the same page, possibly on a different one) with its `xmin` set to that same transaction ID
1. Readers whose snapshots predate the update still see the old tuple
1. Readers whose snapshots postdate the commit see the new tuple

This means readers never block writers and writers never block readers. The trade-off is dead tuple accumulation -- old row versions linger until `VACUUM` reclaims them.

Writer-writer conflicts do still block. If two transactions try to update the same row, the second one waits on the first's lock. Under `SERIALIZABLE` isolation, Postgres uses predicate locking to detect serialization anomalies and will abort one of the conflicting transactions.

### Lock Hierarchy

Postgres has a layered lock system:

- Table-level locks: range from `AccessShareLock` (acquired by `SELECT`) to `AccessExclusiveLock` (acquired by `DROP TABLE`, `ALTER TABLE`). Most DML operations take `RowExclusiveLock` on the table, which is compatible with other `RowExclusiveLock` holders, so concurrent inserts/updates/deletes on different rows don't block each other at the table level.
- Row-level locks: implemented via the `xmax` field on tuples rather than an in-memory lock table. `SELECT FOR UPDATE` sets `xmax` to mark the row as locked. This scales well because it doesn't consume entries in `pg_locks`.
- Advisory locks: application-defined locks that Postgres manages but doesn't enforce semantically.

## Index Maintenance on CRUD Operations

### What Happens on INSERT

Every index on the table must be updated. For a table with 5 indexes, an insert does:

1. Write the new heap tuple
1. For each index, derive the key value(s) from the new tuple and insert an entry pointing back to the heap tuple's `(page, offset)` location

For a B-tree index, this means traversing from root to leaf, finding the correct position, and inserting the key. If the leaf page is full, it splits. Each index insertion is a separate I/O path.

For a GIN index (like a full-text search tsvector index), inserts are more expensive because a single document can produce many lexemes. GIN mitigates this with a "pending list" -- new entries go into an unsorted pending area and get batch-merged into the main index structure later (either by `VACUUM`, `autoVACUUM`, or when the pending list exceeds `gin_pending_list_limit`). This makes inserts faster at the cost of slightly slower reads until the pending entries are merged.

### What Happens on UPDATE

Postgres treats an update as a delete-then-insert at the storage level (new tuple version). This means:

1. The old heap tuple gets its `xmax` set
1. A new heap tuple is written
1. Every index potentially needs a new entry pointing to the new tuple

HOT (Heap-Only Tuples) optimization avoids index updates when:

- The update doesn't change any indexed column
- The new tuple fits on the same heap page as the old one

If both conditions hold, Postgres creates the new tuple on the same page and chains it from the old one via a redirect. No index entries change. This is a significant optimization for workloads that frequently update non-indexed columns. You can monitor HOT effectiveness via `pg_stat_user_tables.n_tup_hot_upd`.

When HOT doesn't apply, every index gets a new entry. The old index entries become dead pointers that `VACUUM` eventually removes.

### What Happens on DELETE

The heap tuple's `xmax` is set, marking it as dead to future transactions. Index entries are not removed immediately -- they become dead pointers. `VACUUM` is responsible for:

1. Scanning the heap for dead tuples
1. Removing the corresponding index entries from every index
1. Marking the heap space as reusable

Until vacuum runs, dead index entries still get traversed during index scans (the executor checks heap visibility and skips them), which is why index bloat matters for read performance.

### What Happens on SELECT

No index maintenance. The index is read-only from the query's perspective. For a B-tree, it's a traversal from root to leaf. For a GIN index, it's a lookup in the inverted posting lists, plus a scan of the pending list if it's non-empty.

The one nuance is visibility checks. Postgres's indexes don't store visibility information (with the exception of the visibility map optimization for index-only scans). So after finding a candidate tuple via the index, the executor must check the heap tuple's `xmin`/`xmax` to confirm it's visible to the current snapshot. Index-only scans can skip this heap fetch for pages that the visibility map confirms are all-visible.

### Cost Summary Per Index Per Operation

| Operation | B-tree cost | GIN cost | Heap cost |
| ---------------- | ------------------------------------------------------ | -------------------------------------------------------- | ------------------------ |
| INSERT | 1 key insertion (tree traversal + possible page split) | N key insertions to pending list (N = number of lexemes) | 1 tuple write |
| UPDATE (HOT) | 0 (no index touch) | 0 | 1 tuple write, same page |
| UPDATE (non-HOT) | 1 old entry becomes dead, 1 new entry inserted | N old entries become dead, N new entries | 1 new tuple write |
| DELETE | entries become dead (cleaned by vacuum) | entries become dead (cleaned by vacuum) | xmax set |
| SELECT | traversal only | posting list lookup + pending list scan | visibility check |

## CREATE INDEX CONCURRENTLY

### How It Works

A normal `CREATE INDEX` takes a `ShareLock` on the table, blocking all writes for the duration of the build. CIC avoids this by:

1. Taking a `ShareUpdateExclusiveLock` (doesn't block reads or writes, does block DDL and other CIC on the same table)
1. First pass: scan the entire table and build the index, while concurrent writes also insert into the index
1. Wait for all transactions that started before pass 1 to complete
1. Second pass: scan again to pick up anything that was in-flight during pass 1
1. Wait for all transactions that started before pass 2 to complete
1. Mark the index as valid

### Failure Modes

- If anything goes wrong during either pass, the index is left in `pg_index` with `indisvalid = false`
- The planner will not use an invalid index, but it still incurs write overhead (inserts still maintain it)
- You must manually drop and retry

### Checking for Invalid Indexes

```sql
select c.relname as index_name, i.indisvalid
from pg_index i
join pg_class c on c.oid = i.indexrelid
where not i.indisvalid;
```

### Cleanup After a Failed CIC

```sql
-- make sure no CIC is still running
select pid, query, state
from pg_stat_activity
where query ilike '%create index concurrently%';

-- drop the invalid index (also concurrent to avoid blocking)
drop index concurrently if exists your_index_name;

-- retry the build
create index concurrently your_index_name on your_table (column);
```

### Things That Block CIC

Long-running transactions are the main culprit. CIC has to wait for all existing transactions to finish at two synchronization points. An idle-in-transaction session, a long `pg_dump`, or a forgotten open `BEGIN` will stall the entire build. Check `pg_stat_activity` for `idle in transaction` sessions before starting a CIC.

### What Doesn't Have a Concurrent Equivalent

`ALTER TABLE ... ALTER COLUMN TYPE` has no concurrent mode. If it requires a table rewrite (e.g. `int` to `bigint`), it holds `AccessExclusiveLock` for the entire rewrite. The workaround is a multi-step migration: add new column, backfill in batches, add a sync trigger, swap column names in a quick transaction, drop the old column.

## GIN Indexes for Full-Text Search

### tsvector vs pgvector

These are unrelated despite the naming overlap:

- `tsvector` + GIN = built-in full-text search. Exact keyword matching on stemmed/normalized lexemes. "Does this document contain these words?"
- pgvector (IVFFlat, HNSW indexes) = similarity search over high-dimensional float arrays. "What's closest to this embedding in vector space?"

They solve complementary problems. tsvector won't match synonyms it hasn't been configured for. pgvector embeddings will, because semantically similar words are close in the embedding space.
