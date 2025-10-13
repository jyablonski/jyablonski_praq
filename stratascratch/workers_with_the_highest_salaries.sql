/* https://platform.stratascratch.com/coding/10353-workers-with-the-highest-salaries?code_type=1

Management wants to analyze only employees with official job titles. Find the job titles
of the employees with the highest salary. If multiple employees have the same highest
salary, include all their job titles. */

-- do the inner join and then do a dense rank to capture any ties at the highest rank
with employee_job_titles as (
    select
        worker.worker_id,
        worker.salary,
        title.worker_title,
        dense_rank() over (order by worker.salary desc) as rn
    from worker
    inner join title
        on worker.worker_id = title.worker_ref_id
)

-- then just select the requested output format w/ the highest rank
select
    worker_title as best_paid_title
from employee_job_titles
where rn = 1