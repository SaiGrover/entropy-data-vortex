-- M4: Platform Behaviour by High-Follower Users
-- Among users with at least 30,000 followers, which platform gives them the
-- highest average engagement per post?  Each platform's figure is compared
-- with the same platform's average across ALL users to see whether the
-- high-follower cohort behaves any differently.

WITH high_follower_posts AS (
    SELECT
        p.platform,
        p.user_id,
        p.likes + p.shares + p.comments AS engagement
    FROM posts p
    JOIN users u ON u.user_id = p.user_id
    WHERE u.follower_count >= 30000
      AND p.platform IS NOT NULL
      AND p.likes    IS NOT NULL
),
cohort_by_platform AS (
    SELECT
        platform,
        COUNT(DISTINCT user_id)      AS high_follower_users,
        COUNT(*)                     AS posts,
        ROUND(AVG(engagement), 1)    AS avg_engagement_high_followers
    FROM high_follower_posts
    GROUP BY platform
),
baseline_by_platform AS (
    SELECT
        platform,
        ROUND(AVG(likes + shares + comments), 1) AS avg_engagement_all_users
    FROM posts
    WHERE platform IS NOT NULL AND likes IS NOT NULL
    GROUP BY platform
)
SELECT
    RANK() OVER (ORDER BY c.avg_engagement_high_followers DESC) AS rank,
    c.platform,
    c.high_follower_users,
    c.posts,
    c.avg_engagement_high_followers,
    b.avg_engagement_all_users,
    ROUND(c.avg_engagement_high_followers - b.avg_engagement_all_users, 1)
                                                                AS cohort_minus_baseline
FROM cohort_by_platform c
JOIN baseline_by_platform b ON b.platform = c.platform
ORDER BY rank;
