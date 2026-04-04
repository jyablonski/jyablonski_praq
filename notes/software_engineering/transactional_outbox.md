# Transactional Outbox Pattern

## The Problem

You cannot atomically write to a database and publish to an external message broker in a single operation. A crash between the two leaves your system inconsistent — the DB write committed but the event was never published, or vice versa.

## Core Strategy

Write the event to an `outbox` table in the same database transaction as your business data. A relay process reads pending rows and processing them, then marks them as completed once processed. Atomicity is guaranteed by the database — the event either commits with the business write or neither does.

The relay uses `select ... for update skip locked` to claim rows safely across concurrent workers. Delivery is at-least-once, so consumers must be idempotent.

## Alternatives

Postgres-native queuing tools like River collapse the relay and consumer into one: workers pull jobs and execute Go functions directly, with no external broker needed. This is the right default when your producers and consumers share a Postgres instance and your workload is job-shaped rather than event-shaped.

External brokers like SQS/SNS or RabbitMQ are the better fit when you need multi-consumer fan-out, cross-language transport, or replay semantics. A common hybrid is using the outbox for the atomic write guarantee, then having the relay forward into Kafka or SQS for distribution.

## When River + Postgres Makes Sense

These are cases where your stack is Go, your consumers share the same Postgres instance, and the workload is discrete jobs rather than a stream of events.

- User signup triggers a welcome email job — write the user row and enqueue the job in the same transaction, River handles retry and backoff if the email provider is down
- Generating a PDF report on demand — the request writes a record and enqueues a generation job, the worker picks it up asynchronously and uploads the result to S3
- Scheduled billing runs — River's cron-style scheduling fires a job to charge each subscription, with durable state in Postgres so a crashed worker doesn't double-charge
- Post-purchase order fulfillment in a monolith — reserve inventory, write the order, and enqueue a fulfillment job atomically; all consumers are Go workers in the same service
- Webhook delivery to external URLs — enqueue one job per webhook target with exponential backoff, River retries failed deliveries without you managing a retry queue manually
- Sending Slack notifications after an internal workflow step — write the state transition and enqueue the notification job together, no risk of a silent drop

## When an External Broker Makes More Sense

These are cases where fan-out, cross-service transport, or volume push you toward SQS/SNS, RabbitMQ, or Kafka.

- A payment event needs to trigger fraud detection, the ledger service, email notifications, analytics, and a webhook dispatcher simultaneously — publish once to an SNS topic, each service consumes from its own SQS queue at its own pace
- Your producer is a Go service but your consumers include a Python ML scoring service and a Node.js notification service — a broker provides language-neutral transport, River does not apply here
- A data team needs to backfill a new attribution model using 90 days of historical page view events — Kafka's log retention makes replay trivial, River and SQS discard events once consumed
- High-volume clickstream or telemetry data where producers emit millions of events per hour — a dedicated broker with its own storage handles backpressure and burst buffering better than a Postgres outbox table under that write load
- An event needs to be consumed by a service owned by a different team with its own infrastructure — a broker is the clean boundary, sharing a Postgres instance across team boundaries is not
