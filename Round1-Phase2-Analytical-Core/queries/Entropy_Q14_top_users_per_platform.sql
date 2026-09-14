-- Q14: Top Performing Users per Platform
-- Identifies top 3 users by average engagement for each platform
-- Techniques: CTE, ROW_NUMBER() partitioned by platform

WITH user_platform_eng AS (
    SELECT
        p.platform,
        p.user_id,
        u.location,
        u.follower_count,
        COUNT(*) AS posts_on_platform,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        ROW_NUMBER() OVER (
            PARTITION BY p.platform
            ORDER BY AVG(COALESCE(p.likes, 0) + p.shares + p.comments) DESC
        ) AS rank_in_platform
    FROM posts p
    JOIN users u ON p.user_id = u.user_id
    WHERE p.platform IS NOT NULL
    GROUP BY p.platform, p.user_id
    HAVING COUNT(*) >= 2
)
SELECT
    platform,
    user_id,
    location,
    follower_count,
    posts_on_platform,
    avg_engagement,
    rank_in_platform
FROM user_platform_eng
WHERE rank_in_platform <= 3
ORDER BY platform, rank_in_platform;
