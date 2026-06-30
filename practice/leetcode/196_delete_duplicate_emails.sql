with ranked_users as (
    select
        id,
        row_number() over(partition by email order by id) as row_num
    from Person
)

delete from Person
using ranked_users
where 
    Person.id = ranked_users.id
    and ranked_users.row_num != 1;
