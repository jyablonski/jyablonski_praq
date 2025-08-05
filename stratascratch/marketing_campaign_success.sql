{# https://platform.stratascratch.com/coding/514-marketing-campaign-success-advanced?code_type=1

You have the marketing_campaign table, which records in-app purchases by users. Users making
their first in-app purchase enter a marketing campaign, where they see call-to-actions for
more purchases. Find how many users made additional purchases due to the campaign's success.

The campaign starts one day after the first purchase. Users with only one or multiple
purchases on the first day do not count, nor do users who later buy only the same products
from their first day. #}

with user_first_purchase_dates as (
    select
        user_id,
        min(created_at) as first_purchase_date
    from marketing_campaign
    group by user_id
),

user_first_purchase as (
    select
        user_first_purchase_dates.user_id,
        marketing_campaign.product_id
    from user_first_purchase_dates
    inner join marketing_campaign
        on user_first_purchase_dates.user_id = marketing_campaign.user_id
        and user_first_purchase_dates.first_purchase_date = marketing_campaign.created_at
),

user_marketing_purchases as (
    select
        marketing_campaign.user_id
    from user_first_purchase
    inner join marketing_campaign
        on user_first_purchase.user_id = marketing_campaign.user_id
    where
        marketing_campaign.created_at = first_purchase_date + interval '1 day'
)

select count(*)
from user_marketing_purchases


--
with user_first_purchase_dates as (
    select
        user_id,
        min(created_at) as first_purchase_date
    from marketing_campaign
    group by user_id
),

first_day_purchases as (
    select
        user_first_purchase_dates.user_id,
        marketing_campaign.product_id
    from user_first_purchase_dates
    inner join marketing_campaign
        on user_first_purchase_dates.user_id = marketing_campaign.user_id
        and user_first_purchase_dates.first_purchase_date = marketing_campaign.created_at
),

day_after_purchases as (
    select
        marketing_campaign.user_id,
        marketing_campaign.product_id
    from user_first_purchase_dates
    inner join marketing_campaign
        on user_first_purchase_dates.user_id = marketing_campaign.user_id
    where
        marketing_campaign.created_at > first_purchase_date
)

select count(distinct day_after_purchases.user_id)
from day_after_purchases
left join first_day_purchases
    on day_after_purchases.user_id = first_day_purchases.user_id
    and day_after_purchases.product_id = first_day_purchases.product_id
where first_day_purchases.product_id is null