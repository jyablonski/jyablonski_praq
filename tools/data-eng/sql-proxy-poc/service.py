import json
import os
import sys
import time
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row


MAX_ATTEMPTS = 20
RETRY_DELAY_SECONDS = 2


def log(event: str, **fields: object) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "service": os.environ["SERVICE_NAME"],
        **fields,
    }
    print(json.dumps(record, sort_keys=True), flush=True)


def connection_details() -> dict[str, object]:
    host = os.environ["DB_HOST"]
    port = int(os.environ["DB_PORT"])
    return {
        "connection_mode": os.environ["CONNECTION_MODE"],
        "configured_target": f"{host}:{port}",
        "database": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
    }


def check_connection() -> None:
    host = os.environ["DB_HOST"]
    port = int(os.environ["DB_PORT"])
    details = connection_details()
    dsn = {
        "dbname": os.environ["DB_NAME"],
        "host": host,
        "password": os.environ["DB_PASSWORD"],
        "port": port,
        "user": os.environ["DB_USER"],
    }

    log("connecting", **details)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with psycopg.connect(
                **dsn,
                application_name=os.environ["SERVICE_NAME"],
                connect_timeout=3,
                row_factory=dict_row,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            current_database() AS database,
                            current_user AS user_name,
                            inet_server_addr()::text AS backend_host,
                            inet_server_port() AS backend_port,
                            inet_client_addr()::text AS client_host,
                            inet_client_port() AS client_port,
                            current_setting('application_name') AS application_name
                        """
                    )
                    server = cursor.fetchone()
                    cursor.execute(
                        """
                        INSERT INTO connection_checks (
                            service_name,
                            connection_mode,
                            configured_target,
                            client_host,
                            backend_host,
                            backend_port
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            os.environ["SERVICE_NAME"],
                            os.environ["CONNECTION_MODE"],
                            details["configured_target"],
                            server["client_host"],
                            server["backend_host"],
                            server["backend_port"],
                        ),
                    )
                    check_id = cursor.fetchone()["id"]

            log(
                "connected",
                check_id=check_id,
                **details,
                backend_host=server["backend_host"],
                backend_port=server["backend_port"],
                client_host=server["client_host"],
                client_port=server["client_port"],
                application_name=server["application_name"],
            )
            log(
                "verified",
                message=(
                    "The client reached the database through its configured target; "
                    "the backend answered on PostgreSQL port 5432."
                ),
                **details,
                backend_port=server["backend_port"],
            )
            return
        except (OSError, psycopg.OperationalError) as error:
            if attempt == MAX_ATTEMPTS:
                log("failed", attempt=attempt, error=str(error), **details)
                raise

            log(
                "retrying",
                attempt=attempt,
                next_attempt=attempt + 1,
                error=f"{type(error).__name__}: {error}",
                **details,
            )
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    try:
        check_connection()
    except Exception as error:
        print(f"service failed: {error}", file=sys.stderr, flush=True)
        sys.exit(1)
