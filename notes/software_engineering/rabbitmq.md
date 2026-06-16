# RabbitMQ

## What it is

RabbitMQ is an open-source message broker that implements AMQP 0-9-1 (with plugins for MQTT, STOMP, and AMQP 1.0). It sits between services and decouples producers from consumers: senders hand messages to RabbitMQ, and it routes and buffers them until a consumer is ready. Written in Erlang/OTP, which is why clustering and fault-tolerance are baked into its runtime.

Core use cases: async task queues, work distribution, pub/sub fan-out, and buffering between systems with mismatched throughput.

## How it works: producers and consumers

The key insight is that producers never publish directly to queues. They publish to an *exchange*, and the exchange routes to one or more queues based on bindings and routing keys.

```
Producer --> Exchange --(binding)--> Queue --> Consumer
```

Exchange types:

- `direct` — routing key matches the binding key exactly (point-to-point).
- `topic` — routing key matched against patterns (`logs.*.error`).
- `fanout` — broadcast to all bound queues, ignores routing key (pub/sub).
- `headers` — route on message header attributes instead of routing key.

Flow:

1. Producer publishes a message + routing key to an exchange.
1. Exchange evaluates bindings, copies the message into matching queues.
1. Queue holds the message (FIFO-ish) until delivered.
1. Consumer either *pushes* (broker delivers via `basic.consume`) or *pulls* (`basic.get`, polling — generally discouraged).

Acknowledgements & reliability:

- Consumers send an `ack` after processing. Until acked, the message stays "unacknowledged" and is redelivered if the consumer dies.
- `prefetch` (QoS) limits how many unacked messages a consumer holds, which is how you do fair load balancing across workers.
- Publishers can use *publisher confirms* to know the broker accepted a message.
- Unroutable/expired/rejected messages can be sent to a *dead-letter exchange*.

## Memory vs. disk

RabbitMQ uses a hybrid memory/disk model for performance and durability:

- Transient messages live in memory only and are lost on broker restart.
- Persistent messages (`delivery_mode=2`) are written to disk, but only durable to a restart if the queue is also declared `durable`. You need both: a durable queue *and* persistent messages.
- Even persistent messages are kept in memory for fast delivery; disk is the durability backstop, not the primary read path.
- Under memory pressure RabbitMQ *pages* messages out to disk to avoid hitting the high-watermark, which triggers flow control (producers get throttled).

Quorum queues (the modern default for durability) always persist to disk via a Raft log. Classic queues can be transient or durable. Streams persist an append-only log on disk and are designed for high-throughput replay.

### Raft

Raft is a consensus algorithm — a protocol for getting a cluster of nodes to agree on an ordered sequence of operations (a replicated log), even when nodes crash or messages are delayed. It's the practical, more-understandable successor to Paxos. The whole design goal was "consensus you can actually reason about and implement correctly," which is why it shows up everywhere now (etcd, Consul, CockroachDB, and RabbitMQ's quorum queues).

It has two main pieces:

- Leader election. One node is the leader; the rest are followers. All writes go through the leader. If followers stop hearing heartbeats from the leader, they start an election, and a candidate that collects votes from a quorum becomes the new leader. (That's where quorum plugs in — Raft uses quorums as its decision rule.) Terms (monotonic counters) prevent a stale old leader from causing damage if it comes back.
- Log replication. The leader appends each operation to its log and ships it to followers. Once a quorum has persisted the entry, the leader marks it committed and applies it to the state machine. A committed entry is durable — it survives any minority of nodes failing.

## HA: single node or clustered?

RabbitMQ can run single-node, but it's designed to cluster.

- Clustering: multiple nodes share users, vhosts, exchanges, and bindings (metadata is replicated to all nodes). But by default a *queue* lives on one node — clustering alone doesn't make queue contents highly available.
- Quorum queues are the recommended HA mechanism: queue contents are replicated across an odd number of nodes (3 or 5) using Raft, with automatic leader election. Survives node loss as long as a majority is up.
- Streams are also replicated and HA via a similar Raft-based design.
- Classic mirrored queues were the old HA approach — *deprecated and removed* in recent versions. Don't use them; use quorum queues.
- Clustering assumes a LAN-quality network (low latency). For multi-DC, use the *Shovel* or *Federation* plugins rather than stretching a cluster.

Practical HA setup: 3-node cluster + quorum queues + a load balancer in front of the client connections, with `durable` queues and `persistent` messages.

## Quick comparison of queue types

| Type | Durability | HA | Best for |
| ------- | ------------- | --------------- | ----------------------------- |
| Classic | optional | none (alone) | simple, single-node workloads |
| Quorum | always (disk) | Raft-replicated | reliable work queues |
| Stream | always (disk) | Raft-replicated | high-throughput, replay/log |
