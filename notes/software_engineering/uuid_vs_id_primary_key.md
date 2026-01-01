# UUIDs vs IDs for Primary Keys

A UUID (Universally Unique Identifier) is a 128-bit value typically represented as a 32-character hexadecimal string (like `550e8400-e29b-41d4-a716-446655440000`). It's generated in a way that ensures global uniqueness. This means that no two UUIDs will ever collide, regardless of where or when they are created.

- UUIDs take up 16 bytes (128 bits) of storage,
- Because they're randomly generated, this causes insertions to happen all over the place in the index which requires more work to be done to maintain an index structure in a database
- Can potentially result in slower query performance, especially on large tables w/ many indexes
- UUIDs are advantageous in distributed databases or when data is sharded across multiple servers. Since UUIDs are unique across all instances, they eliminate the need for coordination between servers or round trips to the database to generate unique keys.

Auto-incrementing integers are sequential numeric values (like 1, 2, 3, 4, ...) typically used as primary keys in a Database. Each new row in a table receives the next integer value in the sequence.

- Integer IDs typically take up 4 bytes (32 bits).
- Inserting them into the index is usually more efficient because the database can predict the order of insertion.
- Typically faster for queries that rely on primary keys
- Risk in distributed systems because different servers might try to insert records with the same auto-increment value, leading to conflicts unless you use a distributed locking mechanism.

Use auto-incrementing integers as primary keys for internal database structures that need to be fast and efficient. Use UUIDs for certain tables where data is distributed or needs to be globally unique (e.g., for user identifiers in a system that integrates across multiple services). While UUIDs are useful in specific cases, avoid using them as primary keys in systems that don't need their features (e.g., if you're building a small, single-instance application, UUIDs could introduce unnecessary complexity).

## Use Cases

UUID

- A system where users can create accounts and data is stored across multiple servers or locations, and you need to guarantee that the IDs are unique even without coordination between these servers (e.g., in a global e-commerce platform with microservices).
- A mobile application that stores user-generated data locally (in the device's database) and later syncs with a central database. UUIDs ensure the data created on the device doesn’t conflict with data created on the server.

Autoincrementing IDs

- A traditional monolithic application with a single database where performance is more critical and the application does not require distributed systems.
- A small business inventory management system where data is localized and you want minimal storage overhead.

## UUID v7: Quick Reference

### What Is It?

Time-ordered UUIDs (RFC 9562, 2024) that combine auto-increment benefits with UUID flexibility.

Structure:

```
018e8c5a-5e3f-7000-8000-000000000000
└──timestamp──┘ └─ random/counter ──┘
```

### Why Use UUID v7?

Solves UUID v4 problems:

- ✅ Sequential insertion (no B-tree fragmentation)
- ✅ Better INSERT performance
- ✅ Sortable by creation time

Keeps UUID benefits:

- ✅ Generate anywhere without coordination
- ✅ No collision risk in distributed systems
- ✅ Client-side generation
- ✅ Merge/shard friendly

Tradeoffs:

- ❌ 4x storage vs INT (16 bytes vs 4)
- ❌ Index size multiplies across all FKs and indexes
- ❌ Needs extension or app-level generation

### Implementation (Postgres)

```sql
-- With extension
CREATE EXTENSION pg_uuidv7;

CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    title TEXT
);
```

Or generate in application code (Python: `uuid-utils`, Node: `uuid` library v9+)

### Migration Strategy

Best practice: Don't migrate existing tables

- ✅ New tables: UUID v7 from day one
- ✅ Existing tables: Leave as auto-increment
- ✅ Mixed state: Totally fine and common

Only migrate if:

- Actually hitting ID exhaustion
- Need to shard/merge that specific table
- Already doing major refactor

### Decision Framework

Use UUID v7 for:

- Distributed systems / microservices
- New projects expecting to scale
- Client-side entity creation needs

Use auto-increment for:

- Single monolith, single database
- Performance absolutely critical
- Existing tables (migration rarely worth it)

______________________________________________________________________

Bottom line: Storage is cheap, complexity is expensive. UUID v7 is the modern default for new work. Don't stress about migrating legacy tables.
