/* https://platform.stratascratch.com/coding/10141-apple-product-counts?code_type=1

We're analyzing user data to understand how popular Apple devices are among users who have performed
at least one event on the platform. Specifically, we want to measure this popularity across different
languages. Count the number of distinct users using Apple devices —limited to "macbook pro",
"iphone 5s", and "ipad air" — and compare it to the total number of users per language.

Present the results with the language, the number of Apple users, and the total number of users for
each language. Finally, sort the results so that languages with the highest total user count appear
first. */

-- good problem. you have to do the join and then make a case when statement for the qualified users
with events_detailed as (
    select
        playbook_events.user_id,
        playbook_events.occurred_at,
        playbook_users.language,
        case
            when playbook_events.device in ('macbook pro', 'iphone 5s', 'ipad air') then 1
            else 0
        end as is_apple_device
    from playbook_events
    inner join playbook_users
        on playbook_events.user_id = playbook_users.user_id
)

-- then create your aggregations, using another case when statement to only count the distinct user_ids
-- that were on an apple device
select
    language,
    count(distinct case when is_apple_device = 1 then user_id end) as n_apple_users,
    count(distinct user_id) as n_total_users
from events_detailed
group by language