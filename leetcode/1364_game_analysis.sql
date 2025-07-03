{# Table: Activity

+--------------+---------+
| Column Name  | Type    |
+--------------+---------+
| player_id    | int     |
| device_id    | int     |
| event_date   | date    |
| games_played | int     |
+--------------+---------+
(player_id, event_date) is the primary key (combination of columns with unique values) of this table.
This table shows the activity of players of some games.
Each row is a record of a player who logged in and played a number of games (possibly 0) before logging out on someday using some device.

Write a solution to report the fraction of players that logged in again on the day after the day they first logged in, rounded to 2 decimal places. In other words, you need to determine the number of players who logged in on the day immediately following their initial login, and divide it by the number of total players.

The result format is in the following example. #}

 
with min_count as (
    select
        player_id,
        date_add(min(event_date), interval 1 day) as day_after
    from Activity
    group by player_id
),

final as (
    select
        Activity.*,
        day_after,
        day_after = event_date as logged_in_day_after
    from Activity
    left join min_count on Activity.player_id = min_count.player_id
)

select
    round(sum(logged_in_day_after) / count(distinct(player_id)), 2) as fraction
from final