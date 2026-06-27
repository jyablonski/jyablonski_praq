# Apache Spark

## What it is

Apache Spark is an open-source, in-memory distributed compute engine for large-scale data processing. It's a unified analytics engine: batch SQL/DataFrame, streaming, ML, and graph workloads all run on the same execution substrate. The core abstraction is the RDD (Resilient Distributed Dataset) — an immutable, partitioned, lineage-tracked collection — but most code today is written against the higher-level DataFrame/Dataset/SQL APIs, which sit on top of a Catalyst-optimized planner and the Tungsten execution engine. Spark runs on the JVM (Scala-native, with PySpark, SparkR, and now Go/Swift/Rust clients via Spark Connect).

## What it's used for

- Batch ETL/ELT at scale — Parquet/Delta/Iceberg/Hudi transformations, the bread-and-butter case
- SQL warehousing-style analytics — interactive query via Thrift Server, Spark SQL, or Databricks SQL
- Streaming — Structured Streaming for near-real-time and (now) real-time sub-second pipelines
- ML feature engineering and training — MLlib for classic ML, and as the preprocessing layer for distributed DL
- Lakehouse compute — the workhorse engine behind Delta Lake, Apache Iceberg, and Hudi tables
- Ad-hoc data exploration at TB+ scale where single-node tools (pandas/Polars/DuckDB) fall over

Spark's sweet spot is the 100 GB – multi-TB range with complex joins and aggregations. Below ~10 GB, DuckDB/Polars usually crushes it on a single node; above it, Spark's shuffle-based parallelism pays off.

______________________________________________________________________

## Hosting: Databricks vs. self-hosted on EKS

### Databricks

Managed, opinionated Spark distribution. You pay a per-DBU premium on top of cloud compute in exchange for:

- Photon — Databricks' vectorized C++ execution engine that transparently accelerates SQL/DataFrame ops (2–5× typical, more on string-heavy queries). Closed-source; only available on Databricks.
- Delta Lake deep integration — Liquid Clustering, predictive optimization, deletion vectors, Z-ordering.
- Unity Catalog — governance, lineage, RBAC, audit. The main reason orgs lock in.
- Job scheduling, notebooks, SQL warehouses, MLflow, Delta Live Tables / Lakeflow Declarative Pipelines — the surrounding platform.
- Cluster autoscaling and pool management — much less plumbing than DIY.

Trade-offs: vendor lock-in (Photon, Unity Catalog, DLT syntax), DBU pricing, less control over JVM tuning, and you can't easily run alongside arbitrary K8s workloads.

### Self-hosted on EKS

You run vanilla Apache Spark on your own EKS cluster. Two flavors:

1. `spark-submit` in cluster mode against the K8s API — Spark's native K8s scheduler creates driver and executor pods directly. Simple, imperative, no extra controller.
1. Apache Spark Kubernetes Operator — launched as an official Apache Spark subproject in May 2025, this is now the recommended path. It uses CRDs (`SparkApplication`, `SparkCluster`, `ScheduledSparkApplication`) to manage lifecycle declaratively. Prior to this, the Kubeflow/GCP Spark Operator was the de facto standard and is still widely used. There's also the option of EMR on EKS if you want AWS's optimized runtime, but that's a third hosting model — not pure self-host.

What you own with self-hosted EKS:

- Container images (build your own, including Hadoop AWS SDK, Iceberg/Delta JARs, Python deps)
- IRSA mappings for S3 access per service account
- Karpenter or Cluster Autoscaler for node provisioning
- Pod templates, affinity/anti-affinity, taints, PriorityClasses
- Shuffle reliability (more below — the painful part)
- Spark History Server, Prometheus/Grafana, log aggregation
- Catalog (external Hive metastore, Glue, or Iceberg REST catalog)

Trade-offs: significantly more operational burden, but zero per-DBU premium, full control, multi-tenancy with other K8s workloads, and no engine lock-in.

### Rough decision frame

| Factor | Databricks | EKS self-host |
| -------------------------------- | ---------------------------------------------- | ---------------------------------------------------- |
| Time-to-production | Days | Weeks-to-months |
| Per-job compute cost | Higher (DBU markup) | Lower (just EC2) |
| Governance/lineage | Unity Catalog out of box | Build it (OpenMetadata, DataHub) |
| Engine performance | Photon advantage | Vanilla Spark only |
| Custom workloads on same cluster | No | Yes |
| Egress from one cloud | Painful | Painful |
| Right answer when | Small/mid platform team, need governance, fast | Strong platform team, cost-sensitive, K8s-first shop |

______________________________________________________________________

## Internal components

### Driver

The driver is the process running your `SparkSession` and `main()`. It owns:

- The `SparkContext` and the high-level APIs you call
- The DAGScheduler, which turns RDD/DataFrame lineage into a DAG of *stages* split at shuffle boundaries
- The TaskScheduler (and a `SchedulerBackend` per cluster manager — K8s, YARN, standalone), which submits *tasks* (one per partition per stage) to executors and tracks completion
- The BlockManagerMaster, which tracks where cached/shuffle blocks live
- The Spark UI, event log, and metrics endpoints

In cluster mode on K8s, the driver is its own pod. Losing it kills the application.

### Executors

JVM processes (or pods, on K8s) that actually run tasks. Each executor has:

- A fixed number of cores (slots for concurrent tasks)
- A heap split between execution memory (joins, aggregations, sorts) and storage memory (cached blocks), unified under Spark's memory manager — borrows between regions are dynamic
- A BlockManager that holds cached partitions and shuffle output
- Off-heap memory for Tungsten binary row format and (optionally) cached data

Executors are stateless from the application's perspective but stateful from the *shuffle* perspective — losing an executor mid-stage means recomputing any shuffle blocks it held (unless you have an external shuffle service or shuffle data on S3).

### Cluster manager

The thing that hands out resources. Options:

- Kubernetes — Spark talks to the K8s API directly; each executor is a pod
- YARN — still dominant in on-prem Hadoop shops
- Standalone — Spark's built-in scheduler
- Mesos — deprecated, gone
- Local — single-JVM for dev

### Catalyst optimizer

The query planner. Pipeline:

1. Parsed logical plan — raw AST from SQL or DataFrame API
1. Analyzed logical plan — resolves columns, functions, types against the catalog
1. Optimized logical plan — applies rule-based optimizations (predicate pushdown, column pruning, constant folding, join reordering, subquery elimination, ~150+ rules)
1. Physical plan — picks join strategies (broadcast hash, sort-merge, shuffle hash, broadcast nested loop), exchange operators, scan operators
1. Code-generated execution — Tungsten compiles whole stages of operators into a single JVM bytecode method (whole-stage codegen) to eliminate iterator overhead

You can inspect any stage with `df.explain(mode="formatted" | "extended" | "cost")`.

### Tungsten execution engine

Spark's columnar/binary execution layer:

- UnsafeRow — off-heap binary row format, no Java object overhead
- Whole-stage code generation — collapses operator chains into one tight loop
- Cache-aware computation — explicit memory management instead of GC'd objects
- Vectorized Parquet/ORC readers — batch decode into columnar buffers

This is the core reason Spark SQL is much faster than equivalent RDD code.

### Adaptive Query Execution (AQE)

Re-plans the query *during* execution based on actual shuffle statistics. On by default since 3.2. It can:

- Coalesce small post-shuffle partitions
- Switch sort-merge joins to broadcast joins when one side ends up small
- Split skewed partitions (covered below)
- Optimize partition counts for stage outputs

If you're not using AQE on a self-hosted Spark, turn it on (`spark.sql.adaptive.enabled=true`).

### Shuffle subsystem

The most failure-prone part of Spark. Each shuffle writes map output to local disk (or S3, with newer plugins), partitioned by hash/range, then reducers fetch their assigned partitions over the network. Components:

- ShuffleManager (sort-based since 2.0; Tungsten sort variant)
- External shuffle service — a long-running daemon that serves shuffle files independently of the executor lifetime (so executors can be removed without losing shuffle data). On K8s, this is awkward — see the EKS gotchas.
- Shuffle service alternatives on K8s: Apache Celeborn, Magnet (LinkedIn), or S3-backed remote shuffle.

### BlockManager

Per-executor (and driver) component that stores cached RDDs, broadcast variables, and shuffle blocks. Coordinates with the driver's BlockManagerMaster to track replicas. Storage levels span memory-only, memory-and-disk, off-heap, and replicated variants.

### Catalog

Where Spark looks up tables, schemas, and functions. Options:

- In-memory (ephemeral, default)
- Hive metastore (most common in production)
- AWS Glue Data Catalog (Glue-compatible metastore)
- Iceberg REST catalog, Nessie, Polaris — newer table-format-native catalogs
- Unity Catalog (Databricks; UC OSS now exists)

### Structured Streaming engine

Stream processing built on top of the DataFrame API and the same Catalyst/Tungsten stack. Micro-batch by default, with continuous processing as a long-standing experimental mode, and now Real-Time Mode (4.1) for true sub-second latency. State is stored in a pluggable state store (default HDFSBackedStateStore; RocksDB state store is preferred for large state).

### Spark Connect

Newer thin-client / server split. Your client (Python, Scala, Go, Swift, Rust) sends an unresolved logical plan over gRPC to a long-running Spark server, which executes it. Decouples client lifecycle from cluster lifecycle. GA in 4.0 with high feature parity to Spark Classic, including new clients for Go, Swift, and Rust, and a `spark.api.mode` setting to switch between Classic and Connect.

### DataSource V2 API

Modern pluggable connector API for sources/sinks. All the lakehouse table formats (Delta, Iceberg, Hudi) implement V2. Pushes down filters, projections, aggregates, and limits.

______________________________________________________________________

## Scaling

Horizontal scaling is the default model: more executors = more parallel tasks. Targets:

- Parallelism: aim for `spark.sql.shuffle.partitions` ≈ 2–4× total executor cores. Default 200 is wrong for almost everything.
- Partition size: target ~128–256 MB per shuffle partition after AQE coalescing. Smaller → scheduler overhead dominates; larger → spill and OOM.
- Executor sizing: 4–8 cores and 16–32 GB heap per executor is the standard sweet spot. Bigger executors hurt GC; smaller hurt broadcast efficiency.

Dynamic allocation lets Spark add/remove executors based on pending tasks. On K8s, this works but historically required either an external shuffle service or shuffle tracking (`spark.dynamicAllocation.shuffleTracking.enabled=true`) to avoid losing shuffle data when executors scale down.

Karpenter on EKS is the modern node-provisioning story — much faster scale-up than Cluster Autoscaler, with native spot/diversified-instance handling. Pair with PodDisruptionBudgets and graceful executor decommissioning (`spark.decommission.enabled=true`) for Spot tolerance.

Vertical scaling mostly means giving the driver more memory for big collect/broadcast plans, and giving executors more off-heap for large hash tables.

______________________________________________________________________

## Data skew

Skew is when one or a few partitions hold disproportionate data, causing a long tail where 199 tasks finish in 30s and one task runs for 20 minutes. Tools, in order of preference:

1. Turn on AQE skew join handling (`spark.sql.adaptive.skewJoin.enabled=true`) — Spark detects skewed partitions at runtime and splits them into sub-partitions, replicating the matching side of the join. This handles most real-world skew without code changes.
1. Broadcast joins — if the small side is < ~10 MB (or whatever you set `spark.sql.autoBroadcastJoinThreshold` to), broadcast it and avoid the shuffle entirely. AQE can promote a sort-merge join to broadcast mid-query.
1. Salting — append a random salt to the join key on the skewed side, explode the dim side by the salt range, then join. Manual but reliable when AQE isn't enough (e.g., extreme skew, complex join graphs).
1. Filter out null/sentinel keys first — a huge amount of "skew" in practice is `NULL` or `0` keys piling into one partition. Filter or pre-aggregate them separately.
1. Repartition by a better key before the operation, or use range partitioning.
1. Two-phase aggregation for skewed groupBy — partial agg with salt, then final agg without. Less needed now that AQE handles aggregate skew well.

Diagnose skew from the Spark UI's stage summary metrics: look at the *task duration* and *shuffle read size* distributions. Median vs. max is the tell.

______________________________________________________________________

## Recent (≥ 2024) additions to be mindful of

### Spark 4.0 (released February 2025)

- ANSI mode on by default — Spark now throws on integer overflow, divide-by-zero, invalid casts, etc., instead of returning NULL. This breaks pipelines. Audit before upgrading; set `spark.sql.ansi.enabled=false` if you need the old behavior temporarily.
- VARIANT data type — efficient binary encoding for semi-structured JSON, comparable in spirit to Snowflake's VARIANT. Faster than parsing JSON strings every read.
- SQL pipe syntax — `FROM t |> WHERE x > 0 |> SELECT a, b` style, more readable for long transformations.
- SQL UDFs, session variables, and SQL scripting with control flow — reusable SQL functions without Python/Scala roundtrips.
- String collation support — locale-aware sorting and comparison.
- Spark Connect GA, with new Python/Scala/Go/Swift/Rust clients.
- Java 17 by default, structured logging (JSON-format logs), Python Data Source API, polymorphic Python UDTFs, Arrow-optimized Python UDFs.
- Streaming State Data Source reader — query Structured Streaming state directly with SQL for debugging.

### Spark 4.1 (released 2025)

- Spark Declarative Pipelines (SDP) — a declarative framework where you define datasets and queries and Spark handles the execution graph, dependency ordering, parallelism, checkpoints, and retries. Effectively OSS DLT.
- Structured Streaming Real-Time Mode for continuous, sub-second latency, dropping to single-digit milliseconds for stateless tasks.
- Spark ML on Connect GA for the Python client, SQL Scripting GA, VARIANT shredding GA for faster reads on semi-structured data, recursive CTEs, and new KLL and Theta approximate sketches.
- Significant RocksDB state store improvements (memory unification, snapshot lag detection, checksum verification).

### Ecosystem (≥ 2024)

- Apache Spark Kubernetes Operator launched as an official Apache subproject in May 2025, supporting Spark 3.5+. This is increasingly the canonical way to run Spark on K8s; the Kubeflow operator remains a viable alternative but the long-term momentum is on the Apache one.
- Apache Celeborn maturing as the leading remote shuffle service — addresses the EKS shuffle reliability gap.
- Iceberg and Delta Lake both shipped major changes (V3 spec for Iceberg with row-level deletes via deletion vectors, Delta UniForm for Iceberg compatibility).
- Databricks: Photon now covers most operators including UDFs in some cases; Liquid Clustering replaces Z-order; serverless compute is the default direction.

### Gotchas worth flagging on upgrade

- ANSI mode changes can silently fail jobs that previously ran on bad data — run with `ansi.enabled=true` in staging well before prod.
- Spark Connect's session model differs from Classic in subtle ways (no `SparkContext`, restricted Hadoop config access) — some libraries still don't work cleanly under Connect.
- Java 17 strict module access can break libraries that reflect into JDK internals; expect to add `--add-opens` flags.
