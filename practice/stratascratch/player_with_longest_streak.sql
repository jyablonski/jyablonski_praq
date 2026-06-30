{# https://platform.stratascratch.com/coding/2059-player-with-longest-streak?code_type=1

You are given a table of tennis players and their matches that they could either win (W) or lose (L).
Find the longest streak of wins. A streak is a set of consecutive won matches of one player.
The streak ends once a player loses their next match. Output the ID of the player or players and the length of the streak. #}

-- to track win streaks, generate a cumulative sum loss count 
with player_loss_count as (
    select
        player_id,
        match_date,
        match_result,
        sum(case when match_result = 'L' then 1 else 0 end) over (partition by player_id order by match_date) as loss_count
    from players_results
),

-- then count the number of rows with match_result = `W` and group by
-- player_id and loss_count. this will give us the number of wins they had in a row
-- without a loss
win_groups as (
    select
        player_id,
        count(*) as streak_length
    from player_loss_count
    where match_result = 'W'
    group by
        player_id,
        loss_count
),

-- then select the max from the dataset
max_winstreaks as (
    select max(streak_length) as max_win_length
    from win_groups
)

-- and inner join it that value back onto the cte with player_id
select
    player_id,
    streak_length
from win_groups
inner join max_winstreaks
    on win_groups.streak_length = max_winstreaks.