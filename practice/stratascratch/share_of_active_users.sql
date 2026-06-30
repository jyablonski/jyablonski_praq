/* https://platform.stratascratch.com/coding/2005-share-of-active-users?code_type=1

Calculate the percentage of users who are both from the US and have an 'open' status, as
indicated in the fb_active_users table. */

with users_enriched as (
    select
        user_id,
        case when
            status = 'open' and country = 'USA' then 1
            else 0
        end as is_criteria_met
    from fb_active_users
),

aggregations as (
    select
        is_criteria_met,
        count(*) / sum(count(*)) over () as us_active_share
    from users_enriched
group by is_criteria_met
)

select
    us_active_share * 100 as us_active_share
from aggregations
where is_criteria_met = 1;


-- can also do this
SELECT 
    COUNT(*) FILTER (WHERE status = 'open' AND country = 'USA') * 100.0 / COUNT(*) AS us_active_share
FROM fb_active_users

-- or  this
SELECT 
    SUM(CASE WHEN status = 'open' AND country = 'USA' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS us_active_share
FROM fb_active_users