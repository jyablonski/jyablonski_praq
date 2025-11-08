/* https://platform.stratascratch.com/coding/10296-facebook-accounts?code_type=1

Of all accounts with status records on January 10th, 2020, calculate the ratio of those with 'closed' status. */

-- have to do some fuckass 1.0 multiplication here to get the integer division to return accurate results
select
    1.0 * count(case when status = 'closed' then 1 end) / (count(*) * 1.0) as closed_ratio
from fb_account_status
where status_date = '2020-01-10';