/* https://platform.stratascratch.com/coding/2102-flags-per-video?code_type=1

For each video, find how many unique users flagged it. A unique user can be identified using the
combination of their first name and last name. Do not consider rows in which there is no flag ID. */

-- big sigh
with valid_records as (
    select
        concat(user_firstname, '-', user_lastname) as id,
        video_id,
        flag_id
    from user_flags
    where flag_id is not null
)

select
    video_id,
    count(distinct id) as num_unique_users
from valid_records
group by video_id