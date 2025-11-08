/* https://platform.stratascratch.com/coding/10134-spam-posts?code_type=1

Calculate the percentage of spam posts in all viewed posts by day. A post is considered a spam
if a string "spam" is inside keywords of the post. Note that the facebook_posts table stores
all posts posted by users. The facebook_post_views table is an action table denoting if a
user has viewed a post. */

-- decent problem. have to do the join to connect user views w/ post, then create
-- a flag if the post was considered a spam post or then
with all_views_detailed as (
    select
        facebook_posts.post_id,
        facebook_posts.post_date,
        facebook_post_views.viewer_id,
        case
            when facebook_posts.post_keywords like '%spam%' then 1 else 0
        end as is_spam_post
    from facebook_posts
    inner join facebook_post_views
        on facebook_posts.post_id = facebook_post_views.post_id
)

-- then do some dipshit 1.0 math so postgres can do the divison properly
select
    post_date,
    (1.0 * sum(is_spam_post)) / (1.0 * count(*))* 100 as spam_share
from all_views_detailed
group by post_date
order by post_date desc