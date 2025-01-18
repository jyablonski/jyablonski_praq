# Timestamps

In the context of databases and SQL, timestamps are data types used to store date and time values. Here's a detailed explanation:

## What are Timestamps?

A **timestamp** is a precise point in time, represented by a date and a time of day. Timestamps are commonly used in databases to record and track events, transactions, or changes over time. They are crucial for applications that require time-based data analysis, logging, scheduling, and more.

## Key Components of Timestamps

1. **Date**: Represents the year, month, and day.
   - Example: `2024-05-16`

2. **Time**: Represents the hours, minutes, and seconds, often including fractions of a second.
   - Example: `10:00:00` or `10:00:00.123`

3. **Time Zone (optional)**: Indicates the time offset from UTC (Coordinated Universal Time).
   - Example: `+02:00` (two hours ahead of UTC)

## Types of Timestamps in SQL

1. **`timestamp`** (or `timestamp without time zone`):
   - **Description**: Stores the date and time without any time zone information.
   - **Use Case**: Suitable for applications where the time zone is implied or irrelevant, and consistent across all usage scenarios.
   - **Example**: `2024-05-16 10:00:00`

2. **`timestamptz`** (or `timestamp with time zone`):
   - **Description**: Stores the date and time along with time zone information. Internally, it is stored in UTC and converted to the local time zone of the client upon retrieval.
   - **Use Case**: Ideal for applications dealing with multiple time zones, ensuring that times are accurately compared and displayed according to user or system preferences.
   - **Example**: `2024-05-16 10:00:00+02`

## Example in SQL

Let's define a table with both types of timestamp columns and insert some data:

```sql
CREATE TABLE event_log (
    event_id serial PRIMARY KEY,
    event_name varchar(255) NOT NULL,
    event_time timestamp NOT NULL,
    event_time_utc timestamptz NOT NULL
);

INSERT INTO event_log (event_name, event_time, event_time_utc)
VALUES ('System Reboot', '2024-05-16 10:00:00', '2024-05-16 10:00:00+02');
```

## Querying Timestamps

When querying timestamps, the difference between `timestamp` and `timestamptz` becomes apparent in how they handle time zones:

```sql
SELECT event_name, event_time, event_time_utc FROM event_log;
```

- `event_time` will return `2024-05-16 10:00:00` as stored.
- `event_time_utc` will return the equivalent time adjusted to the local time zone of the client. If the client is in UTC+00:00, it would return `2024-05-16 08:00:00` (since `10:00:00+02:00` is the same as `08:00:00+00:00`).

## How Timestamps are Stored in Databases

The storage of timestamps in a database involves specific internal representations depending on whether the timestamp includes time zone information or not.

### Storage of Timestamps in PostgreSQL

1. **`timestamp` (or `timestamp without time zone`)**:
   - **Internal Representation**: This data type stores the date and time without any reference to a time zone. Internally, it is stored as a 64-bit integer representing microseconds (or sometimes milliseconds, depending on the database system) from a reference date and time, which is usually the PostgreSQL epoch: midnight (00:00:00) on January 1, 2000.
   - **Precision**: PostgreSQL supports fractional seconds with up to six digits of precision.
   - **Storage Size**: It typically requires 8 bytes of storage.

2. **`timestamptz` (or `timestamp with time zone`)**:
   - **Internal Representation**: This type stores the date and time as an absolute moment in time, including time zone conversion. Internally, PostgreSQL stores this as a 64-bit integer representing the number of microseconds from the PostgreSQL epoch (UTC). When a `timestamptz` value is inserted, it is converted to UTC and stored. When queried, it is converted back to the client's local time zone.
   - **Precision**: Like `timestamp`, it supports fractional seconds with up to six digits of precision.
   - **Storage Size**: It also typically requires 8 bytes of storage.

### How Timestamps are Handled

#### Insertion and Storage

- **`timestamp` Example**:

  ``` sql
  INSERT INTO timestamp_test (timestamp_no_tz) VALUES ('2024-05-16 10:00:00');
  ```

  - The value '2024-05-16 10:00:00' is stored exactly as entered, without any time zone conversion.

- **`timestamptz` Example**:

  ``` sql
  INSERT INTO timestamp_test (timestamp_utc) VALUES ('2024-05-16 10:00:00+02');
  ```

  - The value '2024-05-16 10:00:00+02' is converted to UTC before storage. In this case, it is stored as '2024-05-16 08:00:00+00' (since the original time is two hours ahead of UTC).

#### Retrieval and Display

- **`timestamp` Example**:

  ```sql
  SELECT timestamp_no_tz FROM timestamp_test;
  ```

  - The stored value is retrieved and displayed exactly as it was stored, without any time zone information.

- **`timestamptz` Example**:

  ```sql
  SET TIMEZONE='America/New_York'; -- Set the client's time zone to Eastern Time (UTC-5 or UTC-4 depending on DST)
  SELECT timestamp_utc FROM timestamp_test;
  ```

  - The stored UTC value is converted to the client's time zone (Eastern Time in this example). If the UTC value was '2024-05-16 08:00:00+00', it will be displayed as '2024-05-16 04:00:00-04' or '2024-05-16 03:00:00-05', depending on whether daylight saving time is in effect.

## Unix Epoch Timestamps

Unix epoch timestamps are closely related to the `timestamp` and `timestamptz` data types in SQL databases, and they provide another way to represent and work with date and time values. A **Unix epoch timestamp** is a way to represent a specific point in time as the number of seconds (or milliseconds) that have elapsed since the Unix epoch, which is defined as 00:00:00 Coordinated Universal Time (UTC), Thursday, 1 January 1970.

### How Unix Epoch Timestamps Relate to SQL Timestamps

1. **Storage and Representation**:
   - Unix epoch timestamps are typically stored as integers or floating-point numbers, representing the number of seconds or milliseconds since the Unix epoch.

2. **Conversion**:
   - SQL databases often provide functions to convert between Unix epoch timestamps and SQL `timestamp` or `timestamptz` data types.

### Practical Use in SQL

- **Storing Unix Epoch Timestamps**:
  - You can store Unix epoch timestamps directly as integers in your database, but converting them to SQL `timestamp` or `timestamptz` can provide more readability and ease of use.

- **Example Table with Unix Epoch**:

  ```sql
  CREATE TABLE event_log (
      event_id serial PRIMARY KEY,
      event_name varchar(255) NOT NULL,
      event_time_epoch bigint NOT NULL,
      event_time timestamp NOT NULL,
      event_time_utc timestamptz NOT NULL
  );
  ```

### Conversion Functions

Most SQL databases, including PostgreSQL, provide built-in functions to convert between Unix epoch timestamps and SQL timestamp types.

- **From Unix Epoch to `timestamp`**:

  ```sql
  SELECT to_timestamp(event_time_epoch) AS event_time
  FROM event_log;
  ```

- **From `timestamp` to Unix Epoch**:

  ```sql
  SELECT extract(epoch FROM event_time) AS event_time_epoch
  FROM event_log;
  ```

### Example Use Case

- **Inserting Data**:

  ```sql
  INSERT INTO event_log (event_name, event_time_epoch, event_time, event_time_utc)
  VALUES (
      'System Reboot',
      1713481200,  -- Unix epoch timestamp for '2024-05-16 10:00:00' UTC
      to_timestamp(1713481200),  -- Convert Unix epoch to timestamp
      to_timestamp(1713481200) AT TIME ZONE 'UTC'  -- Convert and set as UTC
  );
  ```

- **Querying Data**:

  ```sql
  SELECT event_id, event_name, event_time, event_time_utc,
         to_timestamp(event_time_epoch) AS event_time_from_epoch
  FROM event_log;
  ```
