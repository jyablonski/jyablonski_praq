
-- every derived table must have an alias <- eat shit

select
    email as Email
from (select email, count(*) from Person group by 1 having count(*) > 1) boobs