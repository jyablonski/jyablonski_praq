{# https://platform.stratascratch.com/coding/10046-top-5-states-with-5-star-businesses?code_type=1

Find the top 5 states with the most 5 star businesses. Output the state name along with the
number of 5-star businesses and order records by the number of 5-star businesses in descending
order. In case there are ties in the number of businesses, return all the unique states. If
two states have the same result, sort them in alphabetical order.
 #}

with five_star_businesses_by_state as (
    select
        state,
        count(*) as n_businesses
    from yelp_business
    where stars = 5
    group by state
),

states_ranked as (
    select
        state,
        n_businesses,
        dense_rank() over (order by n_businesses desc) as state_rank
    from five_star_businesses_by_state
)

select
    state,
    n_businesses
from states_ranked
where state_rank <= 5
order by
    n_businesses desc,
    state