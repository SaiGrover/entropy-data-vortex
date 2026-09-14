-- Q5: Suspicious Posting Patterns (Potential Bot Detection)
-- Identifies users posting > 3 times per day
-- Techniques: CTE, HAVING, Correlated subquery

WITH daily_activity AS (
    SELECT
        user_id,
        DATE(timestamp) AS post_date,
        COUNT(*) AS posts_that_day
    FROM posts
    GROUP BY user_id, DATE(timestamp)
    HAVING COUNT(*) > 3
)
SELECT
    d.user_id,
    u.location,
    u.follower_count,
    d.post_date,
    d.posts_that_day,
    (
        SELECT COUNT(*) FROM posts WHERE user_id = d.user_id
    ) AS total_posts
FROM daily_activity d
JOIN users u ON d.user_id = u.user_id
ORDER BY d.posts_that_day DESC
LIMIT 15;
