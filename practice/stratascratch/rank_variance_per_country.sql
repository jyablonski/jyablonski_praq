{# https://platform.stratascratch.com/coding/2007-rank-variance-per-country?code_type=1

Compare the total number of comments made by users in each country between December 2019 and January 2020.
For each month, rank countries by total comments using dense ranking (i.e., avoid gaps between ranks) in
descending order. Then, return the names of the countries whose rank improved from December to January. #}

-- shorter solution with conditional aggregations
with monthly_comments as (
    select
        fb_active_users.country,
        sum(case when date_trunc('month', fb_comments_count.created_at) = '2019-12-01' then 1 else 0 end) as dec_comments,
        sum(case when date_trunc('month', fb_comments_count.created_at) = '2020-01-01' then 1 else 0 end) as jan_comments
    from fb_comments_count
    inner join fb_active_users
        on fb_comments_count.user_id = fb_active_users.user_id
    where fb_comments_count.created_at between '2019-12-01' and '2020-01-31'
    group by 1
),

country_rankings as (
    select
        country,
        dense_rank() over (order by dec_comments desc) as dec_rank,
        dense_rank() over (order by jan_comments desc) as jan_rank
    from monthly_comments
    where
        dec_comments > 0
        and jan_comments > 0  -- Only countries active in both months
)

select country
from country_rankings
where jan_rank < dec_rank;

-- longer solution with separate ctes 
with user_comments as (
    select
        date_trunc('month', fb_comments_count.created_at) as month,
        fb_active_users.country,
        count(*) as number_of_comments
    from fb_comments_count
    inner join fb_active_users
        on fb_comments_count.user_id = fb_active_users.user_id
    where fb_comments_count.created_at between '2019-12-01' and '2020-01-31'
    group by
        1,
        2
),

country_rankings as (
    select
        country,
        month,
        number_of_comments,
        dense_rank() over (partition by month order by number_of_comments desc) as country_rank
    from user_comments
),

december_rankings as (
    select
        country,
        country_rank
    from country_rankings
    where month = '2019-12-01'
),

january_rankings as (
    select
        country,
        country_rank
    from country_rankings
    where month = '2020-01-01'
)

select december_rankings.country
from december_rankings
inner join january_rankings
    on december_rankings.country = january_rankings.country
where january_rankings.country_rank < december_rankings.country_rank