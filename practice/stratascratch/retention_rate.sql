{# https://platform.stratascratch.com/coding/2053-retention-rate?code_type=1
You are given a dataset that tracks user activity. The dataset includes information about the date of
user activity, the account_id associated with the activity, and the user_id of the user performing the
activity. Each row in the dataset represents a user’s activity on a specific date for a particular account_id.


Your task is to calculate the monthly retention rate for users for each account_id for December 2020
and January 2021. The retention rate is defined as the percentage of users active in a given month who have activity in any future month.


For instance, a user is considered retained for December 2020 if they have activity in December 2020
and any subsequent month (e.g., January 2021 or later). Similarly, a user is retained for January 2021 
if they have activity in January 2021 and any later month (e.g., February 2021 or later).


The final output should include the account_id and the ratio of the retention rate in January 2021
to the retention rate in December 2020 for each account_id. If there are no users retained in December 2020,
the retention rate ratio should be set to 0. #}

with monthly_users as (
    select
        account_id,
        user_id,
        -- this spits out the month as the first day of the month, like a date of `2021-12-26` would become
        -- `2021-12-01` as the activity month
        date_trunc('month', record_date) as activity_month 
    from sf_events
    where
        record_date >= '2020-12-01'
        and record_date <='2021-12-31'
    group by
        account_id,
        user_id,
        date_trunc('month', record_date)
),

user_activity_summary as (
    select
        account_id,
        user_id,
        min(activity_month) as first_month,
        max(activity_month) as last_month,
        -- Flag users active in Dec 2020 and Jan 2021
        max(case when activity_month = '2020-12-01' then 1 else 0 end) as active_dec_2020,
        max(case when activity_month = '2021-01-01' then 1 else 0 end) as active_jan_2021
    from monthly_users
    group by
        account_id,
        user_id
),

retention_calc as (
    select
        account_id,
        -- December 2020 metrics
        sum(active_dec_2020) as dec_total_users,
        sum(case when active_dec_2020 = 1 and last_month >= '2021-01-01' then 1 else 0 end) as dec_retained_users,
        
        -- January 2021 metrics  
        sum(active_jan_2021) as jan_total_users,
        sum(case when active_jan_2021 = 1 and last_month >= '2021-02-01' then 1 else 0 end) as jan_retained_users
    from user_activity_summary
    group by account_id
)

select
    account_id,
    case
        when dec_total_users = 0 or dec_retained_users = 0 then 0
        else (jan_retained_users * 100.0 / jan_total_users) / (dec_retained_users * 100.0 / dec_total_users)
    end as retention_rate_ratio
from retention_calc
order by account_id