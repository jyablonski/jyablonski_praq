# Apache Flink

Open Source high-performance framework designed for large scale data processing, particularly in the real-time streaming domain.  

Features extremely low latency and stateful computations which enable users to process live data and generate insights on the fly.

Commonly paired with tools like Apache Kafka for Streaming Delivery, and then putting Flink on top of that to process that data.

## Flink vs Spark
Use Flink when you need milisecond-level latency for your streaming workloads.  if < 30s latency is okay, then Flink is probably not necessary for your use case and you can just use Python or Spark for your processing framework.