-- Q4: Viral Posts (Statistical Outliers)
-- Finds posts with likes > 2 standard deviations from mean
-- Techniques: CTE, Standard deviation, Z-score

WITH stats AS (
    SELECT
        AVG(likes) AS mean_likes,
        AVG(likes * likes) - AVG(likes) * AVG(likes) AS var_likes
    FROM posts
    WHERE likes IS NOT NULL
),
thresholds AS (
    SELECT
        mean_likes,
        SQRT(var_likes) AS stdev_likes,
        mean_likes + 2 * SQRT(var_likes) AS upper_threshold
    FROM stats
)
SELECT
    p.post_id,
    p.user_id,
    p.platform,
    p.likes,
    p.shares,
    p.comments,
    p.likes + p.shares + p.comments AS total_engagement,
    ROUND((p.likes - t.mean_likes) / t.stdev_likes, 2) AS likes_z_score,
    SUBSTR(p.text_content, 1, 60) AS text_preview
FROM posts p, thresholds t
WHERE p.likes > t.upper_threshold
ORDER BY p.likes DESC
LIMIT 15;
