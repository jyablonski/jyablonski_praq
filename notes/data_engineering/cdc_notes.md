# CDC w/ Debezium + Kafka

Change Data Capture (CDC) is a pattern for tracking and propagating changes in a database (inserts, updates, deletes) so that downstream systems can react to or replicate those changes in near real-time, instead of relying on periodic full-table scans or snapshots.

Traditional batch ETL works by re-querying source tables on a schedule, often comparing timestamps or doing full reloads. This is expensive, high-latency, and tends to miss intermediate states (a row updated three times between batches looks like one change). CDC flips the model: rather than asking "what's different now?", you continuously stream every change as it happens at the source.

Log-based CDC is the gold standard for relational databases. It taps into the database's write-ahead log (WAL) or transaction log, which records every change in a durable, ordered way. By reading the WAL, a CDC tool can capture every insert/update/delete with low latency and minimal load on the source DB.

Trigger-based or query-based are alternative options for databases without robust log access, but they have higher latency and are generally harder to maintain.

## Architecture Overview

Source Postgres -> Debezium connector (running on MSK Connect) -> MSK (Kafka) topics -> downstream consumers (Snowpipe Streaming, S3 sinks, etc.)

Debezium reads the Postgres WAL via a logical replication slot, emits one Kafka topic per source table, and tracks its read position in the `connect-offsets` topic.

## Postgres Source Setup

Required Postgres config:

- `wal_level = logical`
- `max_replication_slots` and `max_wal_senders` sized for the number of connectors
- A replication user with `REPLICATION` privilege and `SELECT` on tracked tables
- A logical replication slot (Debezium creates this on first connect, or you can pre-create it)
- A publication if using `pgoutput` plugin (default for modern Debezium)

Critical operational settings:

- `max_slot_wal_keep_size`: caps WAL retention for slow consumers. Too low risks data loss if Debezium falls behind; too high risks filling source disk if Debezium is stuck.
- Monitor `pg_replication_slots.confirmed_flush_lsn` vs `pg_current_wal_lsn()` for slot lag.

## Debezium Connector Essentials

Per-table topics named `{topic.prefix}.{schema}.{table}`. Each event has `before`, `after`, `source`, `op`, `ts_ms` fields.

Key configs to know:

- `snapshot.mode`: `initial` (snapshot then stream), `never` (stream only, requires seeded offset), `initial_only`, `schema_only`
- `table.include.list` / `table.exclude.list`: which tables to capture
- `heartbeat.interval.ms`: emits periodic heartbeats so Postgres advances the slot on low-traffic tables. Skipping this is the #1 way to fill source DB disk.
- `slot.name`: replication slot name, must be unique per connector
- `publication.name`: pgoutput publication

## Initial Snapshot vs Streaming

First start: Debezium acquires a consistent read position, pages through tracked tables, emits `op: r` events, then switches to streaming from the captured LSN.

Adding a new table later does **not** trigger snapshotting by default. Use **incremental snapshots** (signal table or signal channel) to backfill a new table without restarting everything.

## Self-Hosted Kafka Connect Lifecycle (REST API)

When running Kafka Connect yourself, you have full REST control:

| Operation | Endpoint |
| ---------------- | ----------------------------------------- |
| Create connector | `POST /connectors` |
| Pause | `PUT /connectors/{name}/pause` |
| Resume | `PUT /connectors/{name}/resume` |
| Restart | `POST /connectors/{name}/restart` |
| Read offsets | `GET /connectors/{name}/offsets` (3.6+) |
| Patch offsets | `PATCH /connectors/{name}/offsets` (3.6+) |
| Reset offsets | `DELETE /connectors/{name}/offsets` |
| Delete | `DELETE /connectors/{name}` |

Typical upgrade flow without data gaps:

1. `PUT /pause` on the old connector
1. Wait one `offset.flush.interval.ms` cycle
1. `GET /offsets` to read current position
1. Create new connector with `snapshot.mode=never`, stopped
1. `PATCH /offsets` on new connector with values from step 3
1. Resume new connector
1. Delete old connector

## MSK Connect Reality

MSK Connect does **not** expose the Kafka Connect REST API. You only get the AWS SDK / CLI / Terraform interface:

- `CreateConnector`
- `UpdateConnector` (very limited; mostly worker capacity)
- `DeleteConnector`
- `DescribeConnector`
- `ListConnectors`
- `UpdateConnectorOffsets` (added late 2024)

What you lose:

- No pause/resume. Closest equivalent is `DeleteConnector` (offsets persist in `connect-offsets` so recreating with the same name resumes naturally).
- No restart. Delete and recreate.
- No granular task-level control.
- Most config changes (hostname, table list, etc.) require delete-and-recreate, not update.
- Logs only via CloudWatch / S3 / Firehose.

## Seeding Offsets on MSK Connect

### Path A: Recent MSK Connect with `UpdateConnectorOffsets`

1. Read offsets from old connector (via API or by consuming `connect-offsets`)
1. `DeleteConnector` on the old one
1. `CreateConnector` for the new one with `snapshot.mode=never`
1. `UpdateConnectorOffsets` to seed the new connector's position
1. Connector resumes from seeded LSN on next start

### Path B: Older MSK Connect, no offset API

MSK is just a Kafka cluster; you have full producer/consumer access to `connect-offsets`. Seed offsets directly:

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers="b-1.msk.example.com:9098",
    security_protocol="SASL_SSL",
    sasl_mechanism="AWS_MSK_IAM",
    key_serializer=lambda k: json.dumps(k).encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Key shape: [connector_name, source_partition_dict]
key = ["users-cdc-new", {"server": "dbserver1"}]
value = {
    "lsn": 23847234923,
    "lsn_commit": 23847234900,
    "txId": 4928374,
    "ts_usec": 1714857600000000,
    "snapshot": False,
}

producer.send("connect-offsets", key=key, value=value)
producer.flush()
```

Gotchas:

- Key serialization must match exactly; Connect looks up offsets by exact key match. A wrong key silently falls through to `snapshot.mode` behavior, causing a gap.
- Connector must be stopped (deleted) when seeding, otherwise its in-memory offset overwrites yours on next flush.
- Read old offsets by consuming `connect-offsets` from the beginning, filtering by old connector name, taking latest value per key (compacted topic).

## The Core Invariant

As long as the offset in `connect-offsets` is preserved AND the source DB still has WAL data from that offset forward, the connector can be stopped, reconfigured, or rebuilt without data loss.

The two failure modes that cause gaps:

1. Losing the offset (no resume point)
1. Source DB recycles WAL past the offset before the connector reconnects

Operational protections:

- WAL retention longer than max expected downtime
- Replicated, durable `connect-offsets` topic (default replication factor of 3)
- Any connector recreation seeds offsets before starting

## Failover Considerations

- Postgres replication slots are per-instance until PG16 (failover slots). Failing over to a standby loses the slot; recreate it on the new primary at the captured LSN, then restart Debezium with `snapshot.mode=never`.
- Brief write downtime during cutover, but no data loss.

## When to Skip MSK Connect

Teams doing heavy CDC sometimes self-host Kafka Connect on EKS/ECS to regain:

- Full REST API (pause, resume, restart, offset management)
- Granular task control
- Easier debugging (live log access)
- Faster config iteration without delete/recreate

Tradeoff: you operate Kafka Connect yourself. Worth it past a certain scale of CDC complexity.
