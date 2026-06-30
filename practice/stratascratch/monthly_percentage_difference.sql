/* https://platform.stratascratch.com/coding/10319-monthly-percentage-difference?code_type=1

Given a table of purchases by date, calculate the month-over-month percentage change in revenue.
The output should include the year-month date (YYYY-MM) and percentage change, rounded to the
2nd decimal point, and sorted from the beginning of the year to the end of the year.
The percentage change column will be populated from the 2nd month forward and can be calculated
as ((this month's revenue - last month's revenue) / last month's revenue)*100. */

-- have to create a table of monthly revenue first
with monthly_revenue as (
    select
        to_char(created_at, 'YYYY-mm') as year_month,
        sum(value) as sum_revenue
    from sf_transactions
    group by 1
    order by 1
),

-- then we can use lag to add on the prev month's revenue onto each month record
prev_monthly_revenue as (
    select
        year_month,
        sum_revenue,
        lag(sum_revenue) over (order by year_month) as prev_month_revenue
    from monthly_revenue
)

-- now that we have both the current month and prev month revenue on the same row, you can 
-- easily do the diff in the requested output format
select
    year_month,
    round(((sum_revenue - prev_month_revenue) / prev_month_revenue) * 100, 2) as revenue_diff_pct
from prev_monthly_revenue
