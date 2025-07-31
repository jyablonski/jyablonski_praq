{# https://platform.stratascratch.com/coding/10547-actor-rating-difference-analysis?code_type=1

You are given a dataset of actors and the films they have been involved in, including each
film's release date and rating. For each actor, calculate the difference between the
rating of their most recent film and their average rating across all previous films (the average rating excludes the most recent one).

Return a list of actors along with their average lifetime rating, the rating of their
most recent film, and the difference between the two ratings. If an actor has only one
film, return 0 for the difference and their only film's rating for both the average and latest rating fields. #}

-- build a cte of all movies ranked for each actor by release_date desc
with all_actor_ranked_movies as (
    select
        actor_name,
        film_title,
        release_date,
        film_rating,
        row_number() over (partition by actor_name order by release_date desc) as film_rank
    from actor_rating_shift
),

-- then grab the most recent film rating for each actor
most_recent_rating as (
    select
        actor_name,
        film_rating as latest_rating
    from all_actor_ranked_movies
    where film_rank = 1
),

-- then calculate the avg film rating for each actor, excluding that most recent film
non_most_recent_rating_agg as (
    select
        actor_name,
        avg(film_rating) as avg_rating
    from all_actor_ranked_movies
    where film_rank != 1
    group by actor_name
)

-- then join them together, and do some coalesce shit based on the instructions
-- you cant re-reference the initial coalesce in the same statement, you ahve to copy paste the entire thing
-- again or just make another cte
select
    most_recent_rating.actor_name,
    coalesce(non_most_recent_rating_agg.avg_rating, most_recent_rating.latest_rating) as avg_rating,
    most_recent_rating.latest_rating,
    (most_recent_rating.latest_rating - coalesce(non_most_recent_rating_agg.avg_rating, most_recent_rating.latest_rating)) as rating_difference
from most_recent_rating
left join non_most_recent_rating_agg
    on most_recent_rating.actor_name = non_most_recent_rating_agg.actor_name

