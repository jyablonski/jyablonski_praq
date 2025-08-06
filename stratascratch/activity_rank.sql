{# https://platform.stratascratch.com/coding/10351-activity-rank?code_type=1

Find the email activity rank for each user. Email activity rank is defined by the total
number of emails sent. The user with the highest number of emails sent will have a rank
of 1, and so on. Output the user, total emails, and their activity rank.

•	Order records first by the total emails in descending order.
•	Then, sort users with the same number of emails in alphabetical order by their username.
•	In your rankings, return a unique value (i.e., a unique rank) even if multiple users have the same number of emails. #}

with users_email_count as (
    select
        from_user,
        count(*) as total_emails
    from google_gmail_emails
    group by from_user
),

users_email_count_ranked as (
    select
        from_user,
        total_emails,
        row_number() over(order by total_emails desc, from_user) as row_number
    from users_email_count
)

select
    from_user,
    total_emails,
    row_number
from users_email_count_ranked
order by
    total_emails desc,
    from_user