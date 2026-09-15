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
|-- Round1-Phase2-Analytical-Core/    # SQL analysis (E3 + M4 + H4)
|   |-- Entropy_Phase2_SQL_Queries.pdf          # Deliverable 1: final SQL queries
|   |-- images/Entropy_{E3,M4,H4}_output.jpeg   # Deliverable 2: output screenshots
|   |-- Entropy_Phase2_Logic_Explanation.pdf    # Deliverable 3: logic and approach
|   |-- Entropy_Phase2_Insight_Report.pdf       # Deliverable 4: insights and findings
|   |-- Entropy_01_SQL_Analysis.ipynb           # Builds constrained schema, runs the 3 queries, stat checks (executed)
|   |-- Entropy_social_engine.db                # SQLite database (PK/FK, CHECK constraints, indexes, view)
|   |-- queries/                                # The 3 final .sql files
|   |-- images/                                 # Output screenshots + 4 insight charts
|   |-- Entropy_*.tex                           # LaTeX sources for the three PDFs
|   |-- Entropy_run_queries.py                  # Renders screenshots and charts from query results
|   |-- Entropy_build_notebook.py               # Generates and executes the notebook
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
| Easy | E3 - Average Engagement by Platform | Instagram, 4,040.0 avg total engagement | All five platforms sit within **2.2%** of each other (Kruskal-Wallis p = 0.56); platform choice is irrelevant |
| Medium | M4 - Platform Behaviour by High-Follower Users | Instagram, 4,145.2 for the 594 users with >= 30k followers | Only +105 over the all-user baseline; three of five platforms are below baseline and the cohort is indistinguishable from everyone else (Mann-Whitney p = 0.98) |
| Hard | H4 - Follower-to-Engagement Anomaly | 16 users with < 5k followers in the top 10% | Chance predicts **13.1** (binomial p = 0.39); they post 61% more often at an average per-post rate, so they are prolific, not exceptional or suspicious |

- Two-table normalized schema with primary/foreign keys, NOT NULL and CHECK constraints, 5 indexes, and a convenience view; queries use CTE chains, `RANK()`, `NTILE(10)`, `PERCENT_RANK()` and cross-joined benchmarks
- Explicit NULL policy for the 15% corrupted `likes`: excluded for averages (same denominator), `COALESCE`d to 0 for per-user sums
- **Volume is the only driver of totals:** post count vs total engagement Spearman rho = 0.89, follower count vs total engagement rho = -0.03. Any leaderboard built on totals is a list of frequent posters; rank on per-post engagement instead

## Tech Stack

- **Languages:** Python 3.x, SQL
- **Data Processing:** pandas, numpy, sqlite3
- **Statistics:** scipy.stats (Kruskal-Wallis, Chi-square, Spearman, Mann-Whitney U)
- **Visualization:** matplotlib, seaborn
- **Reporting:** LaTeX (pdflatex), fpdf2
- **Notebooks:** Jupyter
- **Database:** SQLite
