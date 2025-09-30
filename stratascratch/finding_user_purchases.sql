/* https://platform.stratascratch.com/coding/10322-finding-user-purchases?code_type=1

Identify returning active users by finding users who made a second purchase within 1 to 7 days
after their first purchase. Ignore same-day purchases. Output a list of these user_ids. */

with user_first_purchases as (
    select
        user_id,
        min(created_at) as first_purchase_date
    from amazon_transactions
    group by user_id
),

-- example: first purchase on jan 1
-- we want to find users with another purchase from jan 2 to jan 8
returning_users as (
    select
        amazon_transactions.user_id,
        amazon_transactions.id as purchase_id,
        amazon_transactions.created_at as purchase_date
    from amazon_transactions
    inner join user_first_purchases
        on amazon_transactions.user_id = user_first_purchases.user_id
    where
        amazon_transactions.created_at > user_first_purchases.first_purchase_date
        and amazon_transactions.created_at <= user_first_purchases.first_purchase_date + 7
)

select distinct user_id
from returning_users