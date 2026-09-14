-- Q1: Monthly Post Volume Trend with Growth Rate
-- Identifies months with highest/lowest activity and month-over-month growth rate
-- Techniques: CTE, LAG() window function

WITH monthly AS (
    SELECT
        strftime('%Y-%m', timestamp) AS month,
        COUNT(*) AS post_count,
        ROUND(AVG(likes), 0) AS avg_likes,
        ROUND(AVG(shares), 0) AS avg_shares,
        ROUND(AVG(comments), 0) AS avg_comments
    FROM posts
    GROUP BY month
),
trends AS (
    SELECT
        month,
        post_count,
        avg_likes,
        avg_shares,
        avg_comments,
        LAG(post_count) OVER (ORDER BY month) AS prev_month_count,
        ROUND(
            (post_count - LAG(post_count) OVER (ORDER BY month)) * 100.0
            / LAG(post_count) OVER (ORDER BY month), 1
        ) AS growth_pct
    FROM monthly
)
SELECT * FROM trends ORDER BY month;
