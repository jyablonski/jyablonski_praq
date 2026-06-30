-- find ALL the players from yesterday that WERE / WERENT in the top 20 list
-- i find this much more readable to use CTEs than keeping the complex where filter logic in the final select statements
with top_20_scorers as (
    select player, 'top20' as top20
    from {{ ref('prod_scorers') }}
    where season_avg_ppg >= 20
),

players_yesterday as (
    select player
    from {{ ref('prod_recent_games_players') }}
)

-- method 1)
select player
from players_yesterday
where player in (select player from top_20_scorers) -- where player is in the list players in top_20_scorers

-- method 2)
select 
    p.player
from players_yesterday p
left join top_20_scorers t using (player)
where t.player IS NOT NULL -- where the top 20 scorers player IS NOT NULL or IS NULL