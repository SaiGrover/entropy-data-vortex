-- H4: Follower-to-Engagement Anomaly
-- Users with fewer than 5,000 followers whose total post engagement places
-- them in the top 10% of all users.
--
-- Level 1: aggregate every post to its author (total engagement per user).
-- Level 2: rank every user against the whole population (decile + percentile).
-- Level 3: keep the top decile, then apply the low-follower filter.
--
-- Missing likes are treated as 0 (COALESCE) so that a corrupted like count
-- never removes a whole post's shares and comments from a user's total.

WITH user_engagement AS (
    SELECT
        u.user_id,
        u.location,
        u.follower_count,
        COUNT(p.post_id)                                        AS post_count,
        SUM(COALESCE(p.likes, 0) + p.shares + p.comments)       AS total_engagement
    FROM users u
    JOIN posts p ON p.user_id = u.user_id
    GROUP BY u.user_id, u.location, u.follower_count
),
ranked_users AS (
    SELECT
        *,
        NTILE(10)      OVER (ORDER BY total_engagement DESC)     AS engagement_decile,
        PERCENT_RANK() OVER (ORDER BY total_engagement DESC)     AS pct_rank,
        COUNT(*)       OVER ()                                   AS total_users
    FROM user_engagement
)
SELECT
    RANK() OVER (ORDER BY total_engagement DESC)                 AS rank_among_anomalies,
    user_id,
    location,
    follower_count,
    post_count,
    total_engagement,
    ROUND(total_engagement * 1.0 / post_count, 1)                AS avg_engagement_per_post,
    ROUND(100.0 * pct_rank, 2)                                   AS top_percentile
FROM ranked_users
WHERE engagement_decile = 1          -- top 10% of all users by total engagement
  AND follower_count  < 5000         -- ...despite a small audience
ORDER BY total_engagement DESC;
