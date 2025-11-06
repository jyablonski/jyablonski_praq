# Common Packages

## Datetime

Python’s built-in [`datetime`](https://docs.python.org/3/library/datetime.html) module is used for working with dates and times.

- Key Classes

  - `datetime.datetime` – represents a specific date and time.
  - `datetime.date` – represents a date without time.
  - `datetime.time` – represents time without date.
  - `datetime.timedelta` – represents the difference between two date/time values.

- Common Patterns

  ```python
  from datetime import datetime, timedelta

  now = datetime.now()
  tomorrow = now + timedelta(days=1)
  formatted = now.strftime("%Y-%m-%d %H:%M:%S")
  parsed = datetime.strptime("2025-08-10", "%Y-%m-%d")
  ```

- Time Zones

  - `datetime.now(timezone.utc)` is a quick way of using UTC timestamps
  - Use [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html) (Python 3.9+) or `pytz` for timezone-aware datetimes.
  - Always work in UTC internally, and convert to local time at presentation.

---

## Logging

The [`logging`](https://docs.python.org/3/library/logging.html) module provides a flexible framework for emitting log messages.

- Why use logging instead of `print()`?

  - Log levels and filtering.
  - Easy redirection to files, streams, or external services.
  - Timestamps, source module, and more for each log.

- Common Log Levels

  - `DEBUG` – Detailed diagnostic info.
  - `INFO` – Normal operational messages.
  - `WARNING` – An indication something unexpected happened, but the program can still run.
  - `ERROR` – Due to a more serious problem, the program may not be able to perform some function.
  - `CRITICAL` – A serious error, program may abort.

- Handlers determine where logs go (files, streamed to the console, or sent over the network to a remote location)

  - `StreamHandler` – Logs to console.
  - `FileHandler` – Logs to a file.
  - `RotatingFileHandler` – Automatically rotates logs when they reach a size limit.
  - `SMTPHandler`, `HTTPHandler`, etc. – Send logs to email, HTTP endpoints.

  ```python
  import logging

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)

  logger.info("Service started")
  logger.error("Failed to fetch data", exc_info=True)
  ```

---

## Requests

The [`requests`](https://docs.python-requests.org/en/latest/) library simplifies making HTTP requests.

- Basic Usage

  ```python
  import requests

  response = requests.get("https://api.github.com")
  print(response.status_code, response.json())
  ```

- Sessions

  - Maintain cookies, headers, and connections across requests.
  - Improves performance with connection pooling.

  ```python
  with requests.Session() as s:
      s.headers.update({"Authorization": "Bearer TOKEN"})
      r = s.get("https://api.example.com/data")
  ```

- Retries

  - Not built-in directly; use `urllib3`’s `Retry` via `requests.adapters.HTTPAdapter`.

  ```python
  from requests.adapters import HTTPAdapter
  from urllib3.util.retry import Retry

  session = requests.Session()
  retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
  adapter = HTTPAdapter(max_retries=retry_strategy)
  session.mount("https://", adapter)
  ```

---

## Polars

[Polars](https://pola.rs/) is a fast, multi-threaded DataFrame library built in Rust.

- DataFrame Basics

  ```python
  import polars as pl

  df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
  print(df)
  ```

- Vectorization

  - Operate on entire columns at once for speed.

  ```python
  df = df.with_columns((pl.col("a") + pl.col("b")).alias("sum"))
  ```

- `.apply()`

  - Allows custom Python functions, but is slower because it breaks vectorization.
  - Prefer native expressions or `map` when possible.

  ```python
  df = df.with_columns(pl.col("a").apply(lambda x: x * 2).alias("double_a"))
  ```

- Performance Tip

  - Avoid `.apply()` unless you must use Python-only logic; otherwise leverage Polars expressions for better speed.

---

## SQLAlchemy

[SQLAlchemy](https://www.sqlalchemy.org/) is Python’s most popular ORM and SQL toolkit.

- Core Components

  - SQLAlchemy Core – Lower-level, explicit SQL building.
  - SQLAlchemy ORM – Maps Python classes to database tables.

- Example

  ```python
  from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

  engine = create_engine("sqlite:///:memory:")
  metadata = MetaData()
  users = Table("users", metadata, Column("id", Integer, primary_key=True), Column("name", String))
  metadata.create_all(engine)
  ```

- ORM Advantages

  - Allows you to write python code instead of raw SQL queries which simplifies things
  - Don't have to worry about SQL dialect differences
  - Automatic Parametrization & safety

- Connections

  - Use connection pooling automatically.
  - Use context managers to ensure cleanup.

- Best Practices

  - Keep transactions short.
  - Prefer parameterized queries to avoid SQL injection.
  - Parameterized queries send values to the database separately from the SQL command
  - `SELECT * FROM users WHERE name = ?` with Parameters sent: `["Robert'); DROP TABLE users;--"]`
  - Escaped means the special characters in the input - things like quotes ('), semicolons (;), and comment markers (--) — are encoded or quoted in a way that makes them harmless inside the SQL statement.
  - The database treats the parameter entirely as a literal value in the name column, not as SQL. Even if it contains characters like ; or --, they are escaped, so the query just searches for that exact string and returns 0 rows — no extra SQL commands are executed.

```py
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///:memory:")

with engine.connect() as conn:
    # BAD (string concatenation) – vulnerable to SQL injection
    unsafe_name = "Robert'); DROP TABLE users;--"
    query = f"SELECT * FROM users WHERE name = '{unsafe_name}'"
    # conn.execute(query)  # Don't do this

    # GOOD (parameterized) – values are escaped safely
    safe_query = text("SELECT * FROM users WHERE name = :name")
    result = conn.execute(safe_query, {"name": unsafe_name})

    for row in result:
        print(row)

# ORM does this out of the box for you
# session.query(User).filter(User.name == unsafe_name).all()
```

Engine is the starting point to manage the database connection pool. IT does not represent a single connection, it manages a pool of connections.

- `engine.connect()` is used to manually acquire a connection from the pool. With a connection object, you can execute SQL commands
- Doing this in a context manager will automatically clean up the connection and close it when you're done
- `engine.begin()` starts a connection with an active transaction started, and automatically commits if no errors occur

```py
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
```

You can mix and match syntax depending on your SQL needs

```py
# Simple CRUD? Use ORM (easy and clean)
@app.post("/users")
async def create_user(user: UserCreate):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    return db_user

# Complex reporting query? Use raw SQL (readable and obvious) w/ parameterization
@app.get("/reports/daily-stats")
async def daily_stats(date: str):
    query = text("""
        SELECT
            DATE(created_at) as date,
            COUNT(DISTINCT user_id) as active_users,
            AVG(prediction_score) as avg_score
        FROM reporting.user_predictions
        WHERE DATE(created_at) = :date
        GROUP BY DATE(created_at)
    """)
    return conn.execute(query, {"date": date}).fetchone()
```

---

## Asyncio

[asyncio](https://docs.python.org/3/library/asyncio.html) is Python’s built-in framework for asynchronous I/O.

- Core Concepts

  - `async def` defines a coroutine.
  - `await` suspends execution until the awaited coroutine completes.
  - Event loop schedules and runs coroutines.

- Example

  ```python
  import asyncio

  async def fetch_data():
      await asyncio.sleep(1)
      return "done"

  async def main():
      result = await fetch_data()
      print(result)

  asyncio.run(main())
  ```

- When to Use

  - Network I/O (APIs, websockets, DB drivers).
  - Not for CPU-bound tasks — use multiprocessing instead.

---

## Multithreaded

Python supports multi-threading via the `threading` module.

- Important Note

  - The GIL (Global Interpreter Lock) means threads don’t run Python bytecode truly in parallel.
  - Still useful for I/O-bound tasks (file I/O, network requests).

- Example

  ```python
  import threading

  def worker(name):
      print(f"Worker {name} starting")

  threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
  for t in threads:
      t.start()
  for t in threads:
      t.join()
  ```

- Alternatives

  - For CPU-bound tasks -> `multiprocessing`
  - For async-friendly I/O -> `asyncio`.
