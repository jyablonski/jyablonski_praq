/* https://platform.stratascratch.com/coding/9897-highest-salary-in-department?code_type=1

Find the employee with the highest salary per department.
Output the department name, employee's first name along with the corresponding salary. */

-- sigh
with salaries_ranked as (
    select
        department,
        first_name,
        salary,
        row_number() over (partition by department order by salary desc) as rn
    from employee
)

select
    department,
    first_name,
    salary
from salaries_ranked
where rn = 1