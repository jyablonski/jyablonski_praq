{# https://platform.stratascratch.com/coding/2103-reviewed-flags-of-top-videos?code_type=1

For the video (or videos) that received the most user flags, how many of these flags were
reviewed by YouTube? Output the video ID and the corresponding number of reviewed flags. #}

with video_flags as (
    select
        user_flags.video_id,
        count(*) as num_flags,
        sum(case when reviewed_by_yt = true then 1 else 0 end) as num_flags_yt
    from user_flags
    inner join flag_review
        on user_flags.flag_id = flag_review.flag_id
    group by user_flags.video_id
),

videos_ranked as (
    select
        video_id,
        num_flags,
        rank() over(order by num_flags desc) as video_rank
    from video_flags
)

select
    video_flags.video_id,
    num_flags_yt
from video_flags
inner join videos_ranked
    on video_flags.video_id = videos_ranked.video_id
where video_rank = 1