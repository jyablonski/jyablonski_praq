{# Calculate each user's average session time, where a session is defined as the time difference between a
page_load and a page_exit. Assume each user has only one session per day. If there are multiple page_load
or page_exit events on the same day, use only the latest page_load and the earliest page_exit, ensuring
the page_load occurs before the page_exit. Output the user_id and their average session time. #}

-- pretty simple, use this max(case when) syntax to get the latest page_load and earliest page_exit for each user per day
with daily_sessions as (
    select
        user_id,
        date(timestamp) as session_date,
        max(case when action = 'page_load' then timestamp end) as latest_page_load,
        min(case when action = 'page_exit' then timestamp end) as earliest_page_exit
    from facebook_web_log
    group by
        user_id,
        date(timestamp)
),

-- then calculate the session time and only filter for valid sessions according to the criteria given
valid_sessions as (
    select
        user_id,
        timestampdiff(second, latest_page_load, earliest_page_exit) as session_time_sec
    from daily_sessions
    where
        latest_page_load is not null and
        earliest_page_exit is not null and
        latest_page_load < earliest_page_exit
)

-- then finally calculate the average session time for each user
select
    user_id,
    round(avg(session_time_sec), 2) as average_session_time_sec
from valid_sessions
group by
    user_id
