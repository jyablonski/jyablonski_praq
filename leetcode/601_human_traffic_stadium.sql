{# Table: Stadium

+---------------+---------+
| Column Name   | Type    |
+---------------+---------+
| id            | int     |
| visit_date    | date    |
| people        | int     |
+---------------+---------+
visit_date is the column with unique values for this table.
Each row of this table contains the visit date and visit id to the stadium with the number of people during the visit.
As the id increases, the date increases as well.
 

Write a solution to display the records with three or more rows with consecutive id's, and the number of people is greater than or equal to 100 for each.

Return the result table ordered by visit_date in ascending order.

The result format is in the following example.
 #}

-- didnt finish

with data as (
    select
        id,
        visit_date,
        people,
        id - coalesce(lag(id) over (order by id), 0) as lag_diff,
        id - coalesce(lead(id) over (order by id), 0) as lead_diff,
        row_number() over(partition by id - coalesce(lag(id) over (order by id), 0) order by visit_date) as zz
    from Stadium

),

data2 as (

)

select 
    id,
    visit_date,
    people
from data
where
    lag_diff = 1
    and abs(lead_diff) = 1