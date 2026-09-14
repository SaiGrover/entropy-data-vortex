# Phase 2 Insight Report: Analytical Core

**Competition:** Data Vortex | AARUUSH'26  
**Theme:** Rebuilding the Social Engine  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma  
**Date:** September 2026

---

## Executive Summary

This report presents findings from 15 SQL analytical queries executed on the cleaned Social Engine dataset (12,000 posts, 1,500 users, 5 platforms). The analysis covers four dimensions: Trend Detection, Anomaly Discovery, Behavioural Grouping, and Correlation Analysis, supplemented by advanced cross-cutting queries.

---

## 1. Trend Detection

### 1.1 Monthly Post Volume

Post volume remains relatively stable across the 12-month period (May 2024 - April 2025), with counts ranging from **914** (February 2025, lowest) to **1,038** (May 2024, highest).

| Month | Post Count | Growth Rate |
|-------|-----------|------------|
| 2024-05 | 1,038 | -- |
| 2024-08 | 1,015 | +1.9% |
| 2024-10 | 1,029 | +5.6% |
| 2025-02 | 914 | -9.2% |
| 2025-03 | 1,013 | +10.8% |

**Insight:** The largest drop (-9.2%) occurs in February 2025, followed by the largest rebound (+10.8%) in March. This could indicate seasonal patterns or a data collection gap.

### 1.2 Weekly Platform Trends

Rolling 4-week averages smooth out noise and reveal that platform-level engagement is remarkably stable. Facebook's rolling average likes fluctuate between ~2,370 and ~2,640, suggesting no single platform experienced a dramatic engagement shift.

### 1.3 Day-of-Week Patterns

| Day | Avg Total Engagement | Rank |
|-----|---------------------|------|
| Wednesday | 3,683 | 1st |
| Sunday | 3,651 | 2nd |
| Saturday | 3,642 | 3rd |
| Friday | 3,584 | 7th (lowest) |

**Insight:** Mid-week Wednesday leads engagement, while Friday trails. The spread is narrow (99 points between 1st and 7th), indicating that day-of-week is a weak predictor of engagement.

---

## 2. Anomaly Discovery

### 2.1 Viral Post Detection

Using the 2-standard-deviation threshold (mean + 2*stdev), no posts qualified as statistical outliers. This means the engagement distribution is remarkably uniform -- the dataset does not contain extreme viral content. The maximum likes value (5,000) falls within the expected range given the mean (~2,492) and standard deviation (~1,438).

**Insight:** The uniform distribution suggests the Social Engine's data may be synthetically generated with bounded randomness, or the platform has effective engagement normalization mechanisms.

### 2.2 Bot Detection

No users exceeded the 3-posts-per-day threshold. With 12,000 posts across 1,500 users over 364 days, the average is ~0.022 posts per user per day, making high-frequency posting extremely unlikely in this dataset.

### 2.3 Missing Data Analysis

| Completeness | Count | Avg Engagement |
|-------------|-------|----------------|
| Complete | 8,712 | 3,620 |
| Platform Missing | 1,548 | 3,642 |
| Text Missing | 1,504 | 3,685 |
| Both Missing | 236 | 3,399 |

**Insight:** Posts with only platform or only text missing show *slightly higher* engagement than complete posts, while posts missing both fields show lower engagement. This pattern suggests the corruption was largely random (Missing Completely at Random - MCAR), with the "both missing" group being a small exception.

---

## 3. Behavioural Grouping

### 3.1 User Activity Segments

| Segment | Users | Avg Posts | Avg Engagement |
|---------|-------|-----------|----------------|
| Power User | 375 | 11.8 | 3,697 |
| Active | 375 | 8.7 | 3,686 |
| Moderate | 375 | 6.9 | 3,658 |
| Low Activity | 375 | 4.6 | 3,438 |

**Insight:** Power Users produce 2.6x more posts than Low Activity users but only 7.5% higher engagement per post. Volume drives their impact, not per-post quality.

### 3.2 Platform Loyalty

| Dominant Platform | Users | % of Total |
|-------------------|-------|-----------|
| YouTube | 484 | 32.3% |
| Twitter | 331 | 22.1% |
| Reddit | 289 | 19.3% |
| Instagram | 198 | 13.2% |
| Facebook | 198 | 13.2% |

**Insight:** YouTube is the most common "home platform" for users, hosting nearly a third of all dominant-platform users. Instagram and Facebook tie at 13.2% each.

### 3.3 Cross-Platform Behaviour

| Platforms Used | Users | Avg Engagement |
|---------------|-------|----------------|
| 1 | 21 (1.4%) | 3,156 |
| 2 | 148 (9.9%) | 3,574 |
| 3 | 393 (26.2%) | 3,631 |
| 4 | 584 (38.9%) | 3,638 |
| 5 | 354 (23.6%) | 3,640 |

**Insight:** Multi-platform users consistently outperform single-platform users in engagement. The jump from 1 to 2 platforms (+418 avg engagement) is the most significant; returns diminish beyond 3 platforms.

---

## 4. Correlation Analysis

### 4.1 Follower Count vs Engagement

| Bracket | Users | Avg Likes |
|---------|-------|-----------|
| 0-5K | 131 | 2,088 |
| 5K-10K | 156 | 2,073 |
| 10K-20K | 320 | 2,156 |
| 20K-30K | 299 | 2,102 |
| 30K-40K | 301 | 2,108 |
| 40K+ | 293 | 2,071 |

**Insight:** No meaningful correlation exists between follower count and average likes. All brackets cluster within a 85-point range (2,071-2,156), indicating follower count is not a predictor of post engagement on the Social Engine.

### 4.2 Brand Sentiment vs Engagement

Sentiment-engagement patterns vary by brand:
- **Negative outperforms Positive:** Adidas (2,658 vs 2,296), Samsung (2,631 vs 2,480), Pepsi (2,638 vs 2,408)
- **Positive outperforms Negative:** Coca-Cola (2,563 vs 2,461), Nike (2,508 vs 2,372)
- **Near-equal:** Apple (~2,500 across all sentiments), Amazon (~2,540 across all)

**Insight:** Negative sentiment posts often generate higher average likes than positive ones. This "controversy drives engagement" pattern is consistent with real social media dynamics where complaints and critiques attract more attention.

### 4.3 Location-Language Engagement

Top-performing location-language combinations include Dubai-Arabic (4,497), New York-German (4,492), and Sydney-English (4,468). These outliers involve niche communities within locations, suggesting that language minority groups in certain cities may be more engaged.

---

## 5. Advanced Analysis

### 5.1 Cumulative Engagement

Over 12 months, the Social Engine accumulated:
- **25.4 million** total likes
- **12.1 million** total shares
- **6.1 million** total comments

Monthly accumulation is roughly linear, with no acceleration or deceleration, confirming the platform's stable engagement trajectory.

### 5.2 Top Users Per Platform

Each platform has distinct top performers, with no user dominating across multiple platforms. Top per-post engagement ranges from 6,375 to 6,966, approximately 1.9x the overall average. These users tend to have moderate follower counts (15K-45K), reinforcing the finding that follower count alone does not predict engagement.

### 5.3 Account Age

Account maturity shows minimal impact on engagement:
- Accounts < 12 months: 3,602 avg engagement
- Accounts 12-18 months: 3,631 avg engagement
- Accounts 18-24 months: 3,608 avg engagement

**Insight:** Account age is not a meaningful predictor of engagement quality.

---

## Conclusions

1. **Engagement is remarkably uniform** across the dataset -- no viral outliers, no bot patterns, minimal variation by day/platform/follower count.
2. **Multi-platform presence** is the strongest positive correlate with engagement.
3. **Negative sentiment** often drives higher engagement than positive sentiment for brand-related posts.
4. **Missing data appears random** (MCAR), suggesting the corruption was not systematic.
5. **Follower count and account age** are not meaningful predictors of engagement.

## SQL Techniques Used

CTEs, Window Functions (LAG, NTILE, ROW_NUMBER, DENSE_RANK, cumulative SUM, RANK), CASE expressions, COALESCE, HAVING, correlated subqueries, JULIANDAY, strftime, statistical calculations (mean, variance, standard deviation, Z-score).
