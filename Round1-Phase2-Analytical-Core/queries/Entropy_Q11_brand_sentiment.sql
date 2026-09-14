-- Q11: Brand Sentiment vs Engagement Correlation
-- Compares engagement for positive vs negative posts across 10 brands
-- Techniques: CTE, LIKE pattern matching, CASE sentiment

WITH brand_posts AS (
    SELECT
        post_id,
        likes,
        shares,
        comments,
        text_content,
        CASE
            WHEN text_content LIKE '%Nike%' THEN 'Nike'
            WHEN text_content LIKE '%Adidas%' THEN 'Adidas'
            WHEN text_content LIKE '%Apple%' THEN 'Apple'
            WHEN text_content LIKE '%Samsung%' THEN 'Samsung'
            WHEN text_content LIKE '%Amazon%' THEN 'Amazon'
            WHEN text_content LIKE '%Google%' THEN 'Google'
            WHEN text_content LIKE '%Toyota%' THEN 'Toyota'
            WHEN text_content LIKE '%Microsoft%' THEN 'Microsoft'
            WHEN text_content LIKE '%Pepsi%' THEN 'Pepsi'
            WHEN text_content LIKE '%Coca-Cola%' THEN 'Coca-Cola'
        END AS brand,
        CASE
            WHEN text_content LIKE '%loving it%' OR text_content LIKE '%best purchase%'
                 OR text_content LIKE '%highly recommend%' OR text_content LIKE '%worth every penny%'
                 OR text_content LIKE '%exceeded%' OR text_content LIKE '%amazing%'
            THEN 'Positive'
            WHEN text_content LIKE '%disappointed%' OR text_content LIKE '%returning it%'
                 OR text_content LIKE '%not worth%' OR text_content LIKE '%wouldn''t recommend%'
                 OR text_content LIKE '%bummed out%'
            THEN 'Negative'
            ELSE 'Neutral/Mixed'
        END AS sentiment
    FROM posts
    WHERE text_content IS NOT NULL
)
SELECT
    brand,
    sentiment,
    COUNT(*) AS post_count,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(shares), 0) AS avg_shares,
    ROUND(AVG(comments), 0) AS avg_comments
FROM brand_posts
WHERE brand IS NOT NULL
GROUP BY brand, sentiment
ORDER BY brand, sentiment;
