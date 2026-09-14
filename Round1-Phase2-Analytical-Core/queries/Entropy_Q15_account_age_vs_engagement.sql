-- Q15: Account Age vs Engagement
-- Tests whether account maturity correlates with higher engagement
-- Techniques: CTE, JULIANDAY(), CASE bucketing

WITH user_age AS (
    SELECT
        u.user_id,
        u.account_created,
        CAST((JULIANDAY(AVG(JULIANDAY(p.timestamp))) - JULIANDAY(u.account_created)) / 30 AS INTEGER) AS account_age_months,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        COUNT(*) AS total_posts
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id
)
SELECT
    CASE
        WHEN account_age_months < 12 THEN '< 12 months'
        WHEN account_age_months < 18 THEN '12-18 months'
        WHEN account_age_months < 24 THEN '18-24 months'
        ELSE '24+ months'
    END AS account_age_bucket,
    COUNT(*) AS user_count,
    ROUND(AVG(avg_engagement), 0) AS avg_engagement,
    ROUND(AVG(total_posts), 1) AS avg_posts
FROM user_age
GROUP BY account_age_bucket
ORDER BY MIN(account_age_months);
