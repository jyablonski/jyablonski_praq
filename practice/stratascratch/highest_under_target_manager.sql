{# https://platform.stratascratch.com/coding/9905-highest-target-under-manager?code_type=1

Identify the employee(s) working under manager manager_id=13 who have achieved the highest target.
Return each such employee’s first name alongside the target value. The goal is to display the
maximum target among all employees under manager_id=13 and show which employee(s) reached that
top value. #}

with max_target as (
    select
        max(target) as max_target
    from salesforce_employees
    where manager_id = 13
)

select
    first_name,
    target
from salesforce_employees
inner join max_target
    on salesforce_employees.target = max_target.max_target
where manager_id = 13