-- Q8: Platform Preference Clustering
-- Groups users by their dominant platform
-- Techniques: CTE, ROW_NUMBER() partitioned by user

WITH platform_usage AS (
    SELECT
        user_id,
        platform,
        COUNT(*) AS platform_posts,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY COUNT(*) DESC) AS rn
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY user_id, platform
),
dominant AS (
    SELECT user_id, platform AS dominant_platform, platform_posts
    FROM platform_usage
    WHERE rn = 1
)
SELECT
    d.dominant_platform,
    COUNT(*) AS user_count,
    ROUND(AVG(d.platform_posts), 1) AS avg_posts_on_platform,
    ROUND(AVG(u.follower_count), 0) AS avg_followers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT user_id) FROM posts), 1) AS pct_of_users
FROM dominant d
JOIN users u ON d.user_id = u.user_id
GROUP BY d.dominant_platform
ORDER BY user_count DESC;
