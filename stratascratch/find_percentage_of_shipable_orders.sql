/* https://platform.stratascratch.com/coding/10090-find-the-percentage-of-shipable-orders?code_type=1

Find the percentage of shipable orders.
Consider an order is shipable if the customer's address is known. */

-- build a cte at the right grain w/ a simple 0 or 1 for whether the address for the
-- order is known
with orders_enriched as (
    select
        orders.id,
        case
            when customers.address is not null then 1
            else 0
        end as is_address_known
    from orders
    inner join customers
        on orders.cust_id = customers.id
)

-- then perform the calc. the * 1.0 is necessary because of integer division,
-- without it the result is 0. and then we multiply by 100 because they expect
-- the answer to be between 0 and 100, not been 0 and 1.
select (sum(is_address_known) * 1.0 / count(*)) * 100 as percent_shipable
from orders_enriched