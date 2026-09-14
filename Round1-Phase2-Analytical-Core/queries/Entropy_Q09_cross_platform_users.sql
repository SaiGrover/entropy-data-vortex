-- Q9: Cross-Platform Users
-- Measures multi-platform usage and its effect on engagement
-- Techniques: CTE, COUNT(DISTINCT), SUM() OVER()

WITH user_platforms AS (
    SELECT
        user_id,
        COUNT(DISTINCT platform) AS platform_count,
        COUNT(*) AS total_posts,
        ROUND(AVG(COALESCE(likes, 0) + shares + comments), 0) AS avg_engagement
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY user_id
)
SELECT
    platform_count AS platforms_used,
    COUNT(*) AS user_count,
    ROUND(AVG(total_posts), 1) AS avg_total_posts,
    ROUND(AVG(avg_engagement), 0) AS avg_engagement,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_users
FROM user_platforms
GROUP BY platform_count
ORDER BY platform_count;
