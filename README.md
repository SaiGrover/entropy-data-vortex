# Data Vortex - AARUUSH'26

**Theme:** Rebuilding the Social Engine  
**Event:** AARUUSH'26, SRM Institute of Science and Technology  
**Dates:** September 13-16, 2026  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Competition Overview

Data Vortex is a multi-round data science competition centered around recovering and analyzing a corrupted social media platform dataset ("The Social Engine"). Participants must demonstrate skills in data cleaning, SQL analysis, NLP, data collection, and interactive visualization across 4 rounds.

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
|   |-- Entropy_01_Data_Cleaning.ipynb        # 10-step cleaning pipeline
|   |-- Entropy_02_EDA_Report.ipynb           # 13-section EDA with visualizations
|   |-- images/                       # 14 EDA chart PNGs
|   |-- Entropy_Social_Engine_Posts_Cleaned.csv
|   |-- Entropy_Social_Engine_Users_Cleaned.csv
|   |-- Entropy_cleaning_log.txt
|   |-- Entropy_README.md
|
|-- Round1-Phase2-Analytical-Core/    # SQL analysis
|   |-- Entropy_01_SQL_Analysis.ipynb         # 15 analytical SQL queries
|   |-- Entropy_social_engine.db              # SQLite database
|   |-- queries/                      # 15 individual .sql files
|   |-- images/                       # 15 query output screenshots
|   |-- Entropy_Phase2_Insight_Report.pdf      # Comprehensive insight report (PDF)
|   |-- Entropy_Phase2_Insight_Report.md      # Insight report source (Markdown)
|   |-- Entropy_README.md
|
|-- Round2-Semantic-Recovery/         # NLP sentiment & topic modeling
|   |-- Entropy_01_NLP_Model.ipynb            # Full NLP pipeline (executed)
|   |-- model/                        # Trained model files (.pkl)
|   |-- images/                       # 7 evaluation visualizations
|   |-- Entropy_Round2_Technical_Report.md    # Technical report
|   |-- Entropy_README.md
|
|-- Round3-Signal-Tracking/           # Self-collected data analysis
|   |-- Entropy_01_Data_Collection.ipynb      # Data collection code
|   |-- Entropy_02_Analysis.ipynb             # Analysis + comparison with Round 1
|   |-- data/                         # Collected dataset (~2,500 rows)
|   |-- images/                       # 6 analysis visualizations
|   |-- Entropy_Round3_Analytical_Report.md   # Analytical report
|   |-- Entropy_README.md
|
|-- Round4-Social-Engine-Revival/     # Interactive dashboard
|   |-- Entropy_app.py                        # Streamlit dashboard (6 pages)
|   |-- Entropy_requirements.txt              # Python dependencies
|   |-- images/                       # Dashboard screenshots
|   |-- Entropy_README.md
|
|-- Entropy_README.md                         # This file
```

## Round Progress

| Round | Phase | Status | Description |
|-------|-------|--------|-------------|
| 1 | Phase 1 - Data Recovery | Completed | Data cleaning (10 transformations) + EDA (14 visualizations) |
| 1 | Phase 2 - Analytical Core | Completed | 15 SQL queries across 4 analytical categories + insight report |
| 2 | Semantic Recovery | Completed | Sentiment classification (F1: 0.9964) + LDA topic modeling (6 topics) |
| 3 | Signal Tracking | Completed | ~2,500 collected posts, brand sentiment analysis, cross-dataset comparison |
| 4 | Social Engine Revival | Completed | 6-page interactive Streamlit dashboard |

## Key Findings

### Round 1 - Phase 1: Data Recovery
- Identified and fixed **10 corruption patterns** including NULL strings, duplicates, HTML entities, mojibake, inconsistent timestamps, and negative values
- Removed **360 duplicate rows** and corrected **509 negative likes**
- ~15% missing data across platform, text, and likes columns

### Round 1 - Phase 2: Analytical Core
- Post volume is **stable** (~1,000/month) with no extreme outliers
- **Multi-platform users** have consistently higher engagement than single-platform users
- **Negative sentiment** posts often outperform positive ones for brand content
- **Follower count** and **account age** show no meaningful correlation with engagement
- Missing data appears **random** (MCAR), not systematic

### Round 2: Semantic Recovery
- Logistic Regression achieved **0.9964 weighted F1-score** on sentiment classification
- LDA discovered **6 latent topics** clustering around major brands and product review language
- TF-IDF with 2,421 features proved sufficient for high-accuracy classification
- Outperformed Random Forest (0.9867) and Naive Bayes (0.9921)

### Round 3: Signal Tracking
- Collected ~2,500 posts across 10 brands and 4 platforms (Twitter, Reddit, Amazon Reviews, YouTube)
- **Apple and Toyota** lead in positive sentiment; **Amazon and Microsoft** show elevated negative sentiment
- **Negative posts drive higher engagement** across all platforms
- Brand sentiment patterns are **consistent between Round 1 and Round 3** datasets

### Round 4: Social Engine Revival
- 6-page interactive Streamlit dashboard covering: Overview, Platform Analytics, User Insights, Temporal Trends, Content Analysis, Data Quality
- Plotly-powered interactive charts with sidebar navigation
- Integrates data from all previous rounds

## Tech Stack

- **Languages:** Python 3.x, SQL
- **Data Processing:** pandas, numpy, sqlite3
- **Visualization:** matplotlib, seaborn, plotly
- **NLP:** NLTK, scikit-learn (TF-IDF, Logistic Regression, LDA)
- **Dashboard:** Streamlit
- **Notebooks:** Jupyter
- **Database:** SQLite
