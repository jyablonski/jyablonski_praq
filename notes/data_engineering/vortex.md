# Vortex

Vortex is a new open source file format designed to be a superior and more performant alternative to Parquet. It's an OSS-forever project under the Apache 2.0 License and now belongs to the Linux Foundation so it's not going anywhere.

Its goals are:

- Extensible & future-proof (support GPU compute & other hardware shifts that will happen in the future)
- Faster performance than Parquet
  - Faster random access reads
  - Faster scans
  - Faster writes
  - Comparable size
- Interopability w/ other OSS data formats like Arrow
- Optimized for object storage
- Design for SIMT / SIMD / Random Access

Traditionally, each query engine like DuckDB, Polars, Spark etc implemented their own Parquet reader to read Parquet files. Vortex on the other hand builds a hyper-optimized Scan operator that can be used by any query engine. This means that Vortex can be optimized independently of the query engines, and all query engines can benefit from the same optimizations.

## Performance Optimizations

Pushdown

1. Filter Pushdown (prune rows)
2. Projection Pushdown (prune columns)
3. Expression Pushdown (Functions on columns, e.g. `age + 5`)
4. Selection Pushdown (Functions on columns w/ a row mask, e.g. `age + 5` only for rows where `state = 'CA'`)

As well as GPU SIMT & CPU SIMD

## Concepts

### Compression

Data is encoded/compressed to reduce file size. Different algorithms for different data types and patterns.

```text
Original: ["CA", "NY", "CA", "TX", "NY", "CA", "TX"]
Dictionary: {0: "CA", 1: "NY", 2: "TX"}
Encoded: [0, 1, 0, 2, 1, 0, 2]
```

General compression:

- Snappy: Fast, moderate compression
- GZIP: Slower, better compression
- ZSTD: Good balance, modern choice
- LZ4: Very fast, light compression

### Zone Maps

Zone Maps are min/max statistics stored for each column in a row group.

```
Column: age
Row Group 1: min=18, max=35
Row Group 2: min=40, max=67
Row Group 3: min=22, max=58
```

Why they matter:

- Query pruning - Skip entire chunks without reading them
- If you query `WHERE age > 70`, the file format can skip all three row groups above without even decompressing them
- Huge performance win for selective queries

### Row Groups

Row groups are horizontal partitions of data within a file. Each row group contains a chunk of rows stored together (typically 100MB - 1GB uncompressed)

```

File
├── Row Group 1 (rows 0-999,999)
│ ├── Column A
│ ├── Column B
│ └── Column C
├── Row Group 2 (rows 1,000,000-1,999,999)
│ ├── Column A
│ ├── Column B
│ └── Column C
└── Row Group 3 (rows 2,000,000-2,999,999)
├── Column A
├── Column B
└── Column C

```

Why they matter:

- Parallelism - Different row groups can be processed by different threads/workers
- Predicate pushdown - Use zone maps to skip entire row groups
- Memory management - Read one row group at a time instead of entire file
- Write buffering - Buffer data in memory until you have enough for a row group

Trade-offs:

- Larger row groups = better compression, less metadata overhead
- Smaller row groups = better pruning, more parallelism, less memory

### Pages

What they are:

- The smallest unit of data within a column
- Each column in a row group is divided into pages (typically 1MB uncompressed)
- The actual unit of compression and I/O

Structure:

```
Row Group 1
└── Column A
    ├── Page 1 (rows 0-99,999)
    ├── Page 2 (rows 100,000-199,999)
    └── Page 3 (rows 200,000-299,999)
```

## Example

```sql
SELECT
    name,
    age
FROM users
WHERE
    age > 50
    AND state = 'CA'
```

Step-by-step execution:

1. Check file metadata - See which row groups might have age > 50
2. Row group pruning - Zone maps show Row Group 1 has max age = 35, skip it!
3. Read relevant row groups - Load Row Groups 2 and 3
4. Page-level pruning - Within those row groups, check page-level zone maps for age column
5. Decompress pages - Only decompress pages that might contain age > 50
6. Dictionary lookup - For state column, check if 'CA' is even in the dictionary
7. Scan and filter - Apply the actual predicates to the decompressed data
8. Project columns - Only read name and age columns, skip all others

---

users.parquet (1GB file, 10M rows)

Row Group 1: 5M rows, 500MB uncompressed
├── Column: user_id (INT64)
│ ├── Zone map: min=1, max=5000000
│ ├── Encoding: PLAIN + GZIP
│ └── Pages: 50 pages × 100K rows each
│
├── Column: state (STRING)
│ ├── Zone map: values=["AL", "AK", ..., "WY"]
│ ├── Encoding: DICTIONARY + RLE
│ ├── Dictionary: {0: "AL", 1: "AK", ...}
│ └── Pages: 10 pages (fewer due to compression)
│
└── Column: age (INT32)
├── Zone map: min=18, max=89
├── Encoding: BIT_PACKED + SNAPPY
└── Pages: 50 pages × 100K rows each

Row Group 2: 5M rows, 500MB uncompressed
└── ... (same structure)

## Why Not Parquet?

Parquet has known limitations, including:

- Not easily extensible (adding `VARIANT` was a herculean effort)
- Metadata is slow
- Compression is CPU-hungry and slow
- Was designed in 2013, and while it's popular it has started to show its age

Apache Iceberg and Delta Lake are two table formats that build on top of Parquet, but they can't fix the underlying limitations with Parquet itself.

- Parquet is how the bytes are stored on disk. The Lakehouse formats just manage the metadata and transactions on top of Parquet files.

T1 Organizations have continued building specialized Parquet alternatives this entire time, including:

- Capacitor (Google)
- Snowflake (micropartitions)
- Nimble (Meta)
- Amduai (Microsoft)
- DuckDB
- Clickhouse

So it's well known that Parquet isn't perfect, so why not build a better alternative?

```

```

```

```

```

```
