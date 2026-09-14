# Data Vortex - AARUUSH'26

**Theme:** Rebuilding the Social Engine  
**Event:** AARUUSH'26, SRM Institute of Science and Technology  
**Dates:** September 13-16, 2026  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Competition Overview

Data Vortex is a multi-round data science competition centered around recovering and analyzing a corrupted social media platform dataset ("The Social Engine"). Round 1 covers the recovery of the dataset and its analytical foundation in two phases: data cleaning with exploratory analysis, followed by SQL-based analytical reasoning.

## Dataset

The Social Engine dataset was retrieved from a simulated corrupted website (`datavortex-social-engine.vercel.app`) through an interactive recovery terminal. The dataset consists of:

- **Posts:** 12,000 social media posts with text content, engagement metrics (likes, shares, comments), timestamps, and platform tags
- **Users:** 1,500 user profiles with location, language, account creation date, and follower count
- **Platforms:** Facebook, YouTube, Twitter, Reddit, Instagram
- **Date Range:** May 2024 - April 2025

## Project Structure

```
Data Vortex/
|
|-- Round1-Phase1-Data-Recovery/      # Data cleaning + EDA
|   |-- Entropy_01_Data_Cleaning.ipynb          # 10-step cleaning pipeline with before/after examples
|   |-- Entropy_02_EDA_Report.ipynb             # 20-section EDA, 21 visualizations, 6 statistical tests
|   |-- Entropy_Phase1_EDA_Report.pdf           # Standalone EDA insight report (LaTeX)
|   |-- Entropy_eda_report.tex                  # LaTeX source for the PDF report
|   |-- Entropy_Social_Engine_Cleaned.csv       # Single merged submission file (12,000 rows x 12 cols)
|   |-- Entropy_Social_Engine_Posts_Cleaned.csv # Cleaned posts (12,000 rows)
|   |-- Entropy_Social_Engine_Users_Cleaned.csv # Cleaned users (1,500 rows)
|   |-- Entropy_Social_Engine_Posts_Corrupted.csv
|   |-- Entropy_Social_Engine_Users.csv
|   |-- Entropy_cleaning_log.txt                # Log of every transformation applied
|   |-- images/                                 # 21 EDA chart PNGs
|   |-- Entropy_README.md
|
|-- Round1-Phase2-Analytical-Core/    # SQL analysis
|   |-- Entropy_01_SQL_Analysis.ipynb           # 18 analytical SQL queries with interpretations
|   |-- Entropy_social_engine.db                # SQLite database (PK/FK, CHECK constraints, indexes, view)
|   |-- queries/                                # Individual .sql files
|   |-- images/                                 # Query output screenshots and inline visualizations
|   |-- Entropy_Phase2_Insight_Report.pdf       # Comprehensive insight report (PDF)
|   |-- Entropy_Phase2_Insight_Report.md        # Insight report source (Markdown)
|   |-- Entropy_SQL_Queries_Guide.md            # Query-by-query technique and logic guide
|   |-- Entropy_README.md
|
|-- Entropy_README.md                 # This file
```

## Round 1 Progress

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 - Data Recovery | Completed | Data cleaning (10 justified transformations) + EDA (20 sections, 21 visualizations, 6 statistical tests) + PDF insight report |
| Phase 2 - Analytical Core | Completed | 18 SQL queries across 6 analytical categories + insight report |

## Key Findings

### Phase 1: Data Recovery
- Identified and fixed **10 corruption patterns** including NULL strings, duplicates, HTML entities, mojibake, inconsistent timestamps, and negative values
- Removed **360 duplicate rows**, corrected **509 negative likes**, decoded **974 HTML artifacts**, and recovered **306 mojibake instances** to their original Unicode characters
- ~15% missing data across platform, text, and likes columns, confirmed **Missing Completely at Random** (Mann-Whitney U, p = 0.64)
- The dataset is **structurally uniform**: platform volume, day-of-week patterns, brand mentions, and language distribution all show coefficient of variation below 10%
- **5 of 6 statistical tests** return p > 0.05; the one significant signal is that **multi-platform users** show ~15% higher engagement
- Contradictory sentiment phrases in the same post reveal **template-based text generation**

### Phase 2: Analytical Core
- Two-table normalized schema with primary/foreign keys, NOT NULL and CHECK constraints, 5 indexes, and a convenience view
- Post volume is **stable** (914-1,038 per month) with no viral outliers; bot-detection and outlier queries return empty results, a legitimate structural finding
- **Multi-platform users** have consistently higher engagement than single-platform users
- **Negative sentiment** posts often outperform positive ones for brand content
- **Follower count** and **account age** show no meaningful correlation with engagement
- Cohort analysis, SQL-based text pattern detection, and self-join "user twins" all confirm uniform data generation

## Tech Stack

- **Languages:** Python 3.x, SQL
- **Data Processing:** pandas, numpy, sqlite3
- **Statistics:** scipy.stats (Kruskal-Wallis, Chi-square, Spearman, Mann-Whitney U)
- **Visualization:** matplotlib, seaborn
- **Reporting:** LaTeX (pdflatex), fpdf2
- **Notebooks:** Jupyter
- **Database:** SQLite
