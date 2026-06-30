-- https://platform.stratascratch.com/coding/9894-employee-and-manager-salaries?code_type=1

{# Find employees who are earning more than their managers. Output the employee's first name along with the corresponding salary. #}

with manager_data as (
    select
        id as manager_id,
        salary as manager_salary
    from employee
    where employee_title = 'Manager'
)

select
    employee.first_name,
    employee.salary
from employee
inner join manager_data
    on employee.manager_id = manager_data.manager_id
where employee.salary > manager_data.manager_salary
