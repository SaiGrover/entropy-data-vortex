-- Q3: Engagement Trend by Day of Week
-- Determines which days generate the highest total engagement
-- Techniques: CASE, RANK() window function, strftime

SELECT
    CASE CAST(strftime('%w', timestamp) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    COUNT(*) AS total_posts,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(shares), 0) AS avg_shares,
    ROUND(AVG(comments), 0) AS avg_comments,
    ROUND(AVG(COALESCE(likes, 0) + shares + comments), 0) AS avg_total_engagement,
    RANK() OVER (ORDER BY AVG(COALESCE(likes, 0) + shares + comments) DESC) AS engagement_rank
FROM posts
GROUP BY strftime('%w', timestamp)
ORDER BY engagement_rank;
