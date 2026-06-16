# Async Ingestion Consumer

Small runnable demo of an async ingestion pipeline backed by RabbitMQ and Postgres.

The producer:

- creates a RabbitMQ queue named `ingestion-runs`
- inserts queued run metadata into Postgres
- publishes mock ingestion messages into RabbitMQ
- can seed forever during the 20-minute run window or stop after a finite `TOTAL_MESSAGES` count

The consumer:

- reads ingestion messages from RabbitMQ
- pulls messages asynchronously with bounded concurrency
- simulates source reads with `asyncio.sleep(2)`
- simulates saves with `asyncio.sleep(2)`
- updates run metadata in Postgres table `ingestion_runs`

Run it from the project root:

```bash
docker compose -f async/docker-compose.yaml up --build
```

The producer and consumers run for 20 minutes by default, or until you stop the stack. Tune that with `RUN_SECONDS` and `SEED_INTERVAL_SECONDS` in `docker-compose.yaml`.

Scale consumers from the project root:

```bash
docker compose -f async/docker-compose.yaml up --build --scale consumer=3
```

That runs one producer and three consumer worker processes. With `MAX_CONCURRENCY=3`, that allows up to 9 ingestion runs to actively sync at once.

For a finite batch, set `TOTAL_MESSAGES` on the `producer` service. For example, `TOTAL_MESSAGES: 10000` means the producer will publish 10k messages and then stop producing. `SEED_MESSAGES` controls how many messages are published per producer tick, so set `SEED_MESSAGES: 10000` if you want all 10k queued immediately, or use a smaller value to drip-feed the queue.

RabbitMQ management UI:

```text
http://localhost:15672
username: ingest
password: ingest
```

Postgres uses the container filesystem only, so run metadata is removed when the container is removed.

## Packages

The consumer uses a small set of Python packages:

- `aio-pika`: async RabbitMQ client. It connects to RabbitMQ, declares the queue, publishes mock ingestion messages, and consumes work from the queue without blocking the event loop.
- `asyncpg`: async Postgres client. It creates the `ingestion_runs` table and writes run status updates while other ingestion tasks are still running.
- `asyncio`: Python's built-in async runtime. It schedules concurrent ingestion work, waits without blocking during mock I/O, and handles graceful shutdown.

The Docker Compose services are:

- `producer`: the Python message producer. It creates queued ledger rows and publishes RabbitMQ messages.
- `consumer`: the Python async ingestion worker. This service is safe to scale horizontally because it no longer produces messages.
- `rabbitmq`: the message broker and queue.
- `postgres`: ephemeral metadata storage for ingestion run status.

## What Async Enables

Async lets this single Python process make progress on multiple ingestion runs at the same time. In this demo each pull and save waits for two seconds to mimic network or storage I/O. With normal blocking code, one run would sit idle during those waits and prevent other runs from moving forward.

Here, while one ingestion run is waiting on `mock_pull_data` or `mock_save_data`, the event loop can switch to another run. That gives you overlapping work with a small amount of code and without starting a separate process per message.

The result is a consumer that can:

- keep listening to RabbitMQ
- process several messages concurrently
- update Postgres run metadata as each message changes state
- keep a hard cap on concurrent work with `MAX_CONCURRENCY`
- shut down cleanly after 20 minutes or when Compose stops the container

Splitting producer and consumer matters when scaling. If the consumer also produced messages, `--scale consumer=3` would create three producers too. With separate services, scaling consumers only adds processing capacity.

## How The Async Code Works

`async def` defines a coroutine function. Calling it creates work that can be scheduled by the event loop. The coroutine actually pauses and resumes at `await` points.

`await` is where the function yields control back to the event loop. In this demo, `await asyncio.sleep(2)` stands in for slow I/O. While that sleep is waiting, other queued ingestion tasks can run.

`async with` manages async resources whose setup or teardown may need to await. The script uses it for RabbitMQ message acknowledgements and for Postgres connection pool access:

- `async with incoming.process(...)` acknowledges the RabbitMQ message when processing succeeds.
- `async with pool.acquire() as conn` borrows a Postgres connection and returns it to the pool afterward.
- `async with pool, connection` closes Postgres and RabbitMQ resources cleanly on shutdown.

`asyncio.Semaphore(MAX_CONCURRENCY)` limits how many ingestion runs can execute the expensive section at once. RabbitMQ may deliver several messages, but `async with semaphore` ensures only `MAX_CONCURRENCY` runs are actively pulling and saving data at a time.

`asyncio.create_task(...)` starts background work without waiting for it immediately. The consumer uses it to process each RabbitMQ message while continuing to receive more messages from the queue.

`asyncio.wait_for(...)` adds a timeout around an awaitable. The script uses it in two places:

- wait up to `RUN_SECONDS` before ending the demo run
- wait up to `SEED_INTERVAL_SECONDS` between producer batches of mock messages

`asyncio.gather(...)` waits for multiple async tasks together. During shutdown, the script cancels the producer task and gathers it, then gathers any in-flight message-processing tasks so the database pool is not closed while a run is still writing metadata.
