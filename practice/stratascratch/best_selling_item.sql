/* https://platform.stratascratch.com/coding/10172-best-selling-item?code_type=1

Find the best-selling item for each month (no need to separate months by year). The
best-selling item is determined by the highest total sales amount, calculated as:
total_paid = unitprice * quantity. Output the month, description of the item, and the total amount paid. */

-- extract month in the form of an integer `1` `2` etc from invoicedate, and calculate the sales amt
-- for each item
with month_total_sales as (
    select
        invoiceno,
        date_part('month', invoicedate) as month,
        description,
        unitprice * quantity as invoice_sum
    from online_retail
),

-- then do aggregations and do the window function to do the ranking
month_sales_ranked as (
    select
        month,
        description,
        sum(invoice_sum) as total_paid,
        row_number() over(partition by month order by sum(invoice_sum) desc) as rn
    from month_total_sales
    group by
        month,
        description
)

-- final select
select
    month,
    description,
    total_paid
from month_sales_ranked
where rn = 1