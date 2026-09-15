-- E3: Average Engagement by Platform
-- Which platform generates the highest average total engagement?
-- Posts with a missing platform or missing likes are excluded so that all
-- four averages are computed over the same set of rows.

WITH platform_stats AS (
    SELECT
        platform,
        COUNT(*)                                   AS post_count,
        ROUND(AVG(likes), 1)                       AS avg_likes,
        ROUND(AVG(shares), 1)                      AS avg_shares,
        ROUND(AVG(comments), 1)                    AS avg_comments,
        ROUND(AVG(likes + shares + comments), 1)   AS avg_total_engagement
    FROM posts
    WHERE platform IS NOT NULL
      AND likes    IS NOT NULL
    GROUP BY platform
),
overall AS (
    SELECT AVG(likes + shares + comments) AS grand_avg
    FROM posts
    WHERE platform IS NOT NULL AND likes IS NOT NULL
)
SELECT
    RANK() OVER (ORDER BY ps.avg_total_engagement DESC)              AS rank,
    ps.platform,
    ps.post_count,
    ps.avg_likes,
    ps.avg_shares,
    ps.avg_comments,
    ps.avg_total_engagement,
    ROUND(100.0 * (ps.avg_total_engagement - o.grand_avg) / o.grand_avg, 2)
                                                                     AS pct_vs_overall
FROM platform_stats ps
CROSS JOIN overall o
ORDER BY rank;
