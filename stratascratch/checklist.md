# SQL Notes Checklist

## Table of Contents

1. [Window Functions](#window-functions)
1. [String Functions](#string-functions)
1. [Date & Time Functions](#date--time-functions)
1. [Conditional Aggregation](#conditional-aggregation)
1. [Numeric Operations](#numeric-operations)
1. [Joins & Set Operations](#joins--set-operations)

______________________________________________________________________

## Window Functions

### LAG and LEAD

Use `lag()` and `lead()` to access values from previous or subsequent rows within a partitioned result set.

```sql
select
    user_id,
    record_date,
    lag(record_date) over (partition by user_id order by record_date) as prev_record_date,
    lead(record_date) over (partition by user_id order by record_date) as next_record_date
from sf_events;

-- Result:
| --  | user_id | record_date | prev_record_date | next_record_date |
| --- | ------- | ----------- | ---------------- | ---------------- |
| --  | 1       | 2024-01-01  | NULL             | 2024-01-05       |
| --  | 1       | 2024-01-05  | 2024-01-01       | 2024-01-10       |
| --  | 1       | 2024-01-10  | 2024-01-05       | NULL             |
```

Key points:

- `lag()` grabs the previous row's value; the first row returns `NULL`
- `lead()` grabs the next row's value; the last row returns `NULL`
- No `GROUP BY` required; works row-by-row within partitions

Common use case: calculating elapsed time between events.

```sql
select
    cust_id,
    timestamp,
    timestamp - lag(timestamp) over (partition by cust_id order by timestamp) as time_since_last_event
from events;
```

### Ranking Functions

Three ranking functions with different gap behaviors:

```sql
select
    name,
    score,
    row_number() over (order by score desc) as row_num,
    dense_rank() over (order by score desc) as d_rank,
    rank() over (order by score desc) as rnk
from scores;

-- Result (assuming scores: 100, 95, 95, 90):
| --  | name  | score | row_num | d_rank | rnk |
| --- | ----- | ----- | ------- | ------ | --- |
| --  | Alice | 100   | 1       | 1      | 1   |
| --  | Bob   | 95    | 2       | 2      | 2   |
| --  | Carol | 95    | 3       | 2      | 2   |
| --  | Dave  | 90    | 4       | 3      | 4   |
```

| Function | Ties Behavior | Gaps After Ties |
| -------------- | ------------------------- | --------------------- |
| `row_number()` | No ties (arbitrary order) | Never has gaps |
| `dense_rank()` | Same rank for ties | No gaps (1, 2, 2, 3) |
| `rank()` | Same rank for ties | Has gaps (1, 2, 2, 4) |

### PERCENT_RANK

Returns a percentile ranking between 0 and 1.

```sql
select
    name,
    score,
    percent_rank() over (order by score) as percentile
from scores;

-- Result:
| --  | name  | score | percentile |
| --- | ----- | ----- | ---------- |
| --  | Dave  | 90    | 0.0        |
| --  | Bob   | 95    | 0.33       |
| --  | Carol | 95    | 0.33       |
| --  | Alice | 100   | 1.0        |
```

______________________________________________________________________

## String Functions

### SPLIT_PART

Extract a specific segment from a delimited string. Note: 1-indexed.

```sql
select
    business_address,
    split_part(business_address, ' ', 1) as street_number,
    split_part(business_address, ' ', 2) as street_name
from businesses;

-- Input: '123 Main Street'
-- Result: street_number = '123', street_name = 'Main'
```

### STRING_TO_ARRAY and UNNEST

Convert strings to arrays and expand arrays into rows.

```sql
-- Convert string to array
select string_to_array(lower('Hello World Example'), ' ') as words;
-- Result: {'hello', 'world', 'example'}

-- Expand array into individual rows
select unnest(string_to_array(lower('Hello World Example'), ' ')) as word;
-- Result:
| --  | word    |
| --- | ------- |
| --  | hello   |
| --  | world   |
| --  | example |
```

Common use case: word frequency analysis.

```sql
select
    unnest(string_to_array(lower(contents), ' ')) as word,
    count(*) as frequency
from posts
group by 1
order by 2 desc;
```

### TRIM

Remove leading and trailing whitespace from strings.

```sql
select
    trim(business_name) as business_name
from businesses;

-- Input: '  Acme Corp  '
-- Result: 'Acme Corp'
```

### CONCAT

Combine multiple strings together.

```sql
select
    concat(first_name, ' ', last_name) as full_name
from users;

-- Input: first_name = 'John', last_name = 'Doe'
-- Result: 'John Doe'
```

______________________________________________________________________

## Date & Time Functions

### DATE_PART / DATE_TRUNC

Extract specific components from dates.

- Note `date_trunc` rounds down to the start of the specified period.

```sql
select
    invoicedate,
    date_part('month', invoicedate) as month,
    date_part('year', invoicedate) as year,
    date_trunc('month', invoicedate) as month_start
from invoices;

-- Input: '2024-03-15'
-- Result: month = 3, year = 2024, month_start = '2024-03-01'
```

### TO_CHAR for Date Formatting

Create formatted date strings.

```sql
select
    created_at,
    to_char(created_at, 'YYYY-MM') as year_month,
    to_char(created_at, 'Mon YYYY') as month_year_label
from orders;

-- Input: '2024-03-15'
-- Result: year_month = '2024-03', month_year_label = 'Mar 2024'
```

### Date Arithmetic with INTERVAL

Add or subtract time from dates.

```sql
select
    created_at,
    created_at + interval '7 days' as plus_7_days,
    created_at - interval '1 month' as minus_1_month
from orders;

-- Input: '2024-03-15'
-- Result: plus_7_days = '2024-03-22', minus_1_month = '2024-02-15'
```

Alternative syntax (database-dependent):

```sql
select
    created_at,
    date_add(created_at, interval 7 day) as plus_7_days
from orders;
```

### BETWEEN for Date Ranges

Filter dates inclusively on both ends.

```sql
select *
from orders
where created_at between '2024-01-01' and '2024-01-31';

-- Includes both January 1st AND January 31st
```

Caution with timestamps: If `created_at` includes time, `'2024-01-31'` is interpreted as `'2024-01-31 00:00:00'`, potentially excluding records later in the day. Consider:

```sql
where created_at >= '2024-01-01'
  and created_at < '2024-02-01'
```

______________________________________________________________________

## Conditional Aggregation

### Conditional Counts

Count distinct values based on conditions.

```sql
select
    count(distinct user_id) as n_total_users,
    count(distinct case when is_apple_device = 1 then user_id end) as n_apple_users,
    count(distinct case when is_apple_device = 0 then user_id end) as n_non_apple_users
from user_devices;

-- Result:
| --  | n_total_users | n_apple_users | n_non_apple_users |
| --- | ------------- | ------------- | ----------------- |
| --  | 1000          | 600           | 400               |
```

### Conditional Sums for Pivoting

Create columns for counts by category.

```sql
select
    user_id,
    sum(case when date_trunc('month', created_at) = '2024-11-01' then 1 else 0 end) as nov_comments,
    sum(case when date_trunc('month', created_at) = '2024-12-01' then 1 else 0 end) as dec_comments
from comments
group by user_id;

-- Result:
| --  | user_id | nov_comments | dec_comments |
| --- | ------- | ------------ | ------------ |
| --  | 1       | 5            | 12           |
| --  | 2       | 8            | 3            |
```

______________________________________________________________________

## Numeric Operations

### Integer Division Pitfall

Always cast to float when dividing integers to avoid truncation.

```sql
select
    5 / 2 as integer_division,           -- Result: 2 (truncated!)
    5 / 2.0 as float_division,           -- Result: 2.5
    5 * 1.0 / 2 as cast_to_float,        -- Result: 2.5
    cast(5 as decimal) / 2 as explicit   -- Result: 2.5
from dual;
```

Common use case: calculating percentages.

```sql
select
    count(case when status = 'completed' then 1 end) * 1.0 / count(*) as completion_rate
from orders;
```

### CEIL and FLOOR

Round numbers to nearest integers.

```sql
select
    value,
    ceil(value) as rounded_up,
    floor(value) as rounded_down
from (values (4.2), (4.8), (-2.3)) as t(value);

-- Result:
| --  | value | rounded_up | rounded_down |
| --- | ----- | ---------- | ------------ |
| --  | 4.2   | 5          | 4            |
| --  | 4.8   | 5          | 4            |
| --  | -2.3  | -2         | -3           |
```

______________________________________________________________________

## Joins & Set Operations

### Self-Joins for Sequential Events

Find users who made a second purchase within 7 days.

```sql
select distinct
    t1.user_id,
    t1.created_at as first_purchase,
    t2.created_at as second_purchase
from transactions t1
inner join transactions t2
    on t1.user_id = t2.user_id
    and t2.created_at > t1.created_at
    and t2.created_at <= t1.created_at + interval '7 days';
```

Alternative with date difference:

```sql
select distinct t1.user_id
from transactions t1
inner join transactions t2
    on t1.user_id = t2.user_id
    and t2.created_at - t1.created_at between interval '1 day' and interval '7 days';
```

### CROSS JOIN

Create Cartesian products: every row from table A paired with every row from table B.

```sql
-- Generate all date/product combinations for reporting
select
    d.date,
    p.product_id
from dates d
cross join products p;

-- If dates has 30 rows and products has 10 rows, result has 300 rows
```

Use cases:

- Generating date spines for time series
- Creating all possible combinations for analysis
- Building scaffolds for left joins to find missing data

### UNION vs UNION ALL

Stack results from multiple queries.

```sql
-- UNION: removes duplicates (slower)
select user_id from table_a
union
select user_id from table_b;

-- UNION ALL: keeps all rows including duplicates (faster)
select user_id from table_a
union all
select user_id from table_b;
```

Best practice: Use `UNION ALL` when you know there won't be duplicates or don't need deduplication. It's more performant because it skips the sort/distinct operation.
