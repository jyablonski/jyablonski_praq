-- waste of my mf ass time
select
    score,
    dense_rank() over (order by score desc) as 'rank'
from Scores