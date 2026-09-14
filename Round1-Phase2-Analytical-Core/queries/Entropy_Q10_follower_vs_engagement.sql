-- Q10: Follower Count vs Average Engagement
-- Buckets users by follower count and compares engagement
-- Techniques: CTE, CASE bucketing

WITH user_eng AS (
    SELECT
        u.user_id,
        u.follower_count,
        ROUND(AVG(COALESCE(p.likes, 0)), 0) AS avg_likes,
        ROUND(AVG(p.shares), 0) AS avg_shares,
        ROUND(AVG(p.comments), 0) AS avg_comments,
        COUNT(*) AS total_posts
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id
)
SELECT
    CASE
        WHEN follower_count < 5000 THEN '0-5K'
        WHEN follower_count < 10000 THEN '5K-10K'
        WHEN follower_count < 20000 THEN '10K-20K'
        WHEN follower_count < 30000 THEN '20K-30K'
        WHEN follower_count < 40000 THEN '30K-40K'
        ELSE '40K+'
    END AS follower_bracket,
    COUNT(*) AS users_in_bracket,
    ROUND(AVG(avg_likes), 0) AS avg_likes,
    ROUND(AVG(avg_shares), 0) AS avg_shares,
    ROUND(AVG(avg_comments), 0) AS avg_comments,
    ROUND(AVG(total_posts), 1) AS avg_posts
FROM user_eng
GROUP BY follower_bracket
ORDER BY MIN(follower_count);
