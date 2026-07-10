CREATE SCHEMA gold;

CREATE TABLE gold.dim_customers (
    customer_id integer PRIMARY KEY,
    customer_name text NOT NULL,
    segment text NOT NULL,
    region text NOT NULL
);

INSERT INTO gold.dim_customers (customer_id, customer_name, segment, region)
VALUES
    (1, 'Acme Supply Co.', 'Enterprise', 'West'),
    (2, 'Beacon Retail', 'Mid-Market', 'East'),
    (3, 'Cedar Works', 'Small Business', 'South'),
    (4, 'Delta Services', 'Enterprise', 'Central'),
    (5, 'Evergreen Goods', 'Mid-Market', 'West'),
    (6, 'Foxglove Studio', 'Small Business', 'East'),
    (7, 'Granite Labs', 'Enterprise', 'South'),
    (8, 'Harbor Market', 'Mid-Market', 'Central');

CREATE TABLE gold.fct_orders (
    order_id integer PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES gold.dim_customers (customer_id),
    order_date date NOT NULL,
    amount numeric(12, 2) NOT NULL,
    status text NOT NULL CHECK (status IN ('completed', 'cancelled'))
);

INSERT INTO gold.fct_orders (order_id, customer_id, order_date, amount, status)
SELECT
    month_offset * 30 + order_in_month AS order_id,
    ((order_in_month + month_offset) % 8) + 1 AS customer_id,
    (
        DATE '2025-01-01'
        + month_offset * INTERVAL '1 month'
        + ((order_in_month * 3 + month_offset) % 27) * INTERVAL '1 day'
    )::date AS order_date,
    ROUND(
        75.00
        + month_offset * 18.00
        + order_in_month * 1.85
        + ((order_in_month + month_offset) % 8) * 4.25,
        2
    )::numeric(12, 2) AS amount,
    CASE
        WHEN (order_in_month + month_offset) % 7 = 0 THEN 'cancelled'
        ELSE 'completed'
    END AS status
FROM generate_series(0, 11) AS months(month_offset)
CROSS JOIN generate_series(1, 30) AS orders(order_in_month);
