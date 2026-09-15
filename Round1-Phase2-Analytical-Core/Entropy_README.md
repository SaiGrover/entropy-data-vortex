# Round 1 - Phase 2: Analytical Core

**Competition:** Data Vortex | AARUUSH'26  
**Theme:** Rebuilding the Social Engine  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Objective

Solve one question from each difficulty level using SQL on the cleaned Social Engine dataset, and submit the query, its output, the reasoning behind it, and the insights it produces.

| Level | Question | One-line answer |
|-------|----------|-----------------|
| Easy | **E3 - Average Engagement by Platform** | Instagram is first (4,040.0) but all five platforms sit within 2.2% of each other (Kruskal-Wallis p = 0.56) |
| Medium | **M4 - Platform Behaviour by High-Follower Users** | Instagram again (4,145.2 for the 594 users with >= 30k followers), only +105 above the all-user baseline; the cohort is indistinguishable from everyone else (Mann-Whitney p = 0.98) |
| Hard | **H4 - Follower-to-Engagement Anomaly** | 16 users with < 5k followers reach the top 10%, against 13.1 expected by chance (binomial p = 0.39); they post 61% more, not better |

## Why these three

Each question forces a different SQL technique and can be checked against a Phase 1 EDA finding rather than only returning rows:

- **E3** - `GROUP BY` + `RANK()` + cross-joined benchmark; tests "platform does not matter"
- **M4** - join, filter, two aggregated CTEs joined on platform; tests "follower count does not matter"
- **H4** - three-level CTE chain with `NTILE(10)`, `PERCENT_RANK()`, `COUNT(*) OVER ()`; tests whether "anomalies" occur at the rate independence predicts

## Deliverables

| Required item | File |
|---------------|------|
| SQL Query (PDF) | `Entropy_Phase2_SQL_Queries.pdf` |
| Output Screenshot (JPEG) | `images/Entropy_E3_output.jpeg`, `images/Entropy_M4_output.jpeg`, `images/Entropy_H4_output.jpeg` |
| Logic Explanation (PDF) | `Entropy_Phase2_Logic_Explanation.pdf` |
| Phase 2 Insight Report (PDF) | `Entropy_Phase2_Insight_Report.pdf` |

## Database Schema

Two-table normalised schema with referential integrity and DDL-level constraints (loaded with `if_exists="append"` so the constraints survive):

```sql
users (Parent)
  user_id         TEXT PRIMARY KEY
  location        TEXT NOT NULL
  language        TEXT NOT NULL
  account_created DATE NOT NULL
  follower_count  INTEGER NOT NULL CHECK (follower_count >= 0)

posts (Detail)
  post_id      TEXT PRIMARY KEY
  user_id      TEXT NOT NULL REFERENCES users(user_id)
  platform     TEXT            -- nullable (corrupted, 14.9%)
  text_content TEXT            -- nullable (corrupted, 14.3%)
  timestamp    DATETIME NOT NULL
  likes        INTEGER CHECK (likes >= 0)   -- nullable (corrupted, 15.1%)
  shares       INTEGER NOT NULL CHECK (shares >= 0)
  comments     INTEGER NOT NULL CHECK (comments >= 0)

Indexes: posts(user_id), posts(platform), posts(timestamp), users(language), users(location)
View:    user_posts (posts JOIN users, with total_engagement)
```

## NULL policy (the one decision that matters)

- **Averages (E3, M4):** rows with NULL likes are excluded once in `WHERE`, so all averages share a denominator. Substituting 0 would bias every average down by ~15%.
- **Per-user sums (H4):** NULL likes are `COALESCE`d to 0, so a corrupted like count never discards a post's valid shares and comments. The bias is uniform because the corruption is MCAR (Phase 1, p = 0.64).

## Key Insights

1. **Platform is irrelevant.** First-to-last spread is 2.2%; real platforms differ 2-3x.
2. **Audience size is irrelevant.** The >= 30k cohort straddles the per-platform baselines (max gap 2.6%, three of five platforms below baseline).
3. **"Anomalies" are chance.** 16 observed vs 13.1 expected low-follower users in the top decile.
4. **Volume is the only driver of totals.** Post count vs total engagement: Spearman rho = 0.89; follower count vs total engagement: rho = -0.03. Any leaderboard built on totals is a list of frequent posters; rank on per-post engagement instead.

## File Structure

```
Round1-Phase2-Analytical-Core/
|-- Entropy_01_SQL_Analysis.ipynb          # Builds schema, runs the 3 queries, statistical checks (executed)
|-- Entropy_social_engine.db               # SQLite database
|-- queries/
|   |-- Entropy_E3_average_engagement_by_platform.sql
|   |-- Entropy_M4_platform_behaviour_high_follower_users.sql
|   |-- Entropy_H4_follower_to_engagement_anomaly.sql
|-- images/
|   |-- Entropy_E3_output.jpeg             # Output screenshots (required deliverable)
|   |-- Entropy_M4_output.jpeg
|   |-- Entropy_H4_output.jpeg
|   |-- Entropy_E3_insight_chart.png       # Charts used in the insight report
|   |-- Entropy_M4_insight_chart.png
|   |-- Entropy_H4_insight_chart.png
|   |-- Entropy_H4_post_volume_chart.png
|-- Entropy_Phase2_SQL_Queries.pdf         # Deliverable 1
|-- Entropy_Phase2_Logic_Explanation.pdf   # Deliverable 3
|-- Entropy_Phase2_Insight_Report.pdf      # Deliverable 4
|-- Entropy_README.md
```

## Reproduce

Open and run `Entropy_01_SQL_Analysis.ipynb` top to bottom: it rebuilds `Entropy_social_engine.db` from the Phase 1 cleaned CSVs, executes the three queries in `queries/`, and prints every statistic quoted in the reports.

## Tools

Python 3, sqlite3, pandas, scipy.stats, matplotlib, Jupyter, LaTeX (pdflatex).
