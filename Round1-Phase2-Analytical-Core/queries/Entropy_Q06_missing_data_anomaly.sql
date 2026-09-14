-- Q6: Posts with Missing Data Anomaly
-- Compares engagement between complete posts and posts missing key fields
-- Techniques: CASE, COALESCE, Aggregation

SELECT
    CASE
        WHEN platform IS NULL AND text_content IS NULL THEN 'Both Missing'
        WHEN platform IS NULL THEN 'Platform Missing'
        WHEN text_content IS NULL THEN 'Text Missing'
        ELSE 'Complete'
    END AS data_completeness,
    COUNT(*) AS post_count,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(shares), 0) AS avg_shares,
    ROUND(AVG(comments), 0) AS avg_comments,
    ROUND(AVG(COALESCE(likes, 0) + shares + comments), 0) AS avg_total_engagement
FROM posts
GROUP BY data_completeness
ORDER BY post_count DESC;
