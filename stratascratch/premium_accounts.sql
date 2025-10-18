/* https://platform.stratascratch.com/coding/2097-premium-acounts?code_type=1

You have a dataset that records daily active users for each premium account. A premium account
appears in the data every day as long as it remains premium. However, some premium accounts
may be temporarily discounted, meaning they are not actively paying — this is indicated by
a final_price of 0.


For each of the first 7 available dates in the dataset, count the number of premium accounts
that were actively paying on that day. Then, track how many of those same accounts are still
premium and actively paying exactly 7 days later, based solely on their status on that 7th
day (i.e., both dates must exist in the dataset). Accounts are only counted if they appear
in the data on both dates.


Output three columns:
•   The date of initial calculation.
•   The number of premium accounts that were actively paying on that day.
•   The number of those accounts that remain premium and are still paying after 7 days. */

-- grab all of the records that satisfy the criteria for a premium account
with premium_accounts as (
    select
        entry_date,
        account_id,
        final_price
    from premium_accounts_by_day
    where final_price > 0
)

-- then pull from that list and self join onto itself, keeping only the records that are 7 days apart
-- we can order by entry_date (ascending) and perform our aggregations this way to get the answer
select
    premium_accounts.entry_date,
    count(distinct premium_accounts.account_id) as premium_paid_accounts,
    count(distinct premium_accounts_b.account_id) as premium_paid_accounts_after_7d
from premium_accounts
left join premium_accounts premium_accounts_b
    on premium_accounts.account_id = premium_accounts_b.account_id
    and (premium_accounts_b.entry_date - premium_accounts.entry_date) = 7
group by 1
order by 1
limit 7