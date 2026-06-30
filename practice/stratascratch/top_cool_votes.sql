/* https://platform.stratascratch.com/coding/10060-top-cool-votes?code_type=1

Find the review_text that received the highest number of  cool votes.
Output the business name along with the review text with the highest number of cool votes. */

-- same fucking dumbass shit, just use dense rank to not get any ties
with cool_votes as (
    select
        business_name,
        review_text,
        cool,
        dense_rank() over (order by cool desc) as rn
    from yelp_reviews
)

-- no idea why this is a medium fuck oiff
select
    business_name,
    review_text
from cool_votes
where rn = 1