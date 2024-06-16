# Kappa Architecture

The Kappa Architecture diverges from the Lambda Architecture to only provide a single Layer: the Stream Processaing Layer which serves both real-time and historical data. It also avoids the potential inconsistencies of maintaining separate batch and speed layers.

This architecture is ideal when you can use streaming data to handle all data processing needs.

The downsides include it may not be suitable for all use cases. Robust Stream Processing tools need to be stood up and maintained in order to serve data products out of this workflow. Other potential issues can stem from event duplication, message sequencing etc and issues of that nature while trying to process data.

Typical tools include Apache Kafka, Flink, and Cassandra

## Workflow

The workflow involves setting up something like an Apache Kafka Cluster to store Messages, or Events. Your Applications can then send these messages over to Kafka for them to be stored in Topics

Consumers can then consume the message from these Topics at their own Pace to read the data in the message and transform it and/or write it back to some destination source or database.