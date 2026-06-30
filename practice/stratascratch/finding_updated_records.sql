/* https://platform.stratascratch.com/coding/10299-finding-updated-records?code_type=1

We have a table with employees and their salaries, however, some of the records
are old and contain outdated salary information. Find the current salary of
each employee assuming that salaries increase each year. Output their id,
first name, last name, department ID, and current salary. Order your list
by employee ID in ascending order. */

-- can use row number here to identify the rows w/ the highest salary for each employee id
with current_salaries as (
    select
        id,
        first_name,
        last_name,
        salary,
        department_id,
        row_number() over (partition by id order by salary desc) as salary_rn
    from ms_employee_salary
)

-- then return results in the requested format with the ascending employee id sorting
select
    id,
    first_name,
    last_name,
    department_id,
    salary
from current_salaries
where salary_rn = 1
order by id