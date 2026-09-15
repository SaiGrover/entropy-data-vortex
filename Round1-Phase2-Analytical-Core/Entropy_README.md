# Round 1 - Phase 2: Analytical Core

**Competition:** Data Vortex | AARUUSH'26  
**Theme:** Rebuilding the Social Engine  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Objective

Solve one question from each difficulty level using SQL on the cleaned Social Engine dataset, and submit the query, its output, the reasoning behind it, and the insights it produces.

| Level | Question | Answer | How much it can be relied on |
|-------|----------|--------|------------------------------|
| Easy | **E3 - Average Engagement by Platform** | Instagram, 4,040.0 average total engagement | All platforms within 2.2%; the data could detect a 3.7% gap and finds none (Kruskal-Wallis p = 0.56) |
| Medium | **M4 - Platform Behaviour by High-Follower Users** | Instagram, 4,145.2 for the 594 users with 30k+ followers | +4.4% over smaller accounts, but not significant after Holm correction (p = 0.12) and the platform ranking reverses between groups |
| Hard | **H4 - Follower-to-Engagement Anomaly** | 16 users with under 5k followers in the top 10% | Close to the 13.1 expected by chance (p = 0.38); 14 are volume-driven, 2 are exceptional per post |

## Deliverables

| Required item | File |
|---------------|------|
| SQL Query (PDF) | `Entropy_Phase2_SQL_Queries.pdf` |
| Output Screenshot (JPEG) | `images/Entropy_E3_output.jpeg`, `images/Entropy_M4_output.jpeg`, `images/Entropy_H4_output.jpeg` (Jupyter executing each query file) |
| Logic Explanation (PDF) | `Entropy_Phase2_Logic_Explanation.pdf` |
| Phase 2 Insight Report (PDF) | `Entropy_Phase2_Insight_Report.pdf` |

## Query Design

- **E3** - `GROUP BY` + `RANK()` + cross-joined grand mean. Follows the question literally: only posts with a missing platform are excluded, and SQL's NULL handling applies the brief's "ignore missing likes" rule to total engagement.
- **M4** - join + conditional aggregation in a single scan. The 30k+ cohort is compared with users **under** 30k (not all users, which would include the cohort), and each group is ranked separately to test whether the platform order holds.
- **H4** - four-level CTE chain: impute missing likes with each user's own average, roll up to users, rank twice with `NTILE(10)` (by total and by per-post engagement, `user_id` tie-break), then filter and classify as *Volume-driven* or *Exceptional per post*.

## Database Schema

Two-table normalised schema with engine-enforced constraints (foreign key, CHECK and NOT NULL violations are demonstrated in the notebook):

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
  platform     TEXT            -- nullable (corrupted, 1,784 posts)
  text_content TEXT            -- nullable (corrupted)
  timestamp    DATETIME NOT NULL
  likes        INTEGER CHECK (likes >= 0)   -- nullable (corrupted, 1,814 posts)
  shares       INTEGER NOT NULL CHECK (shares >= 0)
  comments     INTEGER NOT NULL CHECK (comments >= 0)

Indexes: posts(user_id), posts(platform), posts(timestamp), users(location), users(language)
View:    user_posts (posts JOIN users, with total_engagement)
```

`EXPLAIN QUERY PLAN` confirms `idx_posts_platform` drives E3 and M4, `idx_posts_user_id` drives H4, and every join to `users` is a primary-key lookup.

## Key Insights

1. **Platform choice moves engagement by less than 4%.** A measured bound, not a small-sample shrug.
2. **Large accounts have no stable best platform.** Instagram's +4.4% disappears under multiple-comparison correction, and YouTube goes from 1st for smaller accounts to 5th for large ones.
3. **Posting volume, not followers, puts users in the top 10%.** Posts vs total engagement: Spearman rho = 0.91; followers vs total: rho = -0.01.
4. **Two genuine small-account outperformers:** `user_ogtvuuki` (Cairo) and `user_kbdvf8d6` (Tokyo) are top 10% on both total and per-post engagement.
5. **How corruption is handled changes answers.** Zero-filling missing likes would have changed 2 of the 16 names in H4.

## File Structure

```
Round1-Phase2-Analytical-Core/
|-- Entropy_Phase2_SQL_Queries.pdf         # Deliverable 1
|-- Entropy_Phase2_Logic_Explanation.pdf   # Deliverable 3
|-- Entropy_Phase2_Insight_Report.pdf      # Deliverable 4
|-- Entropy_01_SQL_Analysis.ipynb          # Builds schema, query plans, runs queries, all statistics (executed)
|-- Entropy_social_engine.db               # SQLite database
|-- queries/
|   |-- Entropy_E3_average_engagement_by_platform.sql
|   |-- Entropy_M4_platform_behaviour_high_follower_users.sql
|   |-- Entropy_H4_follower_to_engagement_anomaly.sql
|-- images/
|   |-- Entropy_E3_output.jpeg             # Deliverable 2: output screenshots
|   |-- Entropy_M4_output.jpeg
|   |-- Entropy_H4_output.jpeg
|   |-- Entropy_E3_insight_chart.png       # Charts used in the insight report
|   |-- Entropy_M4_insight_chart.png
|   |-- Entropy_H4_insight_chart.png
|   |-- Entropy_H4_post_volume_chart.png
|-- Entropy_README.md
```

## Reproduce

Open and run `Entropy_01_SQL_Analysis.ipynb` top to bottom: it rebuilds `Entropy_social_engine.db` from the Phase 1 cleaned CSVs, shows each query plan, executes the three queries in `queries/`, and prints every statistic quoted in the reports.

## Tools

Python 3, sqlite3, pandas, scipy.stats, matplotlib, Jupyter, LaTeX (pdflatex).
