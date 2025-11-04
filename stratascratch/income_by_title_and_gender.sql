/* https://platform.stratascratch.com/coding/10077-income-by-title-and-gender?code_type=1

Find the average total compensation based on employee titles and gender. Total compensation
is calculated by adding both the salary and bonus of each employee. However, not every
employee receives a bonus so disregard employees without bonuses in your calculation.
Employee can receive more than one bonus.

Output the employee title, gender (i.e., sex), along with the average total compensation. */

-- another problem written by a dipshit. the bonus table has multiple records for bonuses,
-- and we aren't incldued any employee without a bonus. so you have to join it up
-- and sum the bonuses for that employee together, and then take the average afterwards
with qualified_employees as (
    select
        sf_employee.id,
        sf_employee.sex,
        sf_employee.employee_title,
        sf_employee.salary,
        sum(sf_bonus.bonus) as total_bonus
    from sf_employee
    inner join sf_bonus
        on sf_employee.id = sf_bonus.worker_ref_id
    group by 1, 2, 3, 4
)

select
    employee_title,
    sex,
    avg(salary + total_bonus) as avg_compensation
from qualified_employees
group by
    employee_title,
    sex