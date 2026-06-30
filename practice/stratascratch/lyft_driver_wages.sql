/* https://platform.stratascratch.com/coding/10003-lyft-driver-wages?code_type=1

Find all Lyft drivers who earn either equal to or less than 30k USD or equal to or more than 70k USD.
Output all details related to retrieved records. */

-- sigh
select *
from lyft_drivers
where
    yearly_salary <= 30000
    or yearly_salary >= 70000