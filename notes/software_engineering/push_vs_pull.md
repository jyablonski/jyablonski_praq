# Push vs. Pull

Push and pull describe **which side initiates a data transfer**. They do not describe where the data is stored, and they are separate from whether work runs on a schedule or in response to an event.

## Pull

In a pull model, the consumer or collector initiates a request to read data from a source. The source returns the data in response. Although the data travels from source to consumer, the consumer initiated the exchange, so this is called pull.

```text
Collector -- requests data --> Source
Collector <-- returns data --- Source
```

For example, Prometheus periodically requests `/metrics` from an app and stores the returned samples. In an OpenMetadata metadata ingestion workflow, a connector can query a configured database or pipeline system, read its metadata, and send the extracted records to OpenMetadata.

The pulling side usually owns the polling cadence, source connection, and read credentials. It learns about changes when it checks the source again, so the update delay depends partly on the polling interval.

## Push

In a push model, the producer initiates a request that sends data to a receiving service. The receiver accepts the data and processes or stores it.

```text
Producer -- sends data --> Receiver
```

For example, after a pipeline changes a table or job definition, the pipeline can call OpenMetadata's API and send the updated metadata. The pipeline initiates the transfer; OpenMetadata does not need to poll that pipeline for this update.

The pushing side usually owns when to send and needs to handle delivery concerns such as retries, duplicate requests, and what to do if the receiver is unavailable. The receiving side needs an API or other endpoint that accepts the incoming data.

## A Scheduled Workflow Can Still Pull

A schedule answers **when a job runs**; push or pull answers **who initiates the data exchange**. A cron job can start a connector that pulls from a source. It can also start a script that pushes a file or API request to another service.

An OpenMetadata workflow can therefore use both patterns in one run:

```text
Schedule starts ingestion worker
    -> worker pulls metadata from the configured source
    -> worker sends the extracted metadata to OpenMetadata
```

That workflow is pull from the source and push to OpenMetadata. Running the workflow from OpenMetadata or from an external orchestrator changes who schedules and launches the job; it does not by itself change the direction of the source read. See the [OpenMetadata ingestion deployment docs](https://docs.open-metadata.org/v1.12.x/deployment/ingestion) for the internally managed and externally managed workflow options.

## Quick Check

Ask: **Which component makes the first request that causes this data to move?** If the collector calls the source to fetch data, it is pull. If the producer calls the receiver to deliver data, it is push. A system can use both patterns at different boundaries in the same pipeline.
