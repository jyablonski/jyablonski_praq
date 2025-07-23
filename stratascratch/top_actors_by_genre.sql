-- https://platform.stratascratch.com/coding/10548-top-actor-ratings-by-genre?code_type=1

{# Find the top actors based on their average movie rating within the genre they appear in most frequently.
•  For each actor, determine their most frequent genre (i.e., the one they’ve appeared in the most).
•   If there is a tie in genre count, select the genre where the actor has the highest average rating.
•   If there is still a tie in both count and rating, include all tied genres for that actor.


Rank all resulting actor + genre pairs in descending order by their average movie rating.
•  Return all pairs that fall within the top 3 ranks (not simply the top 3 rows), including ties.
•  Do not skip rank numbers — for example, if two actors are tied at rank 1, the next rank is 2 (not 3). #}

-- generate genre counts and average movie ratings in each genre for each actor
with actor_genre_counts as (
    select
        actor_name,
        genre,
        count(*) as genre_count,
        avg(movie_rating) as avg_rating
    from top_actors_rating
    group by
        actor_name,
        genre
),

-- generate ranks for each actor based on their genre counts and average ratings
actor_genre_ranked as (
    select
        *,
        rank() over (partition by actor_name order by genre_count desc, avg_rating desc) as actor_rnk
    from actor_genre_counts

),

-- filter each actor's top genre and then make dense rank from that list based on average rating
all_pairs_ranked as (
    select
        actor_name,
        genre,
        avg_rating,
        dense_rank() over (order by avg_rating desc) as dense_rnk
    from actor_genre_ranked
    where actor_rnk = 1
)

-- return the top 3 actor + genre dense rank pairs
select
    actor_name,
    genre,
    avg_rating,
    dense_rnk
from all_pairs_ranked
where dense_rnk <= 3