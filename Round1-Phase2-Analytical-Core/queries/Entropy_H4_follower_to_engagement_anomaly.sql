-- H4: Follower-to-Engagement Anomaly
-- Users with fewer than 5,000 followers whose total post engagement places
-- them in the top 10% of all users.
--
-- Level 1  impute:   a missing like count is replaced by that user's own
--                    average likes (global average if they have none), so a
--                    corrupted value neither erases a post nor penalises
--                    whichever users happened to be corrupted more often.
-- Level 2  aggregate: roll posts up to users (total and per-post engagement).
-- Level 3  rank:     decile every user twice, by total and by per-post
--                    engagement; user_id breaks ties so results are
--                    deterministic.
-- Level 4  filter:   top total decile AND fewer than 5,000 followers, then
--                    classify each survivor by whether their per-post
--                    engagement is also top-decile.

WITH user_like_avg AS (
    SELECT user_id, AVG(likes) AS avg_likes
    FROM posts
    GROUP BY user_id
),
global_like_avg AS (
    SELECT AVG(likes) AS avg_likes FROM posts
),
post_engagement AS (
    SELECT
        p.user_id,
        p.likes IS NULL                                                   AS likes_imputed,
        COALESCE(p.likes, ula.avg_likes, g.avg_likes) + p.shares + p.comments AS engagement
    FROM posts p
    JOIN user_like_avg ula ON ula.user_id = p.user_id
    CROSS JOIN global_like_avg g
),
user_engagement AS (
    SELECT
        u.user_id,
        u.location,
        u.follower_count,
        COUNT(*)              AS post_count,
        SUM(pe.likes_imputed) AS imputed_posts,
        SUM(pe.engagement)    AS total_engagement,
        AVG(pe.engagement)    AS avg_engagement_per_post
    FROM users u
    JOIN post_engagement pe ON pe.user_id = u.user_id
    GROUP BY u.user_id, u.location, u.follower_count
),
ranked_users AS (
    SELECT
        *,
        NTILE(10)      OVER (ORDER BY total_engagement DESC, user_id)        AS total_decile,
        NTILE(10)      OVER (ORDER BY avg_engagement_per_post DESC, user_id) AS per_post_decile,
        PERCENT_RANK() OVER (ORDER BY total_engagement DESC)                 AS pct_rank
    FROM user_engagement
)
SELECT
    RANK() OVER (ORDER BY total_engagement DESC)   AS anomaly_rank,
    user_id,
    location,
    follower_count,
    post_count,
    imputed_posts,
    ROUND(total_engagement, 0)                     AS total_engagement,
    ROUND(avg_engagement_per_post, 1)              AS avg_eng_per_post,
    ROUND(100.0 * pct_rank, 2)                     AS top_pct_of_users,
    per_post_decile,
    CASE WHEN per_post_decile = 1
         THEN 'Exceptional per post'
         ELSE 'Volume-driven' END                  AS classification
FROM ranked_users
WHERE total_decile   = 1        -- top 10% of all users by total engagement
  AND follower_count < 5000     -- ...despite a small audience
ORDER BY total_engagement DESC;
