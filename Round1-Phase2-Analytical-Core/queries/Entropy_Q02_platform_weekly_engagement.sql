-- Q2: Platform-wise Weekly Engagement Trend
-- Tracks how average engagement evolves week-by-week per platform with 4-week rolling average
-- Techniques: CTE, Rolling window (ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)

WITH weekly AS (
    SELECT
        platform,
        strftime('%Y-W%W', timestamp) AS week,
        COUNT(*) AS post_count,
        ROUND(AVG(likes), 0) AS avg_likes
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY platform, week
)
SELECT
    platform,
    week,
    post_count,
    avg_likes,
    ROUND(AVG(avg_likes) OVER (
        PARTITION BY platform
        ORDER BY week
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_4wk_avg_likes
FROM weekly
ORDER BY platform, week;
