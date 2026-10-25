-- Run once, top to bottom, in a Snowsight SQL worksheet on the trial account.
-- This is the standalone SQL alternative to analytics_mcp_poc.tf; both use the same account-role names.
-- CREATE statements deliberately fail on existing objects rather than replace data or reuse old grants. Stop on any error.
-- After setup, run verify_poc.sql. No existing user defaults or account-wide AI settings are changed.

USE ROLE ACCOUNTADMIN;
USE SECONDARY ROLES NONE;

CREATE DATABASE AGENTIC_ACCESS_POC;
CREATE SCHEMA AGENTIC_ACCESS_POC.POC_DATA;
CREATE SCHEMA AGENTIC_ACCESS_POC.ANALYTICS_POC;

CREATE WAREHOUSE AGENTIC_ACCESS_POC_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

USE WAREHOUSE AGENTIC_ACCESS_POC_WH;
ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 120;

-- Each order has one product category and one row, so order counts cannot fan out across line items.
-- All money is USD. Cancelled and refunded orders contribute zero revenue and zero completed units/orders.
CREATE TABLE AGENTIC_ACCESS_POC.POC_DATA.DUMMY_SALES (
    ORDER_ID NUMBER(10, 0) NOT NULL,
    CUSTOMER_ID NUMBER(10, 0) NOT NULL,
    ORDER_DATE DATE NOT NULL,
    PRODUCT_CATEGORY VARCHAR NOT NULL,
    REGION VARCHAR NOT NULL,
    QUANTITY NUMBER(10, 0) NOT NULL,
    UNIT_PRICE NUMBER(12, 2) NOT NULL,
    ORDER_STATUS VARCHAR NOT NULL
);

INSERT INTO AGENTIC_ACCESS_POC.POC_DATA.DUMMY_SALES
    (ORDER_ID, CUSTOMER_ID, ORDER_DATE, PRODUCT_CATEGORY, REGION, QUANTITY, UNIT_PRICE, ORDER_STATUS)
VALUES
    (1,  1, '2026-09-02', 'Electronics', 'North', 2, 100.00, 'completed'),
    (2,  2, '2026-09-04', 'Home',        'South', 1, 150.00, 'completed'),
    (3,  3, '2026-09-08', 'Electronics', 'North', 3, 100.00, 'completed'),
    (4,  1, '2026-09-15', 'Home',        'North', 2,  50.00, 'completed'),
    (5,  2, '2026-09-20', 'Home',        'South', 4,  25.00, 'cancelled'),
    (6,  2, '2026-09-25', 'Electronics', 'South', 1, 250.00, 'completed'),
    (7,  3, '2026-10-02', 'Electronics', 'North', 2, 200.00, 'completed'),
    (8,  4, '2026-10-07', 'Home',        'West',  3, 100.00, 'completed'),
    (9,  1, '2026-10-10', 'Electronics', 'North', 1, 150.00, 'refunded'),
    (10, 5, '2026-10-13', 'Home',        'South', 2,  75.00, 'completed'),
    (11, 2, '2026-10-18', 'Electronics', 'South', 5,  20.00, 'completed'),
    (12, 4, '2026-10-20', 'Home',        'West',  1,  50.00, 'completed');

-- Customer 6 has no orders. Registered customers (6) and purchasing customers (5) are different populations.
-- Separate sources let each restricted role read its own domain without gaining the other domain's data.
CREATE TABLE AGENTIC_ACCESS_POC.POC_DATA.DUMMY_CUSTOMERS (
    CUSTOMER_ID NUMBER(10, 0) NOT NULL,
    CUSTOMER_NAME VARCHAR NOT NULL,
    SEGMENT VARCHAR NOT NULL,
    REGION VARCHAR NOT NULL,
    SIGNUP_DATE DATE NOT NULL
);

INSERT INTO AGENTIC_ACCESS_POC.POC_DATA.DUMMY_CUSTOMERS
    (CUSTOMER_ID, CUSTOMER_NAME, SEGMENT, REGION, SIGNUP_DATE)
VALUES
    (1, 'Ada',  'SMB',        'North', '2026-09-01'),
    (2, 'Ben',  'SMB',        'South', '2026-09-03'),
    (3, 'Cara', 'Enterprise', 'North', '2026-09-07'),
    (4, 'Dev',  'Enterprise', 'West',  '2026-10-01'),
    (5, 'Eli',  'SMB',        'South', '2026-10-05'),
    (6, 'Fay',  'Enterprise', 'West',  '2026-10-09');

-- Native YAML keeps the definitions usable by Cortex Analyst and direct semantic SQL.
-- FALSE deploys; TRUE selects CREATE OR ALTER, preserving grants on subsequent definition-only updates.
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
    'AGENTIC_ACCESS_POC.POC_DATA',
    $$
name: SV_SALES
description: Static sales fixture for September and October 2026, in USD. One row per order with one product category. Revenue includes only completed orders; cancelled and refunded orders contribute zero.
tables:
  - name: sales
    description: Sales orders, including completed, cancelled, and refunded orders. Do not join to the customers domain for this POC.
    base_table:
      database: AGENTIC_ACCESS_POC
      schema: POC_DATA
      table: DUMMY_SALES
    primary_key:
      columns: [ORDER_ID]
    dimensions:
      - name: order_id
        expr: ORDER_ID
        data_type: NUMBER(10, 0)
      - name: customer_id
        expr: CUSTOMER_ID
        data_type: NUMBER(10, 0)
      - name: order_date
        expr: ORDER_DATE
        data_type: DATE
      - name: order_month
        expr: DATE_TRUNC('MONTH', ORDER_DATE)
        data_type: DATE
      - name: order_status
        expr: ORDER_STATUS
        data_type: VARCHAR
      - name: product_category
        expr: PRODUCT_CATEGORY
        data_type: VARCHAR
      - name: sales_region
        expr: REGION
        data_type: VARCHAR
    facts:
      - name: order_amount
        expr: QUANTITY * UNIT_PRICE
        data_type: NUMBER(22, 2)
        access_modifier: private_access
      - name: units
        expr: QUANTITY
        data_type: NUMBER(10, 0)
        access_modifier: private_access
    metrics:
      - name: order_count
        description: Count of distinct orders in all statuses, including cancelled and refunded orders.
        expr: COUNT(DISTINCT sales.order_id)
      - name: completed_orders
        description: Count of distinct completed orders only.
        expr: COUNT(DISTINCT IFF(sales.order_status = 'completed', sales.order_id, NULL))
      - name: revenue
        description: Revenue in USD, computed as quantity times unit price for completed orders only. Excludes cancelled and refunded orders.
        synonyms: [sales revenue, completed revenue]
        expr: SUM(IFF(sales.order_status = 'completed', sales.order_amount, 0))
      - name: units_sold
        description: Units from completed orders only.
        expr: SUM(IFF(sales.order_status = 'completed', sales.units, 0))
      - name: average_order_value
        description: Completed revenue divided by completed order count, in USD. NULL when there are no completed orders. Recompute from totals rather than averaging group averages.
        synonyms: [AOV]
        expr: SUM(IFF(sales.order_status = 'completed', sales.order_amount, 0)) / NULLIF(COUNT(DISTINCT IFF(sales.order_status = 'completed', sales.order_id, NULL)), 0)
      - name: purchasing_customers
        description: Distinct customers with a completed order in the requested period. Distinct counts cannot be added across months.
        expr: COUNT(DISTINCT IFF(sales.order_status = 'completed', sales.customer_id, NULL))
    $$,
    FALSE,
    TRUE
);

CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
    'AGENTIC_ACCESS_POC.POC_DATA',
    $$
name: SV_CUSTOMERS
description: Static snapshot of six registered customers, including customers without orders. Signup month is a registration cohort, not an order month. Does not expose sales amounts or order history.
tables:
  - name: customers
    description: One row per registered customer. Do not infer purchasing activity from customer registration.
    base_table:
      database: AGENTIC_ACCESS_POC
      schema: POC_DATA
      table: DUMMY_CUSTOMERS
    primary_key:
      columns: [CUSTOMER_ID]
    dimensions:
      - name: customer_id
        expr: CUSTOMER_ID
        data_type: NUMBER(10, 0)
      - name: customer_segment
        expr: SEGMENT
        data_type: VARCHAR
      - name: customer_region
        expr: REGION
        data_type: VARCHAR
      - name: signup_date
        expr: SIGNUP_DATE
        data_type: DATE
      - name: signup_month
        expr: DATE_TRUNC('MONTH', SIGNUP_DATE)
        data_type: DATE
    metrics:
      - name: customer_count
        description: Distinct registered customers, including customers without orders. When filtered by signup date, counts registrations in that period.
        synonyms: [registered customers, total customers]
        expr: COUNT(DISTINCT customers.customer_id)
    $$,
    FALSE,
    TRUE
);

CREATE ROLE ROLE_SALES_ANALYTICS_POC;
CREATE ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
CREATE ROLE ROLE_ALL_ANALYTICS_POC;

GRANT ROLE ROLE_SALES_ANALYTICS_POC TO ROLE ROLE_ALL_ANALYTICS_POC;
GRANT ROLE ROLE_CUSTOMERS_ANALYTICS_POC TO ROLE ROLE_ALL_ANALYTICS_POC;

GRANT USAGE ON DATABASE AGENTIC_ACCESS_POC TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT USAGE ON DATABASE AGENTIC_ACCESS_POC TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
GRANT USAGE ON SCHEMA AGENTIC_ACCESS_POC.POC_DATA TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT USAGE ON SCHEMA AGENTIC_ACCESS_POC.POC_DATA TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
GRANT USAGE ON SCHEMA AGENTIC_ACCESS_POC.ANALYTICS_POC TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT USAGE ON SCHEMA AGENTIC_ACCESS_POC.ANALYTICS_POC TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
GRANT USAGE ON WAREHOUSE AGENTIC_ACCESS_POC_WH TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT USAGE ON WAREHOUSE AGENTIC_ACCESS_POC_WH TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;

GRANT SELECT ON SEMANTIC VIEW AGENTIC_ACCESS_POC.POC_DATA.SV_SALES TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT SELECT ON SEMANTIC VIEW AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;

-- Agent execution also needs source SELECT; these grants intentionally permit direct reads of the same dummy domain.
GRANT SELECT ON TABLE AGENTIC_ACCESS_POC.POC_DATA.DUMMY_SALES TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT SELECT ON TABLE AGENTIC_ACCESS_POC.POC_DATA.DUMMY_CUSTOMERS TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_AGENT_USER TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_AGENT_USER TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;

-- Assign roles to the signed-in trial user for isolated primary-role tests with secondary roles disabled.
-- This checks role boundaries; separate-user OAuth isolation still needs dedicated identities later.
-- A Scripting variable supports CURRENT_USER(); quoting preserves the stored identifier's case.
EXECUTE IMMEDIATE $$
DECLARE
    poc_user VARCHAR;
BEGIN
    poc_user := '"' || REPLACE(CURRENT_USER(), '"', '""') || '"';
    GRANT ROLE ROLE_SALES_ANALYTICS_POC TO USER IDENTIFIER(:poc_user);
    GRANT ROLE ROLE_CUSTOMERS_ANALYTICS_POC TO USER IDENTIFIER(:poc_user);
    GRANT ROLE ROLE_ALL_ANALYTICS_POC TO USER IDENTIFIER(:poc_user);
    RETURN 'Granted POC roles to ' || poc_user;
END;
$$;

CREATE AGENT AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC
    COMMENT = 'Sales and customers POC with caller-specific domain access'
    PROFILE = '{"display_name": "Analytics POC"}'
    FROM SPECIFICATION
    $$
models:
  orchestration: auto
orchestration:
  tool_not_accessible: accept
  budget:
    seconds: 60
    tokens: 8000
instructions:
  orchestration: Use the sales tool for order and revenue questions and the customers tool for registered-customer questions, subject to caller access. Ask for exact dates when a period is ambiguous. Refuse cross-domain joins and unsupported metrics. Never substitute an accessible domain when the requested domain is inaccessible.
  response: Report the executed result, metric definition, exact dates, and filters. Preserve access warnings and query failures. If a domain is unavailable, say so and do not guess. Treat registered customers and purchasing customers as different populations. The fixtures are static, so do not invent a freshness timestamp.
tools:
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: sales
      description: Completed revenue in USD, order counts, units, average order value, and purchasing customers, grouped by order month, product category, or sales region.
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: customers
      description: Registered customer counts by segment, region, and signup month, including customers without orders. Does not answer revenue or order questions.
tool_resources:
  sales:
    semantic_view: AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    execution_environment:
      type: warehouse
      warehouse: AGENTIC_ACCESS_POC_WH
      query_timeout: 30
  customers:
    semantic_view: AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS
    execution_environment:
      type: warehouse
      warehouse: AGENTIC_ACCESS_POC_WH
      query_timeout: 30
    $$;

CREATE MCP SERVER AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_MCP_POC
    FROM SPECIFICATION
    $$
tools:
  - name: analytics
    title: Analytics POC
    type: CORTEX_AGENT_RUN
    identifier: AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC
    description: Answer aggregate sales and registered-customer questions within the caller's Snowflake role permissions.
    annotations:
      readOnlyHint: true
      destructiveHint: false
      idempotentHint: false
      openWorldHint: false
    $$;

GRANT USAGE ON AGENT AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT USAGE ON AGENT AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
GRANT USAGE ON MCP SERVER AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_MCP_POC TO ROLE ROLE_SALES_ANALYTICS_POC;
GRANT USAGE ON MCP SERVER AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_MCP_POC TO ROLE ROLE_CUSTOMERS_ANALYTICS_POC;

-- All-access inherits exactly the two domain roles; it has no administrative or write privileges from this script.
SHOW SEMANTIC VIEWS IN SCHEMA AGENTIC_ACCESS_POC.POC_DATA;
SHOW AGENTS IN SCHEMA AGENTIC_ACCESS_POC.ANALYTICS_POC;
SHOW MCP SERVERS IN SCHEMA AGENTIC_ACCESS_POC.ANALYTICS_POC;

-- Append this path to the public Snowflake account URL when configuring ChatGPT OAuth:
-- /api/v2/databases/AGENTIC_ACCESS_POC/schemas/ANALYTICS_POC/mcp-servers/ANALYTICS_MCP_POC
-- The ChatGPT OAuth integration is a separate step because its redirect URI must come from the actual connection.
