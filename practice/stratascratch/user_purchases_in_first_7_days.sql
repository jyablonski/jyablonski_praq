with user_purchases as (
    select
        events.event_id,
        users.user_id
    from events
    inner join users on
        events.user_id = users.user_id
    where
        event_type = 'purchase'
        and event_ts <= users.created_at + interval '7 days'
)

select 
    count(user_purchases.user_id) * 100.0 / count(users.user_id) as purchase_rate
from users
left join user_purchases on
    users.user_id = user_purchases.user_id
