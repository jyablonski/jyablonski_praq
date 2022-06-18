-- top 3 and bottom 3
with players as (
    select *
    from {{ ref('prod_scorers') }}
    where season_avg_ppg >= 5
),

top_3 as (
    select
        player,
        season_avg_ppg,
        'top 3' as type
    from players
    order by season_avg_ppg desc
    limit 3
),

bot_3 as (
    select
        player,
        season_avg_ppg,
        'bot 3' as type
    from players
    order by season_avg_ppg
    limit 3
)

select *
from top_3
union
select *
from bot_3


-- day over day change with LAG
with stat as (
    select 
        player,
        date,
        pts,
        LAG(pts) over (partition by player order by date) as prev_day_pts,
        round(pts / LAG(pts) over (partition by player order by date), 3) * 100 as dod_pct_change
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry'
)

select *
from stat

-- using date between - which is inclusive both ways
with stat as (
    select 
        player,
        date,
        SUM(pts) as sum_pts
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry' and date between '2021-10-19' AND '2021-11-03'
    group by player, date
    
)

select *
from stat

-- ALL 3 RANK FUNCTIONS
with stat as (
    select 
        player,
        date,
        pts,
        row_number() over(partition by player order by pts desc) as row_number_rank, -- never skips
        RANK() OVER (partition by player order by pts desc) as rank_rank,            -- values can have same rank if duplicate, but skips next value if there's a duplicate
        DENSE_RANK() over (partition by player order by pts desc) as dense_rank      -- values can have same rank if duplicate, but never skip the next value
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry' and date between '2021-10-19' AND '2021-12-31'
    
)

select *
from stat

-- cumulative sum
with stat as (
    select 
        player,
        date,
        pts,
        sum(pts) over (partition by player) as cum_sum_pts_agg,           -- this will just return a total raw aggregate
        sum(pts) over (partition by player order by date) as cum_sum_pts, -- this will give a row level running total for cumulative sum
        row_number() over(partition by player order by pts desc) as row_number_rank,
        RANK() OVER (partition by player order by pts desc) as rank_rank,
        DENSE_RANK() over (partition by player order by pts desc) as dense_rank
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry' and date between '2021-10-19' AND '2021-12-31'
    
)

select *
from stat

-- find the first game date where x and y players broke 800 pts in the season
with stat as (
    select 
        player,
        date,
        pts,
        sum(pts) over (partition by player order by date) as cum_sum_pts,
        row_number() over(partition by player order by pts desc) as row_number_rank,
        RANK() OVER (partition by player order by pts desc) as rank_rank,
        DENSE_RANK() over (partition by player order by pts desc) as dense_rank,
        800 - sum(pts) over (partition by player order by date) as closest_value
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player in ('Stephen Curry', 'Kevin Durant') and date between '2021-10-19' AND '2021-12-31'
    
),

-- find the first negative value (which willbe the max value in this list after filtering out positives)
max_cte as (
    select 
        player,
        max(closest_value) as closest_value
    from stat
    where closest_value < 0  
    group by player
)

select 
    player,
    date
from stat
inner join max_cte using (player, closest_value)