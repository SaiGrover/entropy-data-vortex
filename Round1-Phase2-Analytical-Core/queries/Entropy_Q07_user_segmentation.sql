-- Q7: User Segmentation by Activity Level
-- Classifies users into quartile-based segments
-- Techniques: CTE, NTILE(4) window function

WITH user_metrics AS (
    SELECT
        p.user_id,
        u.location,
        u.follower_count,
        COUNT(*) AS total_posts,
        ROUND(AVG(p.likes), 0) AS avg_likes,
        ROUND(AVG(p.shares), 0) AS avg_shares,
        ROUND(AVG(p.comments), 0) AS avg_comments,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement
    FROM posts p
    JOIN users u ON p.user_id = u.user_id
    GROUP BY p.user_id
),
segmented AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY total_posts DESC) AS activity_quartile,
        NTILE(4) OVER (ORDER BY avg_engagement DESC) AS engagement_quartile
    FROM user_metrics
)
SELECT
    CASE activity_quartile
        WHEN 1 THEN 'Power User'
        WHEN 2 THEN 'Active'
        WHEN 3 THEN 'Moderate'
        WHEN 4 THEN 'Low Activity'
    END AS activity_segment,
    COUNT(*) AS user_count,
    ROUND(AVG(total_posts), 1) AS avg_posts,
    ROUND(AVG(avg_engagement), 0) AS avg_engagement,
    ROUND(AVG(follower_count), 0) AS avg_followers,
    MIN(total_posts) AS min_posts,
    MAX(total_posts) AS max_posts
FROM segmented
GROUP BY activity_quartile
ORDER BY activity_quartile;
