-- https://platform.stratascratch.com/coding/10304-risky-projects?code_type=1

{# You are given a set of projects and employee data. Each project has a name, a budget, and a specific duration,
while each employee has an annual salary and may be assigned to one or more projects for particular periods.
The task is to identify which projects are overbudget. A project is considered overbudget if the prorated
cost of all employees assigned to it exceeds the project's budget.

To solve this, you must prorate each employee's annual salary based on the exact period they work on a
given project, relative to a full year. For example, if an employee works on a six-month project, only
half of their annual salary should be attributed to that project. Sum these prorated salary amounts for
all employees assigned to a project and compare the total with the project's budget.

Your output should be a list of overbudget projects, where each entry includes the project's name, its
budget, and the total prorated employee expenses for that project. The total expenses should be rounded
up to the nearest dollar. Assume all years have 365 days and disregard leap years.
 #}

with employee_data as (
    select
        linkedin_employees.id as emp_id,
        linkedin_employees.salary,
        linkedin_emp_projects.project_id,
        linkedin_projects.start_date,
        linkedin_projects.end_date,
        linkedin_projects.budget,
        linkedin_projects.end_date - linkedin_projects.start_date as num_days,
        salary * (linkedin_projects.end_date - linkedin_projects.start_date)::numeric / 365 as prorated_salary
    from linkedin_projects
    inner join linkedin_emp_projects
        on linkedin_projects.id = linkedin_emp_projects.project_id
    inner join linkedin_employees
        on linkedin_emp_projects.emp_id = linkedin_employees.id
),

project_data as (
    select
        project_id,
        ceil(sum(prorated_salary)) as prorated_employee_expense
    from employee_data
    group by project_id

)

select
    title,
    budget,
    prorated_employee_expense
from linkedin_projects
inner join project_data
    on linkedin_projects.id = project_data.project_id
where
    prorated_employee_expense > budget