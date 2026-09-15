-- M4: Platform Behaviour by High-Follower Users
-- Among users with at least 30,000 followers, which platform gives them the
-- highest average engagement per post?
--
-- The high-follower cohort is compared with users BELOW 30,000 followers
-- (not with all users, which would include the cohort itself and shrink any
-- gap). Conditional aggregation computes both groups in a single scan, and
-- ranking each group separately shows whether the platform order holds.
-- Engagement follows the brief's definition: posts with missing likes are
-- ignored.

WITH post_engagement AS (
    SELECT
        p.platform,
        p.user_id,
        u.follower_count >= 30000             AS is_high_follower,
        p.likes + p.shares + p.comments       AS engagement
    FROM posts p
    JOIN users u ON u.user_id = p.user_id
    WHERE p.platform IS NOT NULL
      AND p.likes    IS NOT NULL
),
by_platform AS (
    SELECT
        platform,
        COUNT(DISTINCT CASE WHEN is_high_follower     THEN user_id END) AS high_follower_users,
        SUM(is_high_follower)                                            AS high_follower_posts,
        AVG(CASE WHEN is_high_follower     THEN engagement END)          AS avg_high,
        AVG(CASE WHEN NOT is_high_follower THEN engagement END)          AS avg_other
    FROM post_engagement
    GROUP BY platform
)
SELECT
    RANK() OVER (ORDER BY avg_high  DESC)                AS rank_high_followers,
    RANK() OVER (ORDER BY avg_other DESC)                AS rank_other_users,
    platform,
    high_follower_users,
    high_follower_posts,
    ROUND(avg_high, 1)                                   AS avg_eng_high_followers,
    ROUND(avg_other, 1)                                  AS avg_eng_other_users,
    ROUND(100.0 * (avg_high - avg_other) / avg_other, 2) AS lift_pct
FROM by_platform
ORDER BY rank_high_followers;
