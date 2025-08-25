{# https://platform.stratascratch.com/coding/2136-customer-tracking?code_type=1

Given the users' sessions logs on a particular day, calculate how many hours each user was active that day.
Note: The session starts when state=1 and ends when state=0.

c001	1	2024-11-26 07:00:00
c001	0	2024-11-26 09:30:00
c001	1	2024-11-26 12:00:00
c001	0	2024-11-26 14:30:00
 #}

-- use lag to track the previous timestamp and generate an `elapsed_time` for each session
-- this would get trickier if the data was messy or if some sessions only had state = 0 or 1, but 
-- works fine for this problem
with user_session_timestamps as (
    select
        cust_id,
        state,
        timestamp - lag(timestamp) over (partition by cust_id order by timestamp) as elapsed_time
    from cust_tracking
)

-- then just group by cust_id, filter on state = 0 to identify the end session events, and calculate
-- total hours
select
    cust_id,
    sum(elapsed_time) / 60 / 60 as total_hours
from user_session_timestamps
where state = 0
group by cust_id
