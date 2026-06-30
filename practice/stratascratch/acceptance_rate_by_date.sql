/* https://platform.stratascratch.com/coding/10285-acceptance-rate-by-date?code_type=1

Calculate the friend acceptance rate for each date when friend requests were sent. A request is
sent if action = sent and accepted if action = accepted. If a request is not accepted, there is
no record of it being accepted in the table.

The output will only include dates where requests were sent and at least one of them was accepted
(acceptance can occur on any date after the request is sent). */

-- generate 1 row for every friend request interaction, along w/ whether it was accepted or not
with valid_events as (
    select
        user_id_sender,
        user_id_receiver,
        sum(case when action = 'sent' then 1 else 0 end) as friend_request_sent,
        sum(case when action = 'accepted' then 1 else 0 end) as friend_request_accepted
    from fb_friend_requests
    group by 1, 2
),

-- then join it back onto the friend requests table on the `sent` event to get the date
events_joined as (
    select
        fb_friend_requests.user_id_sender,
        fb_friend_requests.user_id_receiver,
        fb_friend_requests.date,
        valid_events.friend_request_sent,
        valid_events.friend_request_accepted
    from fb_friend_requests
    inner join valid_events
        on fb_friend_requests.user_id_sender = valid_events.user_id_sender
        and fb_friend_requests.user_id_receiver = valid_events.user_id_receiver
    where action = 'sent'
)

-- then calculate the percentage by date
select
    date,
    sum(friend_request_accepted) / sum(friend_request_sent) as percentage_acceptance
from events_joined
group by date