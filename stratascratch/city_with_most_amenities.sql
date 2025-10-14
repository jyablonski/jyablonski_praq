/* https://platform.stratascratch.com/coding/9633-city-with-most-amenities?code_type=1

You're given a dataset of searches for properties on Airbnb. For simplicity, let's say
that each search result (i.e., each row) represents a unique host. Find the city with
the most amenities across all their host's properties. Output the name of the city.

1. unnest amenities dictionary of strings to get 1 row for every amenities
2. group by city and count amenities and rank them by count desc
3. return the city with the highest amenities count */

-- trim removes these quotes and {} brackets on each end of the string
-- this is actually irrelevant to the problem because we can still attribute the values
-- to each city without it, but good to know
with amenities_unnested as (
    select
        id,
        city,
        trim(both '"' from unnest(string_to_array(
            trim(both '{}' from amenities), 
            ','
        ))) AS amenity
    from airbnb_search_details
),

amenity_counts as (
    select
        city,
        count(*) as num_amenities,
        row_number() over (order by count(*) desc) as rn
    from amenities_unnested
    group by city

)

select city
from amenity_counts
where rn = 1