-- https://platform.stratascratch.com/coding/9632-host-popularity-rental-prices?code_type=1

/* You are given a table named airbnb_host_searches that contains data for rental property searches made by users. Determine the minimum, average, and maximum rental prices for each popularity-rating bucket. A popularity-rating bucket should be assigned to every record based on its number_of_reviews (see rules below).

The host’s popularity rating is defined as below:
•   0 reviews: "New"
•   1 to 5 reviews: "Rising"
•   6 to 15 reviews: "Trending Up"
•   16 to 40 reviews: "Popular"
•   More than 40 reviews: "Hot"

Tip: The id column in the table refers to the search ID.

Output host popularity rating and their minimum, average and maximum rental prices. Order the solution by the minimum price. */

-- sigh. terrible question, no idea why the table is for searches and then has duplicate records for # of reviews

with search_buckets as (
    select
        id,
        price,
        case
            when number_of_reviews = 0 then 'New'
            when number_of_reviews between 1 and 5 then 'Rising'
            when number_of_reviews between 6 and 15 then 'Trending Up'
            when number_of_reviews between 16 and 40 then 'Popular'
            else 'Hot'
        end as host_popularity
    from airbnb_host_searches
)

select
    host_popularity,
    min(price) as min_price,
    avg(price) as avg_price,
    max(price) as max_price
from search_buckets
group by host_popularity
order by min(price)