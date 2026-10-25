-- Run after setup_poc.sql, using the same trial user. Execute the commented denial/Agent checks individually.
-- USE ROLE alone is insufficient when other assigned roles are active: keep secondary roles disabled throughout.
USE ROLE ACCOUNTADMIN;
USE SECONDARY ROLES NONE;
USE WAREHOUSE AGENTIC_ACCESS_POC_WH;

-- The setup already assigns all three POC roles to this user. These show membership and the combined role's inheritance.
-- OAuth uses its authorized primary role with secondary roles disabled; other assigned roles remain inactive.
SHOW GRANTS;
SHOW GRANTS TO ROLE ROLE_ALL_ANALYTICS_POC;

-- Independent source baseline: 10 completed orders, USD 2,000 revenue, 22 units, USD 200 AOV, 5 purchasing customers.
-- The unfiltered data has 12 orders worth USD 2,250: cancelled USD 100 and refunded USD 150 must be excluded.
SELECT
    COUNT(*) AS COMPLETED_ORDERS,
    SUM(QUANTITY * UNIT_PRICE) AS REVENUE,
    SUM(QUANTITY) AS UNITS_SOLD,
    AVG(QUANTITY * UNIT_PRICE) AS AVERAGE_ORDER_VALUE,
    COUNT(DISTINCT CUSTOMER_ID) AS PURCHASING_CUSTOMERS
FROM AGENTIC_ACCESS_POC.POC_DATA.DUMMY_SALES
WHERE ORDER_STATUS = 'completed';

USE ROLE ROLE_SALES_ANALYTICS_POC;
SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();

-- Expected: ORDER_COUNT=12, COMPLETED_ORDERS=10, REVENUE=2000, UNITS_SOLD=22, AVERAGE_ORDER_VALUE=200, PURCHASING_CUSTOMERS=5.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    METRICS sales.order_count, sales.completed_orders, sales.revenue,
            sales.units_sold, sales.average_order_value, sales.purchasing_customers
);

-- September: 5 completed orders, revenue=200+150+300+100+250=1000, units=9, AOV=200, purchasing customers=3.
-- October: 5 completed orders, revenue=400+300+150+100+50=1000, units=13, AOV=200, purchasing customers=4.
-- Purchasing customers across both months is 5, not 3+4=7, because customers can purchase in both months.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    DIMENSIONS sales.order_month
    METRICS sales.completed_orders, sales.revenue, sales.units_sold,
            sales.average_order_value, sales.purchasing_customers
)
ORDER BY ORDER_MONTH;

-- Electronics: revenue=1250, completed orders=5, units=13, AOV=250.
-- Home: revenue=750, completed orders=5, units=9, AOV=150.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    DIMENSIONS sales.product_category
    METRICS sales.revenue, sales.completed_orders, sales.units_sold, sales.average_order_value
)
ORDER BY PRODUCT_CATEGORY;

-- North: revenue=1000, completed orders=4, AOV=250.
-- South: revenue=650, completed orders=4, AOV=162.50.
-- West: revenue=350, completed orders=2, AOV=175.
-- Overall AOV=2000/10=200; averaging these three regional AOVs would be incorrect.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    DIMENSIONS sales.sales_region
    METRICS sales.revenue, sales.completed_orders, sales.average_order_value
)
ORDER BY SALES_REGION;

-- Expected: September revenue=1000. The filter is inside SEMANTIC_VIEW so it applies before aggregation.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    METRICS sales.revenue
    WHERE sales.order_date >= '2026-09-01'::DATE AND sales.order_date < '2026-10-01'::DATE
);

-- Cancelled and refunded: one order each, revenue=0, completed orders=0, units=0, AOV=NULL.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_SALES
    DIMENSIONS sales.order_status
    METRICS sales.order_count, sales.revenue, sales.completed_orders, sales.units_sold, sales.average_order_value
    WHERE sales.order_status IN ('cancelled', 'refunded')
)
ORDER BY ORDER_STATUS;

-- Run these separately while ROLE_SALES_ANALYTICS_POC is active. BOTH must fail with an authorization/object-access error.
/*
USE ROLE ROLE_SALES_ANALYTICS_POC;
USE SECONDARY ROLES NONE;
SELECT * FROM SEMANTIC_VIEW(AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS METRICS customers.customer_count);
SELECT COUNT(*) FROM AGENTIC_ACCESS_POC.POC_DATA.DUMMY_CUSTOMERS;
*/

-- Optional live Agent check: consumes AI credits. Expected sales answer=USD 1000 for September 2026.
-- Then ask the same Agent for registered customer count: expect an access limitation, never a guessed count.
/*
USE ROLE ROLE_SALES_ANALYTICS_POC;
USE SECONDARY ROLES NONE;
SELECT TRY_PARSE_JSON(SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
    'AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC',
    $${"stream":false,"messages":[{"role":"user","content":[{"type":"text","text":"What was completed sales revenue from September 1 through September 30, 2026?"}]}]}$$
)) AS AGENT_RESPONSE;

SELECT TRY_PARSE_JSON(SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
    'AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC',
    $${"stream":false,"messages":[{"role":"user","content":[{"type":"text","text":"How many registered customers are in the customers domain?"}]}]}$$
)) AS AGENT_RESPONSE;
*/

USE ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();

-- Expected: 6 registered customers, including Fay, who has no orders.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS
    METRICS customers.customer_count
);

-- Expected: Enterprise=3 and SMB=3.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS
    DIMENSIONS customers.customer_segment
    METRICS customers.customer_count
)
ORDER BY CUSTOMER_SEGMENT;

-- Expected: North=2, South=2, West=2.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS
    DIMENSIONS customers.customer_region
    METRICS customers.customer_count
)
ORDER BY CUSTOMER_REGION;

-- Expected: September signups=3 and October signups=3; these are registration cohorts, not monthly buyers.
SELECT *
FROM SEMANTIC_VIEW(
    AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS
    DIMENSIONS customers.signup_month
    METRICS customers.customer_count
)
ORDER BY SIGNUP_MONTH;

-- Run these separately while ROLE_CUSTOMERS_ANALYTICS_POC is active. BOTH must fail.
/*
USE ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
USE SECONDARY ROLES NONE;
SELECT * FROM SEMANTIC_VIEW(AGENTIC_ACCESS_POC.POC_DATA.SV_SALES METRICS sales.revenue);
SELECT COUNT(*) FROM AGENTIC_ACCESS_POC.POC_DATA.DUMMY_SALES;
*/

-- Optional live Agent check: expected customer answer=6. The sales question must instead report an access limitation.
/*
USE ROLE ROLE_CUSTOMERS_ANALYTICS_POC;
USE SECONDARY ROLES NONE;
SELECT TRY_PARSE_JSON(SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
    'AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC',
    $${"stream":false,"messages":[{"role":"user","content":[{"type":"text","text":"How many registered customers are in the customers domain?"}]}]}$$
)) AS AGENT_RESPONSE;

SELECT TRY_PARSE_JSON(SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
    'AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC',
    $${"stream":false,"messages":[{"role":"user","content":[{"type":"text","text":"What was completed sales revenue from September 1 through September 30, 2026?"}]}]}$$
)) AS AGENT_RESPONSE;
*/

USE ROLE ROLE_ALL_ANALYTICS_POC;
SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();

-- Both must succeed through inherited grants: revenue=2000 and registered customers=6.
SELECT *
FROM SEMANTIC_VIEW(AGENTIC_ACCESS_POC.POC_DATA.SV_SALES METRICS sales.revenue);

SELECT *
FROM SEMANTIC_VIEW(AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS METRICS customers.customer_count);

-- Optional live Agent check: expected revenue=2000 and registered customers=6; no inaccessible-domain warning.
/*
USE ROLE ROLE_ALL_ANALYTICS_POC;
USE SECONDARY ROLES NONE;
SELECT TRY_PARSE_JSON(SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
    'AGENTIC_ACCESS_POC.ANALYTICS_POC.ANALYTICS_AGENT_POC',
    $${"stream":false,"messages":[{"role":"user","content":[{"type":"text","text":"Report completed sales revenue over all fixture dates and the total registered customer count as two separate metrics."}]}]}$$
)) AS AGENT_RESPONSE;
*/
