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
|   |-- Entropy_Social_Engine_Cleaned.csv       # Single merged submission file (12,000 rows x 12 cols)
|   |-- Entropy_Social_Engine_Posts_Cleaned.csv # Cleaned posts (12,000 rows)
|   |-- Entropy_Social_Engine_Users_Cleaned.csv # Cleaned users (1,500 rows)
|   |-- Entropy_Social_Engine_Posts_Corrupted.csv
|   |-- Entropy_Social_Engine_Users.csv
|   |-- Entropy_cleaning_log.txt                # Log of every transformation applied
|   |-- images/                                 # 21 EDA chart PNGs
|   |-- Entropy_README.md
|
|-- Round1-Phase2-Analytical-Core/    # SQL analysis (E3 + M4 + H4)
|   |-- Entropy_Phase2_SQL_Queries.pdf          # Deliverable 1: final SQL queries
|   |-- images/Entropy_{E3,M4,H4}_output.jpeg   # Deliverable 2: output screenshots
|   |-- Entropy_Phase2_Logic_Explanation.pdf    # Deliverable 3: logic and approach
|   |-- Entropy_Phase2_Insight_Report.pdf       # Deliverable 4: insights and findings
|   |-- Entropy_01_SQL_Analysis.ipynb           # Builds constrained schema, runs the 3 queries, stat checks (executed)
|   |-- Entropy_social_engine.db                # SQLite database (PK/FK, CHECK constraints, indexes, view)
|   |-- queries/                                # The 3 final .sql files
|   |-- images/                                 # Output screenshots + 4 insight charts
|   |-- Entropy_README.md
|
|-- README.md                         # This file
```

## Round 1 Progress

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 - Data Recovery | Completed | Data cleaning (10 justified transformations) + EDA (20 sections, 21 visualizations, 6 statistical tests) + PDF insight report |
| Phase 2 - Analytical Core | Completed | One question per level (E3, M4, H4) with SQL query PDF, JPEG output screenshots, logic explanation PDF, and insight report PDF |

## Key Findings

### Phase 1: Data Recovery
- Identified and fixed **10 corruption patterns** including NULL strings, duplicates, HTML entities, mojibake, inconsistent timestamps, and negative values
- Removed **360 duplicate rows**, corrected **509 negative likes**, decoded **974 HTML artifacts**, and recovered **306 mojibake instances** to their original Unicode characters
- ~15% missing data across platform, text, and likes columns, confirmed **Missing Completely at Random** (Mann-Whitney U, p = 0.64)
- The dataset is **structurally uniform**: platform volume, day-of-week patterns, brand mentions, and language distribution all show coefficient of variation below 10%
- **5 of 6 statistical tests** return p > 0.05; the one significant signal is that **multi-platform users** show ~15% higher engagement
- Contradictory sentiment phrases in the same post reveal **template-based text generation**

### Phase 2: Analytical Core

| Level | Question | Answer | What it means |
|-------|----------|--------|---------------|
| Easy | E3 - Average Engagement by Platform | Instagram, 4,040.0 avg total engagement | All platforms within **2.2%**; the data could detect a 3.7% gap and finds none (Kruskal-Wallis p = 0.56) |
| Medium | M4 - Platform Behaviour by High-Follower Users | Instagram, 4,145.2 for the 594 users with 30k+ followers | **+4.4%** over smaller accounts, but not significant after Holm correction (p = 0.12), and the platform ranking reverses between groups |
| Hard | H4 - Follower-to-Engagement Anomaly | 16 users with < 5k followers in the top 10% | Close to the **13.1** expected by chance (p = 0.38); 14 are volume-driven and **2 are exceptional per post** (`user_ogtvuuki`, `user_kbdvf8d6`) |

- Two-table normalized schema with engine-enforced primary/foreign keys, NOT NULL and CHECK constraints; `EXPLAIN QUERY PLAN` confirms the indexes drive each query
- Every query carries its own benchmark: deviation from the overall mean (E3), comparison with users under 30k (M4), and a per-post decile ranking (H4); rankings are deterministic
- Corrupted `likes` handled per question: SQL NULL semantics for E3 averages, the brief's engagement definition for M4, per-user imputation for H4 totals (zero-filling would change 2 of 16 names)
- **Posting volume, not followers, drives user totals:** post count vs total engagement Spearman rho = 0.91, followers vs total rho = -0.01

## Tech Stack

- **Languages:** Python 3.x, SQL
- **Data Processing:** pandas, numpy, sqlite3
- **Statistics:** scipy.stats (Kruskal-Wallis, Chi-square, Spearman, Mann-Whitney U)
- **Visualization:** matplotlib, seaborn
- **Reporting:** LaTeX (pdflatex)
- **Notebooks:** Jupyter
- **Database:** SQLite
