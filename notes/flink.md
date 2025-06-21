# Apache Flink

[Article](https://www.redpanda.com/guides/event-stream-processing-kafka-streams-vs-flink)

Apache Flink is an Open Source high-performance framework designed for large scale data processing, particularly in the real-time streaming domain. It provides true event-by-event streaming capabilities, as opposed to typical Python or Spark solutions which typically offer only micro-batch streaming solutions (polling every 30 - 60 seconds for new data etc).

Features extremely low latency and stateful computations which enable users to process live data and generate insights on the fly.

So, to get data flowing into Flink, you need producer services or systems that generate and send the streaming data into a source Flink can read from.

- [Producer app] --> Kafka topic --> Flink job --> Sink (console / DB / etc.)

## Use Cases

1. Fraud Detection - these events must be caught instantly
2. Online Ad Tech bidding - to get the best offer you have to be first
3. IoT Sensor Data - detect equipment failure or anomalies in real time to avoid costly downtime or incidents
4. General Anomaly Detection

## Workflow Examples

1. Real Time Sliding Window Aggregation - calculate rolling sum every 5 minutes across a streaming data feed
2. Session Windowing for User Activity - detect user sessions by grouping clicks with inactivity gaps of 30 minutes
3. Join multiple stream datasets together for Fraud Detection - join transactions and real time blacklist updates to flag suspicious payments as they happen
4. Detect fraud patterns like 3 failed login attempts with 5 minutes followed by a successful login
5. Process sensor data streams with out-of-order events, discarding or handling late data gracefully.

## Flink Memory Requirements

* Event-by-event streaming: Flink processes records one-by-one with low latency.
* Stateful operators: Flink’s memory use heavily depends on how much state you keep *between* events. For example, if you do windowing, joins, aggregations, or any complex event processing that requires keeping data in memory (state), you’ll need enough memory to hold that state.
* Checkpointing: Flink regularly snapshots state to durable storage, but the in-memory working set still needs to fit in memory for low latency.
* Backpressure & buffers: Flink also buffers data internally in network shuffles, which requires some memory.


- Flink's memory usage is tightly coupled with the size and complexity of your streaming state, not just how many events you process per second.

---

### Spark Memory Requirements

* Micro-batching: Spark processes data in batches and often keeps intermediate results and shuffle data in memory.
* RDD caching & shuffles: Spark uses more memory for caching, shuffles, and holding batches in memory until the entire micro-batch finishes.
* Garbage collection: Because it handles batches, GC pressure can be high if batch sizes or joins are large.

---
| Aspect                   | Flink                                    | Spark                                         |
| ------------------------ | ---------------------------------------- | --------------------------------------------- |
| Processing model         | Event-by-event streaming                 | Micro-batching streaming                      |
| Memory usage depends on  | Size of state and buffered events        | Batch size, caching, shuffles, and batch data |
| Typical memory footprint | Can be lower if state is small & simple  | Usually larger due to batch overhead          |
| Use case                 | Low latency, continuous event processing | Higher latency, batch-style streaming         |


* Flink can run on much lower memory if your streaming job is stateless or has very small state, Flink’s memory footprint can be quite small compared to Spark.
* However, if your Flink job keeps a large state (like large windowed aggregations or joins), you’ll still need enough memory to hold that state efficiently.

* A Flink job doing simple filtering or stateless map functions can run with very little memory.
* A Flink job tracking millions of active sessions or long time-windowed joins will require memory comparable to a Spark cluster running similar workloads.


## Flink vs Spark
Use Flink when you need milisecond-level latency for your streaming workloads.  if < 30s latency is okay, then Flink is probably not necessary for your use case and you can just use Python or Spark for your processing framework.
