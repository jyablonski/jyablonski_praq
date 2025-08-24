{# https://platform.stratascratch.com/coding/10171-find-the-genre-of-the-person-with-the-most-number-of-oscar-winnings?code_type=1

Find the genre of the person with the most number of oscar winnings.
If there are more than one person with the same number of oscar wins, return the first one in alphabetic order based
on their name. Use the names as keys when joining the tables.
 #}

-- dogshit question because their table data was incomplete
with person_oscar_counts as (
    select
        nominee,
        sum(case when winner = true then 1 else 0 end) as num_oscar_winnings,
        rank() over(order by sum(case when winner = true then 1 else 0 end) desc) as rn
    from oscar_nominees
    where winner = true
    group by nominee
),

nominee_details as (
    select
        person_oscar_counts.nominee,
        nominee_information.top_genre
    from person_oscar_counts
    left join nominee_information
        on person_oscar_counts.nominee = nominee_information.name
    where rn = 1
)

select top_genre
from nominee_details
order by top_genre
limit 1