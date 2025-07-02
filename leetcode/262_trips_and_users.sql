{# Table: Trips

+-------------+----------+
| Column Name | Type     |
+-------------+----------+
| id          | int      |
| client_id   | int      |
| driver_id   | int      |
| city_id     | int      |
| status      | enum     |
| request_at  | varchar  |     
+-------------+----------+
id is the primary key (column with unique values) for this table.
The table holds all taxi trips. Each trip has a unique id, while client_id and driver_id are foreign keys to the users_id at the Users table.
Status is an ENUM (category) type of ('completed', 'cancelled_by_driver', 'cancelled_by_client').

Table: Users

+-------------+----------+
| Column Name | Type     |
+-------------+----------+
| users_id    | int      |
| banned      | enum     |
| role        | enum     |
+-------------+----------+
users_id is the primary key (column with unique values) for this table.
The table holds all users. Each user has a unique users_id, and role is an ENUM type of ('client', 'driver', 'partner').
banned is an ENUM (category) type of ('Yes', 'No').

The cancellation rate is computed by dividing the number of canceled (by client or driver) requests with unbanned users by the total number of requests with unbanned users on that day.

Write a solution to find the cancellation rate of requests with unbanned users (both client and driver must not be banned) each day between "2013-10-01" and "2013-10-03" with at least one trip. Round Cancellation Rate to two decimal points.

#}

-- really dumb problem, you wouldnt have banned drivers taking requests ever
with total_requests as (
    select
        date(request_at) as date_request_at,
        count(*) as num_requests_total
    from Trips
    inner join Users ClientUsers on Trips.client_id = ClientUsers.users_id
    left join Users DriverUsers on Trips.driver_id = DriverUsers.users_id
    where 
        ClientUsers.banned = 'No'
        and DriverUsers.banned = 'No'
        and date(Trips.request_at) between '2013-10-01' and '2013-10-03'
    group by 1
),

cancelled_requests as (
    select
        date(request_at) as date_request_at,
        count(*) as num_requests_cancelled
    from Trips
    left join Users ClientUsers on Trips.client_id = ClientUsers.users_id
    left join Users DriverUsers on Trips.driver_id = DriverUsers.users_id
    where
        ClientUsers.banned = 'No'
        and DriverUsers.banned = 'No'
        and Trips.status in ('cancelled_by_driver', 'cancelled_by_client')
        and date(Trips.request_at) between '2013-10-01' and '2013-10-03'
    group by 1
)

select
    total_requests.date_request_at as Day,
    round(coalesce(cancelled_requests.num_requests_cancelled, 0) / total_requests.num_requests_total, 2) as 'Cancellation Rate'

from total_requests
left join cancelled_requests on total_requests.date_request_at = cancelled_requests.date_request_at

{# | Day        | Cancellation Rate |
| ---------- | ----------------- |
| 2013-10-01 | 0.33              |
| 2013-10-02 | 0                 |
| 2013-10-03 | 0.5               | #}