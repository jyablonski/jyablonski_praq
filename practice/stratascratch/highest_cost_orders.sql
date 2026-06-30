-- https://platform.stratascratch.com/coding/9915-highest-cost-orders?code_type=1

{# Find the customers with the highest daily total order cost between 2019-02-01 and 2019-05-01.
If a customer had more than one order on a certain day, sum the order costs on a daily basis. Output each customer's first name, total cost of their items, and the date.


For simplicity, you can assume that every first name in the dataset is unique.
 #}


with daily_order_cost as (
    select
        customers.first_name,
        orders.order_date,
        sum(orders.total_order_cost) as max_cost
    from orders
    left join customers on
        customers.id = orders.cust_id
    where orders.order_date between '2019-02-01' and '2019-05-01'
    group by
        customers.first_name,
        orders.order_date
)


select
    first_name,
    order_date,
    max_cost
from daily_order_cost 
order by max_cost desc
limit 2
