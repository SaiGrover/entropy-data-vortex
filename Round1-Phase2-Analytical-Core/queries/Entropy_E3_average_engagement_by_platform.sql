-- E3: Average Engagement by Platform
-- Calculate the average likes, shares and comments for each platform.
-- Which platform generates the highest average total engagement?
--
-- Only posts with a missing platform are excluded, as the question implies.
-- AVG() skips NULLs, so avg_likes uses posts that have a like count while
-- avg_shares / avg_comments use every post on the platform. For total
-- engagement, likes + shares + comments is NULL when likes is missing, so
-- AVG() drops those posts: exactly the "ignore posts where likes are missing"
-- rule the brief uses to define total engagement (E2).

WITH platform_stats AS (
    SELECT
        platform,
        COUNT(*)                                  AS posts,
        COUNT(likes)                              AS posts_with_likes,
        ROUND(AVG(likes), 1)                      AS avg_likes,
        ROUND(AVG(shares), 1)                     AS avg_shares,
        ROUND(AVG(comments), 1)                   AS avg_comments,
        ROUND(AVG(likes + shares + comments), 1)  AS avg_total_engagement
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY platform
),
overall AS (
    SELECT AVG(likes + shares + comments) AS grand_avg
    FROM posts
    WHERE platform IS NOT NULL
)
SELECT
    RANK() OVER (ORDER BY ps.avg_total_engagement DESC)   AS engagement_rank,
    ps.platform,
    ps.posts,
    ps.posts_with_likes,
    ps.avg_likes,
    ps.avg_shares,
    ps.avg_comments,
    ps.avg_total_engagement,
    ROUND(100.0 * (ps.avg_total_engagement - o.grand_avg) / o.grand_avg, 2)
                                                          AS pct_vs_overall
FROM platform_stats ps
CROSS JOIN overall o
ORDER BY engagement_rank;
