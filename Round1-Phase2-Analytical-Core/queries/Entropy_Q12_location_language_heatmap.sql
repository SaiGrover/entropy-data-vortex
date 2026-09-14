-- Q12: Location-Language Engagement Heatmap
-- Ranks location-language combinations by average engagement
-- Techniques: CTE, DENSE_RANK(), HAVING

WITH loc_lang AS (
    SELECT
        u.location,
        u.language,
        COUNT(*) AS post_count,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        COUNT(DISTINCT p.user_id) AS unique_users
    FROM posts p
    JOIN users u ON p.user_id = u.user_id
    GROUP BY u.location, u.language
    HAVING COUNT(*) >= 10
)
SELECT
    location,
    language,
    unique_users,
    post_count,
    avg_engagement,
    DENSE_RANK() OVER (ORDER BY avg_engagement DESC) AS engagement_rank
FROM loc_lang
ORDER BY engagement_rank
LIMIT 20;
