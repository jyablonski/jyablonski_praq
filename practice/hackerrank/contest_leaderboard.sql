with my_cte as (
    select
        Hackers.hacker_id,
        Hackers.name,
        Submissions.challenge_id,
        max(Submissions.score) as max_score
        -- row_number() over (partition by Hackers.hacker_id, Submissions.challenge_id order by Submissions.score desc) as 
    from Hackers
        inner join Submissions on Hackers.hacker_id = Submissions.hacker_id
    group by
        Hackers.hacker_id,
        Hackers.name,
        Submissions.challenge_id
)

select
    hacker_id,
    name,
    sum(max_score) as total_score
from my_cte
order by 
    sum(max_score) desc,
    hacker_id
