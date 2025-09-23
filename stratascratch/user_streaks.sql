{# https://platform.stratascratch.com/coding/2131-user-streaks?code_type=1

Provided a table with user id and the dates they visited the platform, find the top 3 users
with the longest continuous streak of visiting the platform as of August 10, 2022. Output
the user ID and the length of the streak.

In case of a tie, display all users with the top three longest streaks.
 #}

with user_dates as (
    select distinct
        user_id,
        date_visited
    from user_streaks
    where date_visited <= '2022-08-10'  -- Only consider visits up to Aug 10
),

streak_breaks as (
    select
        user_id,
        date_visited,
        case 
            when lag(date_visited) over (partition by user_id order by date_visited) = date_visited - interval '1 day'
            then 0 
            else 1 
        end as is_new_streak
    from user_dates
),

streak_groups as (
    select
        user_id,
        date_visited,
        sum(is_new_streak) over (partition by user_id order by date_visited) as streak_id
    from streak_breaks
),

user_streaks_calculated as (
    select
        user_id,
        streak_id,
        min(date_visited) as streak_start,
        max(date_visited) as streak_end,
        count(*) as streak_length
    from streak_groups
    group by user_id, streak_id
),

-- Find the most recent streak for each user (should be active as of Aug 10)
latest_streaks as (
    select
        user_id,
        streak_length,
        streak_end,
        row_number() over (partition by user_id order by streak_end desc) as rn
    from user_streaks_calculated
),

active_streaks as (
    select
        user_id,
        streak_length
    from latest_streaks
    where rn = 1  -- Get each user's most recent streak
),

ranked_streaks as (
    select
        user_id,
        streak_length,
        dense_rank() over (order by streak_length desc) as rank
    from active_streaks
)

select
    user_id,
    streak_length
from ranked_streaks
where rank <= 3
order by streak_length desc, user_id;