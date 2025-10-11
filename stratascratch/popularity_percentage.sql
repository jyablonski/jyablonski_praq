/* https://platform.stratascratch.com/coding/10284-popularity-percentage?code_type=1

Find the popularity percentage for each user on Meta/Facebook. The dataset contains two columns,
user1 and user2, which represent pairs of friends. Each row indicates a mutual friendship between
user1 and user2, meaning both users are friends with each other. A user's popularity percentage
is calculated as the total number of friends they have (counting connections from both user1
and user2 columns) divided by the total number of unique users on the platform. Multiply this
value by 100 to express it as a percentage.


Output each user along with their calculated popularity percentage. The results should be ordered
by user ID in ascending order. */

WITH all_friendships AS (
    -- Get all friendships by combining both columns
    SELECT user1 AS username, user2 AS friend
    FROM facebook_friends
    
    UNION ALL
    
    SELECT user2 AS username, user1 AS friend
    FROM facebook_friends
),

user_friend_counts AS (
    -- Count total friends for each user
    SELECT 
        username,
        COUNT(*) AS num_friends
    FROM all_friendships
    GROUP BY username
),

total_users AS (
    -- Get the total number of unique users
    SELECT COUNT(DISTINCT username) AS total
    FROM all_friendships
)

SELECT 
    ufc.username,
    (ufc.num_friends * 100.0 / tu.total) AS popularity_percent
FROM user_friend_counts ufc
CROSS JOIN total_users tu
ORDER BY ufc.username;