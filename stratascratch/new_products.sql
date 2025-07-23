-- https://platform.stratascratch.com/coding/10318-new-products?code_type=1
{# Calculate the net change in the number of products launched by companies in 2020 compared to 2019. Your output should include the company names and the net difference.
(Net difference = Number of products launched in 2020 - The number launched in 2019.)

 #}

with company_counts_2019 as (
    select
        company_name,
        count(*) as yearly_count
    from car_launches
    where year in (2019)
    group by 
        company_name
),


company_counts_2020 as (
    select
        company_name,
        count(*) as yearly_count
    from car_launches
    where year in (2020)
    group by 
        company_name
)

select
    coalesce(company_counts_2019.company_name, company_counts_2020.company_name) as company_name,
    coalesce(company_counts_2019.yearly_count, 0) - coalesce(company_counts_2020.yearly_count, 0) as net_change
from company_counts_2019
full outer join company_counts_2020
    on company_counts_2019.company_name = company_counts_2020.company_name