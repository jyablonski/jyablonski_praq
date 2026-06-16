import asyncio
import json
import os
import random
import signal
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import aio_pika
import asyncpg


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://ingest:ingest@localhost:5672/")
POSTGRES_DSN = os.getenv(
    "POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"
)
QUEUE_NAME = os.getenv("QUEUE_NAME", "ingestion-runs")
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "3"))
SEED_MESSAGES = int(os.getenv("SEED_MESSAGES", "5"))
TOTAL_MESSAGES = int(os.getenv("TOTAL_MESSAGES", "0"))
RUN_SECONDS = int(os.getenv("RUN_SECONDS", "1200"))
SEED_INTERVAL_SECONDS = int(os.getenv("SEED_INTERVAL_SECONDS", "30"))


@dataclass(frozen=True)
class IngestionMessage:
    run_id: str
    source_name: str
    batch_count: int = 3

    @classmethod
    def from_body(cls, body: bytes) -> "IngestionMessage":
        payload = json.loads(body.decode("utf-8"))
        return cls(
            run_id=payload["run_id"],
            source_name=payload["source_name"],
            batch_count=int(payload.get("batch_count", 3)),
        )

    def to_body(self) -> bytes:
        return json.dumps(
            {
                "run_id": self.run_id,
                "source_name": self.source_name,
                "batch_count": self.batch_count,
            }
        ).encode("utf-8")


async def wait_for_postgres() -> asyncpg.Pool:
    while True:
        try:
            return await asyncpg.create_pool(POSTGRES_DSN, min_size=1, max_size=10)
        except OSError as exc:
            print(f"postgres not ready yet: {exc}")
            await asyncio.sleep(2)


async def wait_for_rabbitmq() -> aio_pika.RobustConnection:
    while True:
        try:
            return await aio_pika.connect_robust(RABBITMQ_URL)
        except OSError as exc:
            print(f"rabbitmq not ready yet: {exc}")
            await asyncio.sleep(2)


async def setup_database(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingestion_runs (
                run_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                status TEXT NOT NULL,
                records_pulled INTEGER NOT NULL DEFAULT 0,
                output_location TEXT,
                error TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                started_at TIMESTAMPTZ,
                finished_at TIMESTAMPTZ
            )
            """
        )


async def setup_queue(
    channel: aio_pika.abc.AbstractChannel, prefetch_count: int | None = None
) -> aio_pika.Queue:
    if prefetch_count is not None:
        await channel.set_qos(prefetch_count=prefetch_count)
    return await channel.declare_queue(QUEUE_NAME, durable=True)


async def seed_messages(
    pool: asyncpg.Pool,
    exchange: aio_pika.abc.AbstractExchange,
    message_count: int,
    source_offset: int = 0,
) -> None:
    for idx in range(message_count):
        message = IngestionMessage(
            run_id=str(uuid.uuid4()),
            source_name=f"mock_source_{source_offset + idx + 1}",
            batch_count=random.randint(2, 4),
        )
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ingestion_runs (run_id, source_name, status)
                VALUES ($1, $2, 'queued')
                ON CONFLICT (run_id) DO NOTHING
                """,
                message.run_id,
                message.source_name,
            )

        await exchange.publish(
            aio_pika.Message(
                message.to_body(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=QUEUE_NAME,
        )
        print(f"queued {message.run_id} for {message.source_name}")


async def seed_messages_until_stopped(
    pool: asyncpg.Pool,
    exchange: aio_pika.abc.AbstractExchange,
    stop_event: asyncio.Event,
) -> None:
    total_seeded = 0
    while not stop_event.is_set():
        if TOTAL_MESSAGES and total_seeded >= TOTAL_MESSAGES:
            print(f"producer seeded requested total_messages={TOTAL_MESSAGES}")
            return

        message_count = SEED_MESSAGES
        if TOTAL_MESSAGES:
            message_count = min(SEED_MESSAGES, TOTAL_MESSAGES - total_seeded)

        await seed_messages(pool, exchange, message_count, source_offset=total_seeded)
        total_seeded += message_count
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=SEED_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            pass


async def mock_pull_data(source_name: str, batch_idx: int) -> list[dict]:
    print(f"pulling batch {batch_idx} from {source_name}")
    await asyncio.sleep(2)
    return [
        {
            "external_id": f"{source_name}-{batch_idx}-{record_idx}",
            "value": random.randint(1, 100),
            "pulled_at": datetime.now(UTC).isoformat(),
        }
        for record_idx in range(1, 4)
    ]


async def mock_save_data(run_id: str, batch_idx: int, records: list[dict]) -> str:
    print(f"saving {len(records)} records from run {run_id}, batch {batch_idx}")
    await asyncio.sleep(2)
    return f"mock://warehouse/ingestion_runs/{run_id}/batch-{batch_idx}.json"


async def ensure_run_row(pool: asyncpg.Pool, message: IngestionMessage) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO ingestion_runs (run_id, source_name, status)
            VALUES ($1, $2, 'queued')
            ON CONFLICT (run_id) DO NOTHING
            """,
            message.run_id,
            message.source_name,
        )


async def mark_running(pool: asyncpg.Pool, message: IngestionMessage) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE ingestion_runs
            SET status = 'running',
                started_at = COALESCE(started_at, now()),
                error = NULL
            WHERE run_id = $1
            """,
            message.run_id,
        )


async def mark_succeeded(
    pool: asyncpg.Pool,
    message: IngestionMessage,
    records_pulled: int,
    output_locations: list[str],
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE ingestion_runs
            SET status = 'succeeded',
                records_pulled = $2,
                output_location = $3,
                finished_at = now()
            WHERE run_id = $1
            """,
            message.run_id,
            records_pulled,
            json.dumps(output_locations),
        )


async def mark_failed(
    pool: asyncpg.Pool, message: IngestionMessage, error: Exception
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE ingestion_runs
            SET status = 'failed',
                error = $2,
                finished_at = now()
            WHERE run_id = $1
            """,
            message.run_id,
            repr(error)[:2000],
        )


async def process_ingestion_run(
    pool: asyncpg.Pool, message: IngestionMessage, semaphore: asyncio.Semaphore
) -> None:
    async with semaphore:
        await ensure_run_row(pool, message)
        await mark_running(pool, message)

        records_pulled = 0
        output_locations = []
        try:
            for batch_idx in range(1, message.batch_count + 1):
                records = await mock_pull_data(message.source_name, batch_idx)
                output_location = await mock_save_data(
                    message.run_id, batch_idx, records
                )
                records_pulled += len(records)
                output_locations.append(output_location)

            await mark_succeeded(pool, message, records_pulled, output_locations)
            print(f"succeeded {message.run_id}: {records_pulled} records")
        except Exception as exc:
            await mark_failed(pool, message, exc)
            print(f"failed {message.run_id}: {exc!r}")
            raise


async def handle_message(
    incoming: aio_pika.IncomingMessage,
    pool: asyncpg.Pool,
    semaphore: asyncio.Semaphore,
) -> None:
    async with incoming.process(requeue=False):
        message = IngestionMessage.from_body(incoming.body)
        await process_ingestion_run(pool, message, semaphore)


def build_stop_event() -> asyncio.Event:
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    return stop_event


async def produce() -> None:
    stop_event = build_stop_event()
    pool = await wait_for_postgres()
    connection = await wait_for_rabbitmq()

    async with pool, connection:
        await setup_database(pool)

        channel = await connection.channel()
        await setup_queue(channel)

        print(
            f"producing queue={QUEUE_NAME} seed_messages={SEED_MESSAGES} "
            f"seed_interval_seconds={SEED_INTERVAL_SECONDS} "
            f"total_messages={TOTAL_MESSAGES or 'unbounded'} run_seconds={RUN_SECONDS}"
        )

        producer = asyncio.create_task(
            seed_messages_until_stopped(pool, channel.default_exchange, stop_event)
        )
        try:
            await asyncio.wait_for(
                asyncio.shield(producer),
                timeout=RUN_SECONDS,
            )
        except asyncio.TimeoutError:
            print(f"producer run window complete after {RUN_SECONDS} seconds")
            stop_event.set()
        finally:
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)


async def consume() -> None:
    stop_event = build_stop_event()
    pool = await wait_for_postgres()
    connection = await wait_for_rabbitmq()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async with pool, connection:
        await setup_database(pool)

        channel = await connection.channel()
        queue = await setup_queue(channel, prefetch_count=MAX_CONCURRENCY)

        processing_tasks: set[asyncio.Task[None]] = set()

        async def on_message(incoming: aio_pika.IncomingMessage) -> None:
            task = asyncio.create_task(handle_message(incoming, pool, semaphore))
            processing_tasks.add(task)
            task.add_done_callback(processing_tasks.discard)

        consumer_tag = await queue.consume(on_message)
        print(
            f"consuming queue={QUEUE_NAME} max_concurrency={MAX_CONCURRENCY} "
            f"run_seconds={RUN_SECONDS}"
        )
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=RUN_SECONDS)
        except asyncio.TimeoutError:
            print(f"run window complete after {RUN_SECONDS} seconds")
            stop_event.set()
        finally:
            await queue.cancel(consumer_tag)
            if processing_tasks:
                print(f"waiting for {len(processing_tasks)} in-flight tasks")
                await asyncio.gather(*processing_tasks, return_exceptions=True)


async def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SERVICE_MODE", "consumer")
    if mode == "producer":
        await produce()
    elif mode == "consumer":
        await consume()
    else:
        raise ValueError("mode must be 'producer' or 'consumer'")


if __name__ == "__main__":
    asyncio.run(main())
