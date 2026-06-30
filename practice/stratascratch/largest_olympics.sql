/* https://platform.stratascratch.com/coding/9942-largest-olympics?code_type=1

Find the Olympics with the highest number of unique athletes. The Olympics game is a
combination of the year and the season, and is found in the games column. Output
the Olympics along with the corresponding number of athletes. The id column uniquely
identifies an athlete. */

-- an athlete can participate in multiple olympic events in the same year i guess, so
-- dudupe first
with athletes_deduped as (
    select distinct 
        id,
        year,
        season
    from olympics_athletes_events
),

-- then grab the counts by year and season
olympic_athlete_counts as (
    select
        year,
        season,
        count(*) as athletes_count
    from athletes_deduped
    group by
        year,
        season
),

-- and then build the final dataset in the format they requested,
-- and only grab the highest row count record
athlete_counts_final as (
    select
        concat(year, ' ', season) as games,
        athletes_count,
        row_number() over(order by athletes_count desc) as rn
    from olympic_athlete_counts
)

select
    games,
    athletes_count
from athlete_counts_final
where rn = 1