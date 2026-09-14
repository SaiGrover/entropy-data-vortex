# Round 1 - Phase 1: Data Recovery

**Competition:** Data Vortex | AARUUSH'26  
**Theme:** Rebuilding the Social Engine  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Objective

Recover, clean, and explore the corrupted Social Engine dataset. The dataset was hidden behind an interactive recovery terminal on the competition website and contained multiple corruption patterns that needed systematic identification and repair.

## Dataset Source

- **Website:** `https://datavortex-social-engine.vercel.app`
- **Recovery Process:** Enter Recovery Mode -> Authenticate (Operator ID + Access Key) -> Recovery Shell -> `connect node_07` -> Archive Node 07
- **Raw Files Downloaded:**
  - `Entropy_Social_Engine_Posts_Corrupted.csv` (~12,360 rows, 8 columns)
  - `Entropy_Social_Engine_Users.csv` (1,500 rows, 5 columns)

## Data Cleaning Pipeline

The cleaning notebook (`Entropy_01_Data_Cleaning.ipynb`) applies **10 transformation steps** in sequence. Each step includes a written justification explaining **why** the transformation is necessary and **what alternative approaches** were considered. Every step is followed by a **before/after example cell** showing the exact transformation applied, and the notebook concludes with **validation cells** (user_id pattern check, date range validation, post-correction range verification).

| Step | Transformation | Records Affected | Justification |
|------|---------------|-----------------|---------------|
| 1 | Replace literal `"NULL"` strings with NaN | 24 in text_content | Database serialization artifact -- SQL NULL keyword written as string during corrupted export |
| 2 | Remove exact duplicate rows | 360 duplicates removed | All 8 columns match (including unique post_id) -- replication errors, not legitimate posts |
| 3 | Decode HTML entities (`&amp;`, `<br>`, `<div>`) | 974 text entries | Web frontend rendering artifacts leaking into the data store |
| 4 | Fix mojibake (UTF-8 interpreted as Latin-1) | 306 occurrences | Classic encoding mismatch -- recovers original Unicode characters (e.g., accented letters) |
| 5 | Standardize 3 timestamp formats to datetime | 12,000 timestamps | Unix epoch, ISO 8601, DD-MM-YYYY all unified to datetime64 |
| 6 | Fix negative likes (absolute value) | 509 records | Sign-bit corruption -- magnitudes preserved, only sign flipped. Dropping would lose 4.2% of data unnecessarily |
| 7 | Retain missing platforms as NaN | 1,784 records | No imputation basis exists; engagement is statistically identical for missing vs known platform (Mann-Whitney U, p=0.64) |
| 8 | Standardize empty text to NaN | 1,711 entries | Empty strings and whitespace unified as NaN for consistent null-handling |
| 9 | Strip leading/trailing whitespace | All text columns | Prevents false mismatches in joins and groupby operations |
| 10 | Final validation and export | All columns | Referential integrity check, type casting, cleaned CSV export |

**Result:** 12,000 clean rows exported (360 duplicates removed from 12,360 original).

### Cleaning Assumptions

1. **"NULL" strings are missing data** -- the literal text `NULL` is a database serialization artifact, not valid content.
2. **Duplicate rows are replication errors** -- exact duplicates across all 8 columns (including unique post_id) cannot be legitimate.
3. **Negative likes are sign-bit corruption** -- social media likes cannot be negative; absolute value recovers the true count (magnitude preserved).
4. **HTML artifacts are rendering leakage** -- `&amp;`, `<br>`, `<div>` come from the web layer, not user-authored content.
5. **Mojibake is UTF-8/Latin-1 confusion** -- standard encoding mismatch; recovered to original Unicode characters.
6. **Missing platforms are genuinely unknown** -- no secondary signal to infer platform (Kruskal-Wallis p=0.37 confirms platforms are engagement-equivalent). Imputation would fabricate data.
7. **All timestamp formats share the same timezone** -- parsed uniformly without timezone adjustment.

## EDA Report

The EDA notebook (`Entropy_02_EDA_Report.ipynb`) produces **20 analytical sections** with **21 visualizations** and **6 formal statistical significance tests**.

A standalone **PDF report** (`Entropy_Phase1_EDA_Report.pdf`) provides written explanations for every graph, its purpose, and what the results mean.

### Sections

| # | Section | Visualizations | Key Finding |
|---|---------|---------------|-------------|
| 1 | Dataset Overview | -- | 12,000 posts, 1,500 users, 364-day span |
| 2 | Platform Distribution | 2 | Near-uniform distribution (~2,000/platform); 14.9% missing |
| 3 | Engagement by Platform | 1 | Platform choice does NOT affect engagement (Kruskal-Wallis p=0.37) |
| 4 | Monthly Post Volume | 1 | Stable 914-1,038/month; Feb 2025 dip (-9.2%), Mar rebound (+10.8%) |
| 5 | Day-of-Week & Hourly Patterns | 2 | <6% temporal variation -- unusually flat for social media |
| 6 | Engagement Distributions | 1 | Uniform (not power-law); mean~median confirms symmetry |
| 7 | Engagement Correlation | 1 | Metrics are independent (r < 0.01 between all pairs) |
| 8 | User Activity | 1 | Mean 8.0 posts/user; follower count has zero predictive power |
| 9 | Geographic Analysis | 1 | 33 cities across 6 continents; no location dominates engagement |
| 10 | Language Analysis | 1 | 10 languages, 119-168 users each; engagement is language-independent |
| 11 | Hashtag Analysis | 1 | Top: #Fashion, #Sale, #Tech, #Health (consumer-focused themes) |
| 12 | Brand Analysis | 1 | 10 brands with ~1,000 mentions each; no brand drives more engagement |
| 13 | Sentiment Indicators | 1 | Contradictory sentiment detected (template-based text generation) |
| 14 | Anomaly Detection | 1 | Zero outliers by IQR method; no viral content exists |
| 15 | Missing Data Analysis | 1 | MCAR confirmed; corruption was random, not systematic |
| 16 | Statistical Significance Tests | -- | 5 formal tests (Kruskal-Wallis, Chi-square, Spearman, Mann-Whitney U) |
| 17 | Brand x Platform Cross-Analysis | 1 | No brand-platform affinity; uniform assignment |
| 18 | Text Length Analysis | 1 | ~18-20 words/post; length does not predict engagement |
| 19 | Coefficient of Variation | 1 | Most metrics CV < 10%; formal proof of structural uniformity |
| 20 | Contradictory Sentiment Deep Dive | 1 | Template reverse-engineering; phrase co-occurrence analysis |
| 21 | Multi-Brand Posts & Engagement | 1 | Brand density vs engagement; Mann-Whitney U test |
| 22 | Analytical Narrative | -- | Connects all findings; synthetic-vs-real comparison table |

### Key Findings

- **12,000 posts** from **1,500 users** across **5 platforms**
- Date range: May 2024 -- April 2025 (364 days)
- Average engagement: 2,492 likes | 1,007 shares | 504 comments
- ~15% missing data across platform, text, and likes columns (confirmed MCAR)
- Weak correlation between engagement metrics (semi-independent)
- Top brands mentioned: Nike, Samsung, Amazon, Toyota, Google, Apple
- **5 of 6 statistical tests return p > 0.05** -- conventional factors do not predict engagement
- **One significant finding:** multi-platform users show ~15% higher engagement (Kruskal-Wallis, p<0.05)
- Template-based text generation confirmed via contradictory sentiment deep dive

## File Structure

```
Round1-Phase1-Data-Recovery/
|-- Entropy_01_Data_Cleaning.ipynb           # Data cleaning pipeline (10 justified steps)
|-- Entropy_02_EDA_Report.ipynb              # EDA (20 sections, 21 visualizations, 6 stat tests)
|-- Entropy_Phase1_EDA_Report.pdf            # Standalone PDF report with graph explanations
|-- Entropy_Social_Engine_Posts_Corrupted.csv # Original corrupted dataset
|-- Entropy_Social_Engine_Users.csv          # Original users dataset
|-- Entropy_Social_Engine_Posts_Cleaned.csv  # Cleaned posts (12,000 rows)
|-- Entropy_Social_Engine_Users_Cleaned.csv  # Cleaned users (1,500 rows)
|-- Entropy_Social_Engine_Cleaned.csv        # Single merged submission file (posts LEFT JOIN users on user_id; 12,000 rows x 12 cols)
|-- Entropy_cleaning_log.txt                 # Detailed log of all transformations
|-- Entropy_generate_eda_pdf.py              # Script to regenerate the PDF report
|-- images/                          # All visualizations (21 PNGs)
|   |-- Entropy_corruption_catalog.png
|   |-- Entropy_data_quality_scorecard.png
|   |-- Entropy_eda_platform_distribution.png
|   |-- Entropy_eda_engagement_by_platform.png
|   |-- Entropy_eda_monthly_posts.png
|   |-- Entropy_eda_temporal_patterns.png
|   |-- Entropy_eda_engagement_distributions.png
|   |-- Entropy_eda_engagement_correlation.png
|   |-- Entropy_eda_user_activity.png
|   |-- Entropy_eda_geographic.png
|   |-- Entropy_eda_language.png
|   |-- Entropy_eda_top_hashtags.png
|   |-- Entropy_eda_brand_analysis.png
|   |-- Entropy_eda_sentiment.png
|   |-- Entropy_eda_anomalies.png
|   |-- Entropy_eda_missing_patterns.png
|   |-- Entropy_eda_brand_platform_heatmap.png
|   |-- Entropy_eda_text_length_analysis.png
|   |-- Entropy_eda_coefficient_of_variation.png
|   |-- Entropy_eda_contradictory_sentiment_deep_dive.png
|   |-- Entropy_eda_multi_brand_engagement.png
|-- Entropy_README.md                        # This file
```

## Submission Checklist

- [x] Cleaned dataset (single CSV) -- `Entropy_Social_Engine_Cleaned.csv` (posts joined with users on `user_id`)
- [x] Cleaned source tables -- `Entropy_Social_Engine_Posts_Cleaned.csv`, `Entropy_Social_Engine_Users_Cleaned.csv`
- [x] EDA report with visualizations -- `Entropy_02_EDA_Report.ipynb` + `images/`
- [x] **PDF EDA report with explanations** -- `Entropy_Phase1_EDA_Report.pdf`
- [x] Well-documented code notebook -- `Entropy_01_Data_Cleaning.ipynb` (each step justified)
- [x] Cleaning assumptions documented in notebook (Section 8)
- [x] Transformation log -- `Entropy_cleaning_log.txt`
- [x] Statistical significance tests (6 formal hypothesis tests, including 1 significant finding)
- [x] Coefficient of Variation analysis (formal uniformity quantification)
- [x] Contradictory sentiment deep dive (template reverse-engineering)
- [x] Analytical narrative connecting all findings

## Tools & Libraries

- Python 3.x, Jupyter Notebook
- pandas, numpy (data manipulation)
- matplotlib, seaborn (visualization)
- scipy.stats (Kruskal-Wallis, Chi-square, Spearman, Mann-Whitney U)
- fpdf2 (PDF report generation)
- re (regex for text cleaning)
- collections.Counter (hashtag analysis)
