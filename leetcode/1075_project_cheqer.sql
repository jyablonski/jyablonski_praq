-- easy as fuq tbh
with combo as (
    select
        Employee.employee_id,
        Project.project_id,
        Employee.experience_years
    from Project
    inner join Employee on
        Project.employee_id = Employee.employee_id
)

select
    project_id,
    round(avg(experience_years), 2) as average_years
from combo
group by project_id