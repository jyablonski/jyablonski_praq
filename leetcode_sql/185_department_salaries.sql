{# A company's executives are interested in seeing who earns the most money in each of the company's departments.
  A high earner in a department is an employee who has a salary in the top three unique salaries for that department.
Write a solution to find the employees who are high earners in each of the departments.
Return the result table in any order.
The result format is in the following example. #}

-- for each department, return the customers w/ the 3 highest unique salaries

with highest_earners as (
    select
        Employee.id,
        Department.id as department_id,
        Department.name as Department,
        salary,
        dense_rank() over (partition by Department.id order by salary desc) as highest_rank
    from Employee
    inner join Department on Employee.departmentId = Department.id
)

select
    Department,
    Employee.name as Employee,
    Employee.salary as Salary
from Employee
inner join highest_earners on Employee.id = highest_earners.id
where highest_rank <= 3;