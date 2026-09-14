# Round 1 - Phase 2: Analytical Core

**Competition:** Data Vortex | AARUUSH'26  
**Theme:** Rebuilding the Social Engine  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Objective

Perform SQL-based analytical reasoning on the cleaned Social Engine dataset. This phase converts the cleaned CSV data into a relational SQLite database and solves 18 analytical queries across 6 categories: Trend Detection, Anomaly Discovery, Behavioural Grouping, Correlation Analysis, Advanced Analysis, and Extended Analysis.

## Database Schema

Two-table normalized schema with referential integrity, CHECK constraints, indexes, and a convenience view:

```sql
users (Parent Table)
  user_id         TEXT PRIMARY KEY
  location        TEXT NOT NULL
  language        TEXT NOT NULL
  account_created DATE NOT NULL
  follower_count  INTEGER NOT NULL  CHECK (follower_count >= 0)

posts (Detail Table)
  post_id      TEXT PRIMARY KEY
  user_id      TEXT NOT NULL  -> REFERENCES users(user_id)
  platform     TEXT           -- nullable (corrupted data)
  text_content TEXT           -- nullable (corrupted data)
  timestamp    DATETIME NOT NULL
  likes        INTEGER       CHECK (likes >= 0)   -- nullable (corrupted data)
  shares       INTEGER NOT NULL  CHECK (shares >= 0)
  comments     INTEGER NOT NULL  CHECK (comments >= 0)

-- Foreign key enforcement
PRAGMA foreign_keys = ON;

-- Performance indexes
idx_posts_user_id     ON posts(user_id)
idx_posts_timestamp   ON posts(timestamp)
idx_posts_platform    ON posts(platform)
idx_users_language    ON users(language)
idx_users_location    ON users(location)

-- Convenience view for common join pattern
CREATE VIEW user_posts AS
  SELECT p.*, u.location, u.language, u.account_created, u.follower_count
  FROM posts p JOIN users u ON p.user_id = u.user_id;
```

## SQL Queries

### Category 1: Trend Detection (Q1-Q3)

| # | Query | Techniques | Purpose |
|---|-------|-----------|---------|
| Q1 | Monthly Post Volume with Growth Rate | CTE, `LAG()` window function | Identify months with highest/lowest activity and month-over-month percentage change |
| Q2 | Platform-wise Weekly Engagement Trend | CTE, Rolling window (`ROWS BETWEEN 3 PRECEDING AND CURRENT ROW`) | Track how average engagement evolves week-by-week for each platform with 4-week rolling average |
| Q3 | Engagement Trend by Day of Week | `CASE`, `RANK()` window function, `strftime('%w')` | Determine which days of the week generate the highest total engagement |

### Category 2: Anomaly Discovery (Q4-Q6)

| # | Query | Techniques | Purpose |
|---|-------|-----------|---------|
| Q4 | Viral Posts (Statistical Outliers) | CTE, Standard deviation calculation, Z-score | Find posts with engagement > 2 standard deviations from mean (potential viral content) |
| Q5 | Suspicious Posting Patterns (Bot Detection) | CTE, `HAVING`, Correlated subquery | Identify users posting > 3 times per day, suggesting automated/bot accounts |
| Q6 | Missing Data Anomaly Analysis | `CASE`, `COALESCE`, Aggregation | Compare engagement between complete posts and posts missing platform/text to detect non-random corruption |

### Category 3: Behavioural Grouping (Q7-Q9)

| # | Query | Techniques | Purpose |
|---|-------|-----------|---------|
| Q7 | User Segmentation by Activity Level | CTE, `NTILE(4)` window function | Classify users into Power User / Active / Moderate / Low Activity quartile-based segments |
| Q8 | Platform Preference Clustering | CTE, `ROW_NUMBER()` partitioned by user | Group users by their dominant (most-posted-on) platform to understand platform loyalty |
| Q9 | Cross-Platform Users | CTE, `COUNT(DISTINCT)`, `SUM() OVER()` | Measure how many platforms each user posts on and whether multi-platform users are more engaged |

### Category 4: Correlation Analysis (Q10-Q12)

| # | Query | Techniques | Purpose |
|---|-------|-----------|---------|
| Q10 | Follower Count vs Average Engagement | CTE, `CASE` bucketing | Bucket users by follower count ranges and compare average engagement per bracket |
| Q11 | Brand Sentiment vs Engagement | CTE, `LIKE` pattern matching, `CASE` sentiment classification | Compare engagement for positive vs negative posts across 10 major brands |
| Q12 | Location-Language Engagement Heatmap | CTE, `DENSE_RANK()`, `HAVING` | Rank location-language combinations by average total engagement |

### Category 5: Advanced Analysis (Q13-Q15)

| # | Query | Techniques | Purpose |
|---|-------|-----------|---------|
| Q13 | Cumulative Engagement Over Time | `SUM() OVER (ORDER BY)` cumulative window | Track running totals of likes, shares, comments across the entire timeline |
| Q14 | Top Performing Users per Platform | CTE, `ROW_NUMBER()` partitioned by platform | For each platform, identify the top 3 users by average engagement |
| Q15 | Account Age vs Engagement | CTE, `JULIANDAY()`, `CASE` bucketing | Test whether account maturity correlates with higher post engagement |

### Category 6: Extended Analysis (Q16-Q18)

| # | Query | Techniques | Purpose |
|---|-------|-----------|---------|
| Q16 | User Cohort Analysis by Account Creation Quarter | CTE, `CASE` cohort bucketing, `SUM() OVER()` for percentage, `COUNT(DISTINCT)` | Compare posting behaviour across account creation cohorts |
| Q17 | Text Pattern Analysis via SQL | `CASE` with `LIKE`, `LENGTH()`, string functions, `GROUP BY` | Reverse-engineer text templates using pure SQL string functions |
| Q18 | Self-Join -- Finding User "Twins" | Self-join, `ABS()`, `HAVING`, inequality join (`a.user_id < b.user_id`) | Find user pairs with nearly identical posting patterns |

## Key Insights

1. **Stable Volume:** Monthly post counts range from 914 to 1,038, with February 2025 as the lowest and May 2024 as the highest.
2. **Wednesday Peak:** Wednesday has the highest average total engagement (3,683), Friday the lowest (3,584).
3. **Missing Data is Random:** Posts with missing platform/text show similar engagement to complete posts, suggesting corruption was random rather than systematic.
4. **Activity Segmentation:** Power Users (top 25%) average 11.8 posts each; Low Activity users average 4.6 posts.
5. **YouTube Dominance:** 32.3% of users have YouTube as their dominant platform.
6. **Multi-Platform Benefit:** Users on all 5 platforms have higher engagement than single-platform users.
7. **Follower Count Irrelevant:** No meaningful correlation between follower count brackets and average engagement.
8. **Brand Sentiment Mixed:** Negative sentiment posts sometimes outperform positive ones (e.g., Adidas negative avg 2,658 vs positive avg 2,296).
9. **Global Engagement:** Top location-language pairs include Dubai-Arabic (4,497 avg engagement) and New York-German (4,492).
10. **Cumulative Growth:** Total cumulative likes reached 25.4M over 12 months.
11. **Cohort Uniformity:** All account creation cohorts (Q1-Q4 2023) show identical engagement patterns, confirming stationary data generation.
12. **Template Detection:** Posts follow identifiable text templates (Unboxing, Review, Ad Reaction, etc.); engagement does not vary by template type.
13. **User Twins:** Abundant near-identical user pairs exist (matching post counts, platform counts, and engagement within 50 points), confirming uniform generation.

## File Structure

```
Round1-Phase2-Analytical-Core/
|-- Entropy_01_SQL_Analysis.ipynb         # SQL analysis notebook with all 18 queries
|-- Entropy_social_engine.db              # SQLite database
|-- queries/                      # Individual SQL query files
|   |-- Entropy_Q01_monthly_volume_trend.sql
|   |-- Entropy_Q02_platform_weekly_engagement.sql
|   |-- Entropy_Q03_day_of_week_engagement.sql
|   |-- Entropy_Q04_viral_posts_outliers.sql
|   |-- Entropy_Q05_bot_detection.sql
|   |-- Entropy_Q06_missing_data_anomaly.sql
|   |-- Entropy_Q07_user_segmentation.sql
|   |-- Entropy_Q08_platform_preference.sql
|   |-- Entropy_Q09_cross_platform_users.sql
|   |-- Entropy_Q10_follower_vs_engagement.sql
|   |-- Entropy_Q11_brand_sentiment.sql
|   |-- Entropy_Q12_location_language_heatmap.sql
|   |-- Entropy_Q13_cumulative_engagement.sql
|   |-- Entropy_Q14_top_users_per_platform.sql
|   |-- Entropy_Q15_account_age_vs_engagement.sql
|   |-- Q16_user_cohort_analysis.sql
|   |-- Q17_text_pattern_analysis.sql
|   |-- Q18_user_twins_self_join.sql
|-- images/                       # SQL output screenshots
|-- Entropy_Phase2_Insight_Report.pdf      # Comprehensive insight report (PDF)
|-- Entropy_Phase2_Insight_Report.md      # Insight report source (Markdown)
|-- Entropy_README.md                     # This file
```

## Submission Checklist

- [x] SQL queries (18 analytical queries) - `Entropy_01_SQL_Analysis.ipynb` + `queries/`
- [x] Output screenshots - `images/`
- [x] Logic explanation for each query with "Why this technique" annotations - documented in notebook markdown cells
- [x] Post-query "What This Means" interpretations for every query
- [x] Schema constraints verified (PKs, FKs, NOT NULL, CHECK constraints, indexes)
- [x] COALESCE consistency across all queries
- [x] Phase 2 Insight Report (PDF) - `Entropy_Phase2_Insight_Report.pdf`
- [x] Database file - `Entropy_social_engine.db`

## Tools & Libraries

- Python 3.x, Jupyter Notebook
- sqlite3 (database engine)
- pandas (query execution and display)
- SQL techniques: CTEs, Window Functions (LAG, NTILE, ROW_NUMBER, DENSE_RANK, SUM OVER), CASE expressions, subqueries, HAVING, COALESCE, Self-joins, SQL string functions (LENGTH, SUBSTR, INSTR)
