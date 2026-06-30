-- https://platform.stratascratch.com/coding/10308-salaries-differences?code_type=1
-- Calculates the difference between the highest salaries in the marketing and engineering departments. Output just the absolute difference in salaries.

with salaries as (
    select
        db_employee.id,
        db_dept.department,
        db_employee.salary,
        rank() over(partition by db_dept.department order by salary desc) as salary_rnk
    from db_employee
    inner join db_dept
        on db_employee.department_id = db_dept.id
    where db_dept.department in ('engineering', 'marketing')
),

max_salaries as (
    select
        max(case when department = 'engineering' then salary end) as max_engineering_salary,
        max(case when department = 'marketing' then salary end) as max_marketing_salary
    from salaries
    where salary_rnk = 1
)

select abs(max_engineering_salary - max_marketing_salary) as salary_difference
from max_salaries