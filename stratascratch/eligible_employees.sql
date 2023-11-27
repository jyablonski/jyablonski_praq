-- IBM wants to reward employees who meet certain criteria. However, to ensure fairness, the following conditions must be met:


-- •	The employee must have been with the company for at least 3 years
-- •	The employee's department must have at least 5 employees
-- •	The salary must be within the top 10% of salaries within the department


-- The output should include the Employee ID, Salary, and Department of the employees meeting the criteria.

with department_employees as (
    select
        department,
        count(*) as num_employees
    from employee_salaries
    group by department
),

salary_rank as (
    select
        employee_id,
        percent_rank() over (partition by department order by salary desc) as salary_rank
    from employee_salaries
)

select 
    employee_salaries.employee_id,
    salary_rank,
    salary,
    employee_salaries.department,
    num_employees,
    tenure
from employee_salaries
    inner join department_employees 
        on employee_salaries.department = department_employees.department
    inner join salary_rank
        on employee_salaries.employee_id = salary_rank.employee_id
where 
    num_employees >= 5
    and tenure >= 3
    and salary_rank <= 0.10;