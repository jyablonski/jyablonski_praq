-- top 3 and bottom 3
with players as (
    select *
    from {{ ref('prod_scorers') }}
    where season_avg_ppg >= 5
),

top_3 as (
    select
        player,
        season_avg_ppg,
        'top 3' as type
    from players
    order by season_avg_ppg desc
    limit 3
),

bot_3 as (
    select
        player,
        season_avg_ppg,
        'bot 3' as type
    from players
    order by season_avg_ppg
    limit 3
)

select *
from top_3
union
select *
from bot_3


-- day over day change with LAG
with stat as (
    select 
        player,
        date,
        pts,
        LAG(pts) over (partition by player order by date) as prev_day_pts,
        round(pts / LAG(pts) over (partition by player order by date), 3) * 100 as dod_pct_change
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry'
)

select *
from stat

-- using date between - which is inclusive both ways
with stat as (
    select 
        player,
        date,
        SUM(pts) as sum_pts
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry' and date between '2021-10-19' AND '2021-11-03'
    group by player, date
    
)

select *
from stat

-- ALL 3 RANK FUNCTIONS
with stat as (
    select 
        player,
        date,
        pts,
        row_number() over(partition by player order by pts desc) as row_number_rank, -- never skips
        RANK() OVER (partition by player order by pts desc) as rank_rank,            -- values can have same rank if duplicate, but skips next value if there's a duplicate
        DENSE_RANK() over (partition by player order by pts desc) as dense_rank      -- values can have same rank if duplicate, but never skip the next value
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry' and date between '2021-10-19' AND '2021-12-31'
    
)

select *
from stat

-- cumulative sum
with stat as (
    select 
        player,
        date,
        pts,
        sum(pts) over (partition by player) as cum_sum_pts_agg,           -- this will just return a total raw aggregate
        sum(pts) over (partition by player order by date) as cum_sum_pts, -- this will give a row level running total for cumulative sum
        row_number() over(partition by player order by pts desc) as row_number_rank,
        RANK() OVER (partition by player order by pts desc) as rank_rank,
        DENSE_RANK() over (partition by player order by pts desc) as dense_rank
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player = 'Stephen Curry' and date between '2021-10-19' AND '2021-12-31'
    
)

select *
from stat

-- find the first game date where x and y players broke 800 pts in the season
with stat as (
    select 
        player,
        date,
        pts,
        sum(pts) over (partition by player order by date) as cum_sum_pts,
        row_number() over(partition by player order by pts desc) as row_number_rank,
        RANK() OVER (partition by player order by pts desc) as rank_rank,
        DENSE_RANK() over (partition by player order by pts desc) as dense_rank,
        800 - sum(pts) over (partition by player order by date) as closest_value
    from {{ ref('prep_boxscores_mvp_calc') }}
    where player in ('Stephen Curry', 'Kevin Durant') and date between '2021-10-19' AND '2021-12-31'
    
),

-- find the first negative value (which willbe the max value in this list after filtering out positives)
max_cte as (
    select 
        player,
        max(closest_value) as closest_value
    from stat
    where closest_value < 0  
    group by player
)

select 
    player,
    date
from stat
inner join max_cte using (player, closest_value);

select distinct name
from cats
union
select distinct name
from dogs;


UPDATE enrollments set year = 2015 where ids between 20 and 100;


with my_cte as (
    SELECT
        userId,
        count(*) as num_records
    from sessions
    group by userId
    having num_records > 1
)

SELECT
    userId,
    avg(duration) as avg_duration
from sessions
inner join my_cte using (userId)
group by userId;


select x, y from table1
inner joins table2 on table1.x = table2.fk_x

-- starts and ends with vowels
select distinct city
from STATION
where CITY REGEXP '^[aeiou]' AND CITY REGEXP '[aeiou]$';

-- does not start and end with voewels.
select distinct city
from station
where city not REGEXP '^[aeiou]' AND city not REGEXP '[aeiou]$';

-- ^^^ same as
SELECT DISTINCT CITY
FROM STATION
WHERE CITY NOT REGEXP '^[aeiou].*[aeiou]$'; 

-- finding salary of the best friends who earned more than the person did.
with my_cte as (
    select
        f.ID,
        f.Friend_ID,
        stu1.Name as name,
        p.Salary as salary,
        stu2.Name as best_friend_name,
        p2.Salary as best_friend_salary
    from Friends f
    left join Students stu1 using (ID)
    left join Students stu2 on f.Friend_ID = stu2.ID
    left join Packages p on f.ID = p.ID
    left join Packages p2 on stu2.ID = p2.ID
    where p2.Salary > p.Salary
    order by p2.Salary
)

select name
from my_cte;

-- contest and challenge id one
with my_cte as (
    select
        c.contest_id,
        c.hacker_id,
        c.name,
        co.college_id,
        co.contest_id,
        ch.challenge_id,
        vs.total_views,
        vs.total_unique_views,
        s.total_submissions,
        s.total_accepted_submissions
    from Contests c
    left join Colleges co using (contest_id)
    left join Challenges ch using (college_id)
    left join View_Stats vs using (challenge_id)
    left join Submission_Stats s using (challenge_id)
),

final as (
    select
        contest_id,
        hacker_id,
        name,
        sum(total_submissions) as sum_total_submissions,
        sum(total_accepted_submissions) as sum_total_accepted_submissions,
        sum(total_views) as sum_total_views,
        sum(total_unique_views) as sum_total_unique_views
    from my_cte
    group by contest_id, hacker_id, name
    having sum(total_submissions) + sum(total_accepted_submissions) + sum(total_views) + sum(total_unique_views) > 0
    order by contest_id
)

select *
from final;

-- triangle case when
select 
    case when C * C > ((B * B) + (A * A)) then 'Not A Triangle'
     when (A = B and B != C) OR
          (A != B and B = C) OR
          (A = C and B != C) then 'Isosceles'
     when ((A != B) and (A != C) and (B != C)) then "Scalene"
     when A = B and B = C then 'Equilateral'
     else 'HELP' end
from TRIANGLES;

-- occupation
with doctors as (
    select
        name as Doctor,
        row_number() over (order by name) as seqnum
    from OCCUPATIONS
    where Occupation = 'Doctor'
),

actors as (
    select
        name as Actor,
        row_number() over (order by name) as seqnum
    from OCCUPATIONS
    where Occupation = 'Actor'
),

singers as (
    select
        name as Singer,
        row_number() over (order by name) as seqnum
    from OCCUPATIONS
    where Occupation = 'Singer'
),

professors as (
    select
        name as Professor,
        row_number() over (order by name) as seqnum
    from OCCUPATIONS
    where Occupation = 'Professor'
),

final as (
    select 
        Doctor,
        Professor,
        Singer,
        Actor
    from professors
    left join actors using (seqnum)
    left join singers using (seqnum)
    left join doctors using (seqnum)
)

select 
    *
from final; 

-- Binary Search Tree
select
    N,
    case when P IS NULL then 'Root' -- this means it has no parent so it has to be the root
         when N IN (select distinct P from BST) then 'Inner' -- this means if the node is found as an existing parent in the same table, then it has to be inner
         else 'Leaf' end as output -- if it doesn't fall under the 2 previous categories then it has to be a leaf.
from BST
order by N;


-- business owner - MS SQL Server
with companies as (
    select distinct
        company_code,
        founder
    from Company
),

lead_managers as (
    select distinct
        company_code,
        count(distinct lead_manager_code) as num_lead_managers
    from Lead_Manager
    group by company_code
),

senior_managers as (
    select distinct
        company_code,
        count(distinct senior_manager_code) as num_senior_managers
    from Senior_Manager
    group by company_code
),

managers as (
    select distinct
        company_code,
        count(distinct manager_code) as num_managers
    from Manager
    group by company_code
),

employees as (
    select distinct
        company_code,
        count(distinct employee_code) as num_employees
    from Employee
    group by company_code
),

final as (
    select 
        c.company_code,
        c.founder,
        lm.num_lead_managers,
        sm.num_senior_managers,
        m.num_managers,
        e.num_employees
    from companies c
    left join lead_managers lm on lm.company_code = c.company_code
    left join senior_managers sm on sm.company_code = c.company_code
    left join managers m on m.company_code = c.company_code
    left join employees e on e.company_code = c.company_code
)

select *
from final
order by company_code;


-- alternatively
select c.company_code, c.founder,
       count(distinct l.lead_manager_code),
       count(distinct s.senior_manager_code),
       count(distinct m.manager_code),
       count(distinct e.employee_code)
from Company as c 
join Lead_Manager as l 
on c.company_code = l.company_code
join Senior_Manager as s
on l.lead_manager_code = s.lead_manager_code
join Manager as m 
on m.senior_manager_code = s.senior_manager_code
join Employee as e
on e.manager_code = m.manager_code
group by c.company_code, c.founder
order by c.company_code;

-- print ***** 
SET @NUMBER = 21;
SELECT REPEAT('* ', @NUMBER := @NUMBER - 1)
    FROM information_schema.tables LIMIT 20;

-- other way around
SET @NUMBER = 0;
SELECT REPEAT('* ', @NUMBER := @NUMBER + 1)
    FROM information_schema.tables LIMIT 20;

-- num separator
SELECT GROUP_CONCAT(NUMB SEPARATOR '&')
FROM (
    SELECT @num:=@num+1 as NUMB FROM
    information_schema.tables t1,
    information_schema.tables t2,
    (SELECT @num:=1) tmp
) tempNum
WHERE NUMB<=1000 AND NOT EXISTS(
        SELECT * FROM (
            SELECT @nu:=@nu+1 as NUMA FROM
                information_schema.tables t1,
                information_schema.tables t2,
                (SELECT @nu:=1) tmp1
                LIMIT 1000
            ) tatata
        WHERE FLOOR(NUMB/NUMA)=(NUMB/NUMA) AND NUMA<NUMB AND NUMA>1
    )


-- hackers per day
-- grabbing date_rank and hacker_rank and then making them equal each other to find the people submitting on each day.
with cte_1 as (
    select *
    , dense_rank() over(order by submission_date) as date_rank
    , dense_rank() over(partition by hacker_id order by submission_date) as hacker_rank 
    from submissions s 
),

-- cte_2 gives the hackers that have participated every day up until the day they stop.
cte_2 as (
    select submission_date, count(distinct hacker_id) as hkr_cnt
    from cte_1 
    where cte_1.date_rank = cte_1.hacker_rank
    group by submission_date
),

-- making hacker submission counts per day
cte_3 as (
    select submission_date, hacker_id, count(*) as sub_cnt 
    from submissions 
    group by submission_date, hacker_id
),

-- grabbing the hackers who submitted the most per day and abiding by the order the question asked for (submission count desc, hacker_id ascending)
cte_4 as (
    select 
        submission_date,
        hacker_id, 
        rank() over(partition by submission_date order by sub_cnt desc, hacker_id) as max_rank 
    from cte_3
),

-- querying both the hackers that participated every day from cte_2, and the #1 hacker data each day from cte_4.
cte_5 as (
    select cte_2.submission_date, cte_2.hkr_cnt, cte_4.hacker_id, Hackers.name
    from cte_2 
    join cte_4 on cte_2.submission_date = cte_4.submission_date and cte_4.max_rank = 1
    join Hackers on Hackers.hacker_id = cte_4.hacker_id
)

select * from cte_5
order by 1;


with num_submissions as (
    select
        hacker_id,
        submission_date,
        count(*) as num_submissions
    from Submissions
    group by hacker_id, submission_date
),

num_hackers as (
    select
        submission_date,
        count(distinct hacker_id) as num_hackers
    from Submissions
    group by submission_date
),

final as (
    select
        num_submissions.submission_date,
        Hackers.hacker_id,
        num_hackers.num_hackers,
        name,
        num_submissions
    from num_submissions
    left join Hackers on Hackers.hacker_id = num_submissions.hacker_id
    left join num_hackers on num_hackers.submission_date = num_submissions.submission_date

)

select *
from final
order by submission_date, num_submissions desc, hacker_id;

-- average salary with no 0s.
-- remove literally all 0s in a column.
with my_cte as (
    select 
        *,
        REPLACE(salary, 0, '') as fk_salary
    from Employees
)

-- ceil will round up no matter what
select
    ceil(avg(salary) - avg(fk_salary))
from my_cte;


-- sql server doesnt have fucking limit lmao
with my_cte as (
    select
        employee_id,
        months * salary as total_earnings
    from employee
),

max_cte as (
    select
        max(total_earnings) as max_total_earnings,
        count(*) as num_emps
    from my_cte
    group by total_earnings

)

-- manhattan distance
SELECT TOP 1 CONCAT(max_total_earnings, ' ', num_emps)
from max_cte
order by max_total_earnings desc;