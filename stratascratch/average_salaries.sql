/* https://platform.stratascratch.com/coding/9917-average-salaries?code_type=1

Compare each employee's salary with the average salary of the corresponding department.
Output the department, first name, and salary of employees along with the average salary
of that department. */

-- sigh
with avg_department_salaries as (
    select
        department,
        round(avg(salary), 3) as avg_salary
    from employee
    group by department
)

select
    employee.department,
    employee.first_name,
    employee.salary,
    avg_department_salaries.avg_salary
from employee
inner join avg_department_salaries
    on employee.department = avg_department_salaries.department