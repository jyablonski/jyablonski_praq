{# https://platform.stratascratch.com/coding/2029-the-most-popular-client_id-among-users-using-video-and-voice-calls?code_type=1

Select the most popular client_id based on the number of users who individually have
at least 50% of their events from the following list: 'video call received',
'video call sent', 'voice call received', 'voice call sent'.
 #}

-- build a cte of total event count and total valid event count for each user_id
with user_event_counts as (
    select
        user_id,
        sum(case when event_type in ('video call received', 'video call sent', 'voice call received', 'voice call sent') then 1 else 0 end) as count_valid_events,
        count(*) as count_events
    from fact_events
    group by user_id

),

-- then only select user_id that have a pct_total valid events of >= 50%
-- the 1.0 is needed for proper division, because both columns are integers
select_users as (

    select
        user_id
    from user_event_counts
    where round(count_valid_events * 1.0 / count_events, 3) >= 0.5
),

-- then join fact_events back onto those select user_ids so that we can do a group by
-- count for client_id
client_id_count as (
    select
        client_id,
        count(*) as num_records
    from select_users
    inner join fact_events
        on select_users.user_id = fact_events.user_id
    group by client_id

)

-- then just select the client_id with the highest count`
select
    client_id
from client_id_count
order by num_records desc
limit 1