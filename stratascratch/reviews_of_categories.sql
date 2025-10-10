/* https://platform.stratascratch.com/coding/10049-reviews-of-categories?code_type=1

Calculate number of reviews for every business category. Output the category along with the
total number of reviews. Order by total reviews in descending order. */

-- categories comes in w/ values like `Auto Detailing;Automotive`
-- so you have to str split that by `;` into an array of strings,
-- and then unnest that array of strings into 1 row for every category
with business_categories as (
    select
        unnest(string_to_array(categories, ';')) as category,
        sum(review_count) as review_cnt
    from yelp_business
    group by 1
)

select
    category,
    review_cnt
from business_categories
order by review_cnt desc