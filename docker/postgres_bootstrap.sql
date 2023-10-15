CREATE SCHEMA source;
CREATE SCHEMA dbt_stg;
CREATE SCHEMA dbt_prod;

-- default directory for every statement in this bootstrap
SET search_path TO source;

-- Create the sales data tables
CREATE TABLE customers (
    customer_id serial PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    created_at timestamp default current_timestamp
);

CREATE TABLE products (
    product_id serial PRIMARY KEY,
    product_name VARCHAR(100),
    product_category VARCHAR(50),
    product_price DECIMAL(10, 2),
    created_at timestamp default current_timestamp
);

CREATE TABLE sales (
    sale_id serial PRIMARY KEY,
    sale_date DATE,
    customer_id INT,
    product_id INT,
    quantity INT,
    total_amount DECIMAL(10, 2),
    created_at timestamp default current_timestamp
);

CREATE TABLE invoices (
    invoice_id serial PRIMARY KEY,
    customer_id integer,
    sale_id integer,
    is_voided boolean default FALSE,
    created_at timestamp default current_timestamp

);

-- if Cash then leave `payment_type_info` NULL
-- if Credit Card then input last 4 digits
-- if Gift Card then input Full Gift Card number
CREATE TYPE payment_enum AS ENUM ('Cash', 'Credit Card', 'Gift Card');
CREATE TABLE payments (
    payment_id serial PRIMARY KEY,
    amount decimal(10, 2),
    payment_type payment_enum,
    payment_type_info text,
    invoice_id integer,
    created_at timestamp default current_timestamp
);

-- this basically acts as an audit table - will have multiple rows for each change per customer id / integration
CREATE TYPE integration_enum AS ENUM ('Mailchimp', 'Salesforce', 'Hubspot');
CREATE TABLE integrations (
    integration_id serial PRIMARY KEY,
    customer_id integer,
    integration_type integration_enum,
    is_active integer,
    created_at timestamp default current_timestamp
);

CREATE TABLE orders (
    order_id serial PRIMARY KEY,
    external_data json not null,
    created_at timestamp default current_timestamp
);

-- Insert some dummy data
INSERT INTO customers (customer_name, customer_email)
VALUES
    ('Johnny Allstar', 'customer1@example.com'),
    ('Aubrey Plaza', 'customer2@example.com'),
    ('John Wick', 'customer3@example.com');

INSERT INTO products (product_name, product_category, product_price)
VALUES
    ('Product A', 'Category 1', 10.99),
    ('Product B', 'Category 2', 19.99),
    ('Product C', 'Category 1', 15.99);

INSERT INTO sales (sale_date, customer_id, product_id, quantity, total_amount)
VALUES
    ('2023-01-01', 1, 1, 3, 32.97),
    ('2023-01-02', 2, 2, 2, 39.98),
    ('2023-01-03', 1, 3, 4, 63.96);

INSERT INTO integrations (customer_id, integration_type, is_active)
VALUES
    (1, 'Mailchimp', 1),
    (2, 'Salesforce', 1),
    (3, 'Hubspot', 0);

-- 
INSERT INTO integrations (customer_id, integration_type, is_active, created_at)
VALUES
    (1, 'Mailchimp', 0, current_timestamp + interval '7 days'),
    (1, 'Salesforce', 1, current_timestamp + interval '7 days'),
    (2, 'Salesforce', 0, current_timestamp + interval '7 days'),
    (3, 'Hubspot', 1, current_timestamp + interval '7 days'),
    (1, 'Mailchimp', 1, current_timestamp + interval '14 days'),
    (2, 'Salesforce', 1, current_timestamp + interval '14 days'),
    (3, 'Hubspot', 0, current_timestamp + interval '14 days'),
    (1, 'Salesforce', 0, current_timestamp + interval '21 days');

INSERT INTO invoices (customer_id, sale_id)
VALUES 
    (1, 1),
    (2, 2),
    (1, 3);

INSERT INTO payments (amount, payment_type, payment_type_info, invoice_id)
VALUES 
    (32.97, 'Cash', NULL, 1),
    (39.98, 'Credit Card', '4436', 2),
    (3.96, 'Gift Card', 'G42423241', 3),
    (60, 'Cash', NULL, 3);

INSERT INTO orders (external_data)
VALUES
    ('{"id": 1, "source": {"address": "123 Wells Way", "store": "Walgreens", "state": "IL", "zip_code": 60601, "transaction_timestamp": "2023-09-17 20:00:00.000000"}, "sale_id": 4}');