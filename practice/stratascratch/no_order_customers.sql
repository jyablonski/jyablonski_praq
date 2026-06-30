/* https://platform.stratascratch.com/coding/10142-no-order-customers?code_type=1

Identify customers who did not place an order between 2019-02-01 and 2019-03-01.

Include:

•    Customers who placed orders only outside this date range.
•    Customers who never placed any orders.

Output the customers' first names. */

/* https://platform.stratascratch.com/coding/10142-no-order-customers?code_type=1

Identify customers who did not place an order between 2019-02-01 and 2019-03-01.

Include:

-    Customers who placed orders only outside this date range.
-    Customers who never placed any orders.

Output the customers' first names. */

-- just make a case when statement to track each customer and if they made an order between
-- the provided date range
with all_customer_orders as (
    select
        orders.cust_id,
        case
            when order_date >= '2019-02-01' and order_date <= '2019-03-01' then 1 else 0
        end as had_feb_2019_order
    from orders
    inner join customers
        on orders.cust_id = customers.id
    
)

-- then pull from the customers table, and pull all customer ids that didnt have a feb 2019 order
-- this actually is the right answer, but i didnt have to check for customers who never placed any orders.
-- fuck em
select distinct
    first_name
from customers
where id not in (
    select cust_id from all_customer_orders where had_feb_2019_order = 1
)