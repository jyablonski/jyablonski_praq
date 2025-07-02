{# Table: Employee

+--------------+---------+
| Column Name  | Type    |
+--------------+---------+
| id           | int     |
| name         | varchar |
| salary       | int     |
| departmentId | int     |
+--------------+---------+
id is the primary key (column with unique values) for this table.
departmentId is a foreign key (reference columns) of the ID from the Department table.
Each row of this table indicates the ID, name, and salary of an employee. It also contains the ID of their department.
 

Table: Department

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| id          | int     |
| name        | varchar |
+-------------+---------+
id is the primary key (column with unique values) for this table. It is guaranteed that department name is not NULL.
Each row of this table indicates the ID of a department and its name.
 

Write a solution to find employees who have the highest salary in each of the departments.

Return the result table in any order.

The result format is in the following example.

 
 #}

-- row_num - no ties, and no gaps
-- rank - ties, and gaps
-- dense_rank - ties, no gaps
with cte as (
    select
        Department.name as department,
        Employee.name as employee,
        Employee.salary,
        dense_rank() over(partition by Department.id order by Employee.salary desc) as row_num
    from Employee
    Inner Join Department on Employee.departmentId = Department.id
)

select
    department,
    employee,
    salary
from cte
where row_num = 1