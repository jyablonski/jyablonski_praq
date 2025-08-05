{# https://platform.stratascratch.com/coding/2054-consecutive-days?code_type=1

Find all the users who were active for 3 consecutive days or more.
 #}

-- we're only interested in finding one row per user that proves they had
-- 3 consecutive days of activity.

-- get the previous and next activity dates
-- for each user using LAG and LEAD window functions.
with user_record_dates as (
    select
        user_id,
        record_date,
        lag(record_date) over (partition by user_id order by record_date) as lag_record_date,
        lead(record_date) over (partition by user_id order by record_date) as lead_record_date
    from sf_events
)


-- then ind users who were active for 3 consecutive days.
-- if the current record_date is surrounded by dates exactly one day before and after,
-- it means the user was active for 3 consecutive days (lag, current, lead).
select user_id
from user_record_dates
where
    lag_record_date = record_date - 1
    and lead_record_date = record_date + 1