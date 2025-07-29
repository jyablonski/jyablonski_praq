-- https://platform.stratascratch.com/coding/9782-customer-revenue-in-march?code_type=1

{# Calculate the total revenue from each customer in March 2019. Include only customers who were active in March 2019.
An active user is a customer who made at least one transaction in March 2019.


Output the revenue along with the customer id and sort the results based on the revenue in descending order. #}

-- whjat the fuck was this man
select
    cust_id,
    sum(total_order_cost) as total_revenue
from orders
where order_date between '2019-03-01' and '2019-03-31'
group by cust_id
order by sum(total_order_cost) desc