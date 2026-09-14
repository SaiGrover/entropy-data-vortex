# SQL Queries - Step-by-Step Guide

## How to Run

Open a terminal in the `Round1-Phase2-Analytical-Core` folder and launch SQLite:

```
sqlite3 Entropy_social_engine.db
```

Then set up readable output:

```sql
.mode column
.headers on
.width auto
```

Now paste any query below directly into the prompt.

When done, type `.quit` to exit.

---

## 1. Schema Overview

```sql
-- See all tables
.tables

-- See table structure
.schema users
.schema posts

-- Quick row counts
SELECT 'users' AS tbl, COUNT(*) AS rows FROM users
UNION ALL
SELECT 'posts', COUNT(*) FROM posts;
```

---

## TREND DETECTION

### Q1: Monthly Post Volume with Growth Rate

Uses: `CTE`, `LAG()`, `strftime()`

```sql
WITH monthly AS (
    SELECT
        strftime('%Y-%m', timestamp) AS month,
        COUNT(*) AS post_count,
        ROUND(AVG(likes), 0) AS avg_likes,
        ROUND(AVG(shares), 0) AS avg_shares,
        ROUND(AVG(comments), 0) AS avg_comments
    FROM posts
    GROUP BY month
),
trends AS (
    SELECT
        month,
        post_count,
        avg_likes,
        avg_shares,
        avg_comments,
        LAG(post_count) OVER (ORDER BY month) AS prev_month_count,
        ROUND(
            (post_count - LAG(post_count) OVER (ORDER BY month)) * 100.0
            / LAG(post_count) OVER (ORDER BY month), 1
        ) AS growth_pct
    FROM monthly
)
SELECT * FROM trends ORDER BY month;
```

**What to look for:** Feb 2025 has the largest drop (-9.2%), Mar 2025 rebounds (+10.8%). Overall volume is stable around 914-1038 posts/month.

---

### Q2: Platform-wise Weekly Engagement (Rolling 4-Week Average)

Uses: `CTE`, `Rolling Window (ROWS BETWEEN)`, `strftime()`

```sql
WITH weekly AS (
    SELECT
        platform,
        strftime('%Y-W%W', timestamp) AS week,
        COUNT(*) AS post_count,
        ROUND(AVG(likes), 0) AS avg_likes
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY platform, week
)
SELECT
    platform,
    week,
    post_count,
    avg_likes,
    ROUND(AVG(avg_likes) OVER (
        PARTITION BY platform
        ORDER BY week
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_4wk_avg_likes
FROM weekly
ORDER BY platform, week;
```

**What to look for:** The rolling average smooths weekly noise. All platforms hover in a tight band, confirming stable engagement.

---

### Q3: Engagement by Day of Week

Uses: `CTE`, `CASE`, `COALESCE`, `RANK()`, `strftime()`

```sql
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
```

**What to look for:** Wednesday peaks (3,683), Friday dips (3,584). The spread is only 99 points (2.7%) -- unusually narrow for real social media.

---

## ANOMALY DISCOVERY

### Q4: Viral Posts (Statistical Outliers)

Uses: `CTE`, `Statistical Calculations (mean, variance, stdev, z-score)`

```sql
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
```

**What to look for:** Empty result! No posts exceed 2 standard deviations above the mean. The engagement distribution is remarkably uniform.

---

### Q5: Suspicious Posting Patterns (Bot Detection)

Uses: `CTE`, `HAVING`, `Correlated Subquery`

```sql
WITH daily_activity AS (
    SELECT
        user_id,
        DATE(timestamp) AS post_date,
        COUNT(*) AS posts_that_day
    FROM posts
    GROUP BY user_id, DATE(timestamp)
    HAVING COUNT(*) > 3
)
SELECT
    d.user_id,
    u.location,
    u.follower_count,
    d.post_date,
    d.posts_that_day,
    (
        SELECT COUNT(*) FROM posts WHERE user_id = d.user_id
    ) AS total_posts
FROM daily_activity d
JOIN users u ON d.user_id = u.user_id
ORDER BY d.posts_that_day DESC
LIMIT 15;
```

**What to look for:** Empty result! No users post more than 3 times/day. No bot-like behaviour detected.

---

### Q6: Missing Data vs Engagement

Uses: `CTE`, `CASE`, `COALESCE`

```sql
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
```

**What to look for:** Engagement is similar across all completeness levels (3399-3685). This confirms corruption was random (MCAR), not systematic.

---

## BEHAVIOURAL GROUPING

### Q7: User Segmentation by Activity Level

Uses: `CTE`, `NTILE()`, `CASE`, `COALESCE`

```sql
WITH user_metrics AS (
    SELECT
        p.user_id,
        u.location,
        u.follower_count,
        COUNT(*) AS total_posts,
        ROUND(AVG(p.likes), 0) AS avg_likes,
        ROUND(AVG(p.shares), 0) AS avg_shares,
        ROUND(AVG(p.comments), 0) AS avg_comments,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement
    FROM posts p
    JOIN users u ON p.user_id = u.user_id
    GROUP BY p.user_id
),
segmented AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY total_posts DESC) AS activity_quartile,
        NTILE(4) OVER (ORDER BY avg_engagement DESC) AS engagement_quartile
    FROM user_metrics
)
SELECT
    CASE activity_quartile
        WHEN 1 THEN 'Power User'
        WHEN 2 THEN 'Active'
        WHEN 3 THEN 'Moderate'
        WHEN 4 THEN 'Low Activity'
    END AS activity_segment,
    COUNT(*) AS user_count,
    ROUND(AVG(total_posts), 1) AS avg_posts,
    ROUND(AVG(avg_engagement), 0) AS avg_engagement,
    ROUND(AVG(follower_count), 0) AS avg_followers,
    MIN(total_posts) AS min_posts,
    MAX(total_posts) AS max_posts
FROM segmented
GROUP BY activity_quartile
ORDER BY activity_quartile;
```

**What to look for:** Power Users average 11.8 posts vs 4.6 for Low Activity, but per-post engagement differs by only 7.5%. Quantity != quality here.

---

### Q8: Platform Preference Clustering

Uses: `CTE`, `ROW_NUMBER()`

```sql
WITH platform_usage AS (
    SELECT
        user_id,
        platform,
        COUNT(*) AS platform_posts,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY COUNT(*) DESC) AS rn
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY user_id, platform
),
dominant AS (
    SELECT user_id, platform AS dominant_platform, platform_posts
    FROM platform_usage
    WHERE rn = 1
)
SELECT
    d.dominant_platform,
    COUNT(*) AS user_count,
    ROUND(AVG(d.platform_posts), 1) AS avg_posts_on_platform,
    ROUND(AVG(u.follower_count), 0) AS avg_followers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT user_id) FROM posts), 1) AS pct_of_users
FROM dominant d
JOIN users u ON d.user_id = u.user_id
GROUP BY d.dominant_platform
ORDER BY user_count DESC;
```

**What to look for:** YouTube dominates (32.3% of users), followed by Twitter (22.1%). Instagram and Facebook tie at 13.2%.

---

### Q9: Cross-Platform Users

Uses: `CTE`, `SUM() OVER`, `COALESCE`

```sql
WITH user_platforms AS (
    SELECT
        user_id,
        COUNT(DISTINCT platform) AS platform_count,
        COUNT(*) AS total_posts,
        ROUND(AVG(COALESCE(likes, 0) + shares + comments), 0) AS avg_engagement
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY user_id
)
SELECT
    platform_count AS platforms_used,
    COUNT(*) AS user_count,
    ROUND(AVG(total_posts), 1) AS avg_total_posts,
    ROUND(AVG(avg_engagement), 0) AS avg_engagement,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_users
FROM user_platforms
GROUP BY platform_count
ORDER BY platform_count;
```

**What to look for:** 38.9% of users post on 4 platforms. 5-platform users have 15% higher engagement than single-platform users (3640 vs 3156).

---

## CORRELATION ANALYSIS

### Q10: Follower Count vs Engagement

Uses: `CTE`, `CASE`, `COALESCE`

```sql
WITH user_eng AS (
    SELECT
        u.user_id,
        u.follower_count,
        ROUND(AVG(COALESCE(p.likes, 0)), 0) AS avg_likes,
        ROUND(AVG(p.shares), 0) AS avg_shares,
        ROUND(AVG(p.comments), 0) AS avg_comments,
        COUNT(*) AS total_posts
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id
)
SELECT
    CASE
        WHEN follower_count < 5000 THEN '0-5K'
        WHEN follower_count < 10000 THEN '5K-10K'
        WHEN follower_count < 20000 THEN '10K-20K'
        WHEN follower_count < 30000 THEN '20K-30K'
        WHEN follower_count < 40000 THEN '30K-40K'
        ELSE '40K+'
    END AS follower_bracket,
    COUNT(*) AS users_in_bracket,
    ROUND(AVG(avg_likes), 0) AS avg_likes,
    ROUND(AVG(avg_shares), 0) AS avg_shares,
    ROUND(AVG(avg_comments), 0) AS avg_comments,
    ROUND(AVG(total_posts), 1) AS avg_posts
FROM user_eng
GROUP BY follower_bracket
ORDER BY MIN(follower_count);
```

**What to look for:** All brackets show nearly identical engagement (~2071-2156 avg likes). Follower count has zero correlation with engagement in this dataset.

---

### Q11: Brand Sentiment vs Engagement

Uses: `CTE`, `CASE`

```sql
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
```

**What to look for:** Negative sentiment often gets MORE likes than positive (e.g., Adidas: 2658 neg vs 2296 pos). This is the "outrage engagement" effect.

---

### Q12: Location-Language Engagement Ranking

Uses: `CTE`, `DENSE_RANK()`, `HAVING`

```sql
WITH loc_lang AS (
    SELECT
        u.location,
        u.language,
        COUNT(*) AS post_count,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        COUNT(DISTINCT p.user_id) AS unique_users
    FROM posts p
    JOIN users u ON p.user_id = u.user_id
    GROUP BY u.location, u.language
    HAVING COUNT(*) >= 10
)
SELECT
    location,
    language,
    unique_users,
    post_count,
    avg_engagement,
    DENSE_RANK() OVER (ORDER BY avg_engagement DESC) AS engagement_rank
FROM loc_lang
ORDER BY engagement_rank
LIMIT 20;
```

**What to look for:** Dubai (Arabic) tops the ranking (4497 avg engagement). Cross-language posting in non-native regions often shows higher engagement.

---

## ADVANCED ANALYSIS

### Q13: Cumulative Engagement Over Time

Uses: `CTE`, `SUM() OVER (ORDER BY)`, `COALESCE`, `strftime()`

```sql
WITH monthly_eng AS (
    SELECT
        strftime('%Y-%m', timestamp) AS month,
        SUM(COALESCE(likes, 0)) AS total_likes,
        SUM(shares) AS total_shares,
        SUM(comments) AS total_comments
    FROM posts
    GROUP BY month
)
SELECT
    month,
    total_likes,
    total_shares,
    total_comments,
    SUM(total_likes) OVER (ORDER BY month) AS cumulative_likes,
    SUM(total_shares) OVER (ORDER BY month) AS cumulative_shares,
    SUM(total_comments) OVER (ORDER BY month) AS cumulative_comments
FROM monthly_eng
ORDER BY month;
```

**What to look for:** Cumulative likes reach ~25.4M by Apr 2025. The near-linear growth confirms steady, uniform engagement over time.

---

### Q14: Top 3 Users per Platform

Uses: `CTE`, `ROW_NUMBER()`, `COALESCE`, `HAVING`

```sql
WITH user_platform_eng AS (
    SELECT
        p.platform,
        p.user_id,
        u.location,
        u.follower_count,
        COUNT(*) AS posts_on_platform,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        ROW_NUMBER() OVER (
            PARTITION BY p.platform
            ORDER BY AVG(COALESCE(p.likes, 0) + p.shares + p.comments) DESC
        ) AS rank_in_platform
    FROM posts p
    JOIN users u ON p.user_id = u.user_id
    WHERE p.platform IS NOT NULL
    GROUP BY p.platform, p.user_id
    HAVING COUNT(*) >= 2
)
SELECT
    platform,
    user_id,
    location,
    follower_count,
    posts_on_platform,
    avg_engagement,
    rank_in_platform
FROM user_platform_eng
WHERE rank_in_platform <= 3
ORDER BY platform, rank_in_platform;
```

**What to look for:** Top performers span diverse locations and follower counts. Reddit's #1 user (Rio de Janeiro, 33K followers) scores 6966 avg engagement.

---

### Q15: Account Age vs Engagement

Uses: `CTE`, `CASE`, `JULIANDAY()`

```sql
WITH user_age AS (
    SELECT
        u.user_id,
        u.account_created,
        CAST((JULIANDAY(AVG(JULIANDAY(p.timestamp))) - JULIANDAY(u.account_created)) / 30 AS INTEGER) AS account_age_months,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        COUNT(*) AS total_posts
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id
)
SELECT
    CASE
        WHEN account_age_months < 12 THEN '< 12 months'
        WHEN account_age_months < 18 THEN '12-18 months'
        WHEN account_age_months < 24 THEN '18-24 months'
        ELSE '24+ months'
    END AS account_age_bucket,
    COUNT(*) AS user_count,
    ROUND(AVG(avg_engagement), 0) AS avg_engagement,
    ROUND(AVG(total_posts), 1) AS avg_posts
FROM user_age
GROUP BY account_age_bucket
ORDER BY MIN(account_age_months);
```

**What to look for:** All age buckets show similar engagement (3602-3815). Account maturity does not predict success in this dataset.

---

## EXTENDED ANALYSIS

### Q16: User Cohort Analysis by Account Creation Quarter

Uses: `CTE`, `CASE` cohort bucketing, `SUM() OVER()` for percentages, `COUNT(DISTINCT)`

```sql
.mode column
.headers on

-- Q16: User Cohort Analysis by Account Creation Quarter
-- Techniques: CTE, CASE cohort bucketing, window SUM for percentages
WITH user_cohorts AS (
    SELECT user_id,
        CASE
            WHEN account_created < '2023-04-01' THEN 'Q1-2023'
            WHEN account_created < '2023-07-01' THEN 'Q2-2023'
            WHEN account_created < '2023-10-01' THEN 'Q3-2023'
            ELSE 'Q4-2023'
        END AS cohort
    FROM users
),
cohort_metrics AS (
    SELECT c.cohort, COUNT(DISTINCT c.user_id) AS users,
        COUNT(p.post_id) AS total_posts,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_engagement,
        ROUND(1.0 * COUNT(p.post_id) / COUNT(DISTINCT c.user_id), 1) AS posts_per_user,
        COUNT(DISTINCT p.platform) AS platforms_used
    FROM user_cohorts c JOIN posts p ON c.user_id = p.user_id
    GROUP BY c.cohort
)
SELECT cohort, users, total_posts, posts_per_user, avg_engagement, platforms_used,
    ROUND(100.0 * users / SUM(users) OVER (), 1) AS pct_of_total
FROM cohort_metrics ORDER BY cohort;
```

**Why this technique:** CASE bucketing groups continuous dates into discrete cohorts; the window SUM computes each cohort's share of total without a subquery.

**What to look for:** All cohorts show identical engagement and posts-per-user, confirming the data was generated uniformly across time periods rather than reflecting real-world cohort effects.

---

### Q17: Text Pattern Analysis via SQL

Uses: `CASE` with `LIKE`, `LENGTH()`, string functions, `GROUP BY`

```sql
.mode column
.headers on

-- Q17: Text Pattern Analysis via SQL
-- Techniques: CASE + LIKE, LENGTH(), string functions
SELECT
    CASE
        WHEN text_content LIKE 'Just unboxed%' THEN 'Unboxing'
        WHEN text_content LIKE 'My one-%' OR text_content LIKE 'My one %' THEN 'Review'
        WHEN text_content LIKE 'Just saw an ad%' THEN 'Ad Reaction'
        WHEN text_content LIKE 'Comparing%' THEN 'Comparison'
        WHEN text_content LIKE 'Fed up%' THEN 'Complaint'
        WHEN text_content LIKE 'Super excited%' THEN 'Excitement'
        ELSE 'Other'
    END AS template_type,
    COUNT(*) AS post_count,
    ROUND(AVG(LENGTH(text_content)), 0) AS avg_char_length,
    ROUND(AVG(COALESCE(likes, 0)), 0) AS avg_likes,
    ROUND(AVG(shares), 0) AS avg_shares,
    MIN(LENGTH(text_content)) AS min_length,
    MAX(LENGTH(text_content)) AS max_length
FROM posts WHERE text_content IS NOT NULL
GROUP BY template_type ORDER BY post_count DESC;
```

**Why this technique:** LIKE pattern matching at the start of text_content identifies recurring templates; LENGTH() reveals whether templates produce uniform or variable-length text.

**What to look for:** Posts cluster into identifiable templates (Unboxing, Review, etc.). Engagement does not vary meaningfully by template type, reinforcing that content type has no influence on engagement in this dataset.

---

### Q18: Self-Join -- Finding User "Twins"

Uses: `Self-join`, `ABS()`, `HAVING`, inequality join (`a.user_id < b.user_id`)

```sql
.mode column
.headers on

-- Q18: Self-Join -- Finding User "Twins"
-- Techniques: Self-join, ABS(), inequality join
WITH user_stats AS (
    SELECT p.user_id, u.location, COUNT(*) AS total_posts,
        ROUND(AVG(COALESCE(p.likes, 0) + p.shares + p.comments), 0) AS avg_eng,
        COUNT(DISTINCT p.platform) AS platforms
    FROM posts p JOIN users u ON p.user_id = u.user_id
    GROUP BY p.user_id HAVING COUNT(*) >= 5
)
SELECT a.user_id AS user_a, b.user_id AS user_b,
    a.avg_eng AS eng_a, b.avg_eng AS eng_b,
    ABS(a.avg_eng - b.avg_eng) AS eng_diff,
    a.total_posts AS posts_a, b.total_posts AS posts_b,
    a.location AS loc_a, b.location AS loc_b
FROM user_stats a JOIN user_stats b
    ON a.user_id < b.user_id
    AND ABS(a.avg_eng - b.avg_eng) <= 50
    AND a.total_posts = b.total_posts
    AND a.platforms = b.platforms
ORDER BY eng_diff LIMIT 15;
```

**Why this technique:** The inequality join `a.user_id < b.user_id` avoids duplicate pairs (A,B vs B,A) and self-matches. ABS() measures engagement distance between users.

**What to look for:** Abundant near-identical user pairs appear (same post count, same platform count, engagement within 50 points). This abundance of "twins" is a strong signal of uniform data generation rather than organic user behaviour.

---

## Quick Reference

| Query | Category | Key Technique | Result |
|-------|----------|---------------|--------|
| Q1 | Trend | LAG() | Stable volume, Feb dip |
| Q2 | Trend | Rolling Window | Smooth cross-platform |
| Q3 | Trend | RANK() | Wed best, Fri worst |
| Q4 | Anomaly | Stdev/Z-score | No viral posts |
| Q5 | Anomaly | Correlated Subquery | No bots |
| Q6 | Anomaly | CASE + COALESCE | Corruption was random |
| Q7 | Grouping | NTILE() | 4 user segments |
| Q8 | Grouping | ROW_NUMBER() | YouTube dominates |
| Q9 | Grouping | SUM() OVER | Multi-platform = better |
| Q10 | Correlation | CASE buckets | Followers don't matter |
| Q11 | Correlation | LIKE + CASE | Outrage engagement |
| Q12 | Correlation | DENSE_RANK() | Dubai/Arabic #1 |
| Q13 | Advanced | Cumulative SUM | Linear growth |
| Q14 | Advanced | ROW_NUMBER() | Top 3 per platform |
| Q15 | Advanced | JULIANDAY() | Age irrelevant |
| Q16 | Extended | CTE + CASE cohort | Cohorts identical |
| Q17 | Extended | LIKE + LENGTH() | Templates detected |
| Q18 | Extended | Self-join + ABS() | Abundant user twins |
