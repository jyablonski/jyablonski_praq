/* https://platform.stratascratch.com/coding/10553-finding-purchases?code_type=1

Identify returning active users by finding users who made a second purchase within 7 days or
less of any previous transaction, excluding same-day purchases. Output a list of these user_id. */

-- for these problems that involve "finding second purchase", you can typically just join the table
-- onto itself and find the solutions you're looking for
select
    distinct amazon_transactions.user_id
from amazon_transactions
inner join amazon_transactions as amazon_transactions_b
    on amazon_transactions.user_id = amazon_transactions_b.user_id
    and (
        amazon_transactions.created_at != amazon_transactions_b.created_at
        and amazon_transactions_b.created_at > amazon_transactions.created_at
        and amazon_transactions_b.created_at - amazon_transactions.created_at <= 7
    )

order by amazon_transactions.user_id


-- this also works
with purchases as (
    select
        user_id,
        created_at,
        lag(created_at) over(partition by user_id order by created_at) as prev_purchase
    from amazon_transactions
)

select distinct user_id
from purchases
where created_at - prev_purchase between 1 and 7