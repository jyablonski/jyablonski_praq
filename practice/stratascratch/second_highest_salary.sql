/* https://platform.stratascratch.com/coding/9892-second-highest-salary?code_type=1

Find the second highest salary of employees. */

-- sigh
with salaries_ranked as (
    select
        salary,
        row_number() over (order by salary desc) as rn
    from employee
    order by salary desc
)

select salary
from salaries_ranked
where rn = 2