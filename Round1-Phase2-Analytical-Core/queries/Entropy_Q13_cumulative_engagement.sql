-- Q13: Cumulative Engagement Over Time
-- Tracks running totals of engagement across the timeline
-- Techniques: SUM() OVER (ORDER BY) cumulative window

WITH monthly_eng AS (
    SELECT
        strftime('%Y-%m', timestamp) AS month,
        SUM(COALESCE(likes, 0)) AS total_likes,
        SUM(shares) AS total_shares,
        SUM(comments) AS total_comments
    FROM posts
    GROUP BY month
)
SELECT
    month,
    total_likes,
    total_shares,
    total_comments,
    SUM(total_likes) OVER (ORDER BY month) AS cumulative_likes,
    SUM(total_shares) OVER (ORDER BY month) AS cumulative_shares,
    SUM(total_comments) OVER (ORDER BY month) AS cumulative_comments
FROM monthly_eng
ORDER BY month;
