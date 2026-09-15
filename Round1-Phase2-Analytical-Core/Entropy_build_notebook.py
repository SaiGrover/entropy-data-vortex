"""Build Entropy_01_SQL_Analysis.ipynb from the query files, then execute it."""
import nbformat as nbf
import subprocess

nb = nbf.v4.new_notebook()
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))

md("""# Round 1 - Phase 2: Analytical Core

**Competition:** Data Vortex | AARUUSH'26
**Theme:** Rebuilding the Social Engine
**Team:** Entropy
**Members:** Saanvi Grover & Aditya Sharma

Questions solved: **E3** (Average Engagement by Platform), **M4** (Platform Behaviour by High-Follower Users), **H4** (Follower-to-Engagement Anomaly).

This notebook (1) builds the SQLite schema from the Phase 1 cleaned CSVs with real DDL constraints, (2) runs the three final queries stored in `queries/`, and (3) records the statistical checks quoted in the reports.""")

code("""import sqlite3
import pandas as pd
from pathlib import Path
from scipy import stats

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

DB = "Entropy_social_engine.db"
P1 = Path("../Round1-Phase1-Data-Recovery")
posts = pd.read_csv(P1 / "Entropy_Social_Engine_Posts_Cleaned.csv")
users = pd.read_csv(P1 / "Entropy_Social_Engine_Users_Cleaned.csv")
print(posts.shape, users.shape)""")

md("""## 1. Schema

Two normalised tables. `posts.user_id` is a foreign key to `users`; NOT NULL / CHECK constraints reflect what Phase 1 cleaning guarantees, and the three corrupted columns (`platform`, `text_content`, `likes`) are deliberately nullable. Data is loaded with `if_exists="append"` so the hand-written DDL (and its constraints) survives.""")

code("""DDL = '''
PRAGMA foreign_keys = ON;
DROP VIEW  IF EXISTS user_posts;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id         TEXT PRIMARY KEY,
    location        TEXT NOT NULL,
    language        TEXT NOT NULL,
    account_created DATE NOT NULL,
    follower_count  INTEGER NOT NULL CHECK (follower_count >= 0)
);

CREATE TABLE posts (
    post_id      TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(user_id),
    platform     TEXT,
    text_content TEXT,
    timestamp    DATETIME NOT NULL,
    likes        INTEGER CHECK (likes >= 0),
    shares       INTEGER NOT NULL CHECK (shares >= 0),
    comments     INTEGER NOT NULL CHECK (comments >= 0)
);

CREATE INDEX idx_posts_user_id   ON posts(user_id);
CREATE INDEX idx_posts_platform  ON posts(platform);
CREATE INDEX idx_posts_timestamp ON posts(timestamp);
CREATE INDEX idx_users_language  ON users(language);
CREATE INDEX idx_users_location  ON users(location);

CREATE VIEW user_posts AS
SELECT p.*, u.location, u.language, u.account_created, u.follower_count,
       COALESCE(p.likes, 0) + p.shares + p.comments AS total_engagement
FROM posts p JOIN users u ON u.user_id = p.user_id;
'''
con = sqlite3.connect(DB)
con.executescript(DDL)
users.to_sql("users", con, if_exists="append", index=False)
posts.to_sql("posts", con, if_exists="append", index=False)
con.commit()
print(pd.read_sql_query("SELECT name, type FROM sqlite_master WHERE type IN ('table','index','view') ORDER BY type, name", con))""")

code("""def run(path):
    sql = Path(path).read_text(encoding="utf-8")
    return pd.read_sql_query(sql, con)

def engagement_posts():
    return pd.read_sql_query('''
        SELECT p.platform, u.follower_count, p.likes + p.shares + p.comments AS eng
        FROM posts p JOIN users u ON u.user_id = p.user_id
        WHERE p.platform IS NOT NULL AND p.likes IS NOT NULL''', con)""")

md("""## 2. E3 - Average Engagement by Platform (Easy)

**Challenge:** Calculate the average likes, shares and comments for each platform. Which platform generates the highest average total engagement?

**Why this design:** posts with a missing platform or missing likes are filtered once in `WHERE` so that all four averages share the same denominator (8,662 posts). A cross-joined grand mean adds `pct_vs_overall`, which turns "who is first" into "by how much".""")

code("""e3 = run("queries/Entropy_E3_average_engagement_by_platform.sql")
e3""")

code("""ep = engagement_posts()
kw = stats.kruskal(*[g.eng.values for _, g in ep.groupby("platform")])
spread = 100 * (e3.avg_total_engagement.max() - e3.avg_total_engagement.min()) / e3.avg_total_engagement.mean()
print(f"First-to-last spread: {spread:.2f}% of the mean")
print(f"Kruskal-Wallis across platforms: H = {kw.statistic:.2f}, p = {kw.pvalue:.3f}")""")

md("""**What this means:** Instagram is first (4,040.0) and Twitter last (3,951.9), a 2.2% spread with p = 0.56. Platform choice does not affect engagement, matching the Phase 1 EDA (Kruskal-Wallis p = 0.37 on the full table).""")

md("""## 3. M4 - Platform Behaviour by High-Follower Users (Medium)

**Challenge:** Among users with at least 30,000 followers, which platform gives them the highest average engagement per post?

**Why this design:** the cohort average per platform is joined to the same platform's average across *all* users. Without that baseline "Instagram is best for big accounts" is unfalsifiable; with it, the cohort can be shown to track the population.""")

code("""m4 = run("queries/Entropy_M4_platform_behaviour_high_follower_users.sql")
m4""")

code("""hf = ep[ep.follower_count >= 30000]
kw_hf = stats.kruskal(*[g.eng.values for _, g in hf.groupby("platform")])
mw = stats.mannwhitneyu(hf.eng, ep[ep.follower_count < 30000].eng)
print(f"Users with >= 30k followers: {(users.follower_count >= 30000).sum()} of {len(users)}")
print(f"Kruskal-Wallis within cohort: H = {kw_hf.statistic:.2f}, p = {kw_hf.pvalue:.3f}")
print(f"Mann-Whitney cohort vs rest:  p = {mw.pvalue:.3f}")
print(f"Largest cohort-minus-baseline gap: {m4.cohort_minus_baseline.abs().max():.1f}")""")

md("""**What this means:** the cohort's best platform is Instagram (4,145.2), just +105 above Instagram's all-user average, and three of five platforms are below baseline. Follower count buys no engagement (Mann-Whitney p = 0.98).""")

md("""## 4. H4 - Follower-to-Engagement Anomaly (Hard)

**Challenge:** Find users with fewer than 5,000 followers whose total post engagement places them in the top 10% of all users.

**Why this design:** three CTE levels (post -> user -> population -> filter). `NTILE(10)` defines the top decile relative to the data rather than a hard-coded threshold; `PERCENT_RANK()` shows how deep inside the decile each user sits; `avg_engagement_per_post` separates *volume* from *performance*. Missing likes are `COALESCE`d to 0 so a corrupted like count never discards a post's valid shares and comments from a user's total.""")

code("""h4 = run("queries/Entropy_H4_follower_to_engagement_anomaly.sql")
h4""")

code("""ue = pd.read_sql_query('''
    SELECT u.user_id, u.follower_count, COUNT(p.post_id) AS post_count,
           SUM(COALESCE(p.likes,0) + p.shares + p.comments) AS total_engagement
    FROM users u JOIN posts p ON p.user_id = u.user_id GROUP BY u.user_id''', con)
ue["decile"] = pd.qcut(ue.total_engagement.rank(ascending=False, method="first"), 10, labels=False) + 1
n_top = (ue.decile == 1).sum()
p_low = (ue.follower_count < 5000).mean()
observed = ((ue.decile == 1) & (ue.follower_count < 5000)).sum()
expected = n_top * p_low
print(f"Top decile size: {n_top} | share of users with < 5k followers: {100*p_low:.2f}%")
print(f"Expected anomalies under independence: {expected:.1f} | observed: {observed} | binomial p = {stats.binomtest(observed, n_top, p_low).pvalue:.3f}")
print(f"Mean posts: all users {ue.post_count.mean():.2f} | anomalies {ue[(ue.decile==1)&(ue.follower_count<5000)].post_count.mean():.2f}")
print(f"Spearman posts vs total engagement:     rho = {stats.spearmanr(ue.post_count, ue.total_engagement)[0]:.3f}")
print(f"Spearman followers vs total engagement: rho = {stats.spearmanr(ue.follower_count, ue.total_engagement)[0]:.3f}, p = {stats.spearmanr(ue.follower_count, ue.total_engagement)[1]:.3f}")""")

md("""**What this means:** 16 low-follower users sit in the top decile against 13.1 expected by chance (p = 0.39). They average 12.9 posts vs 8.0 for the population while their per-post engagement (~4,040) is the platform mean. They are prolific, not exceptional or suspicious; ranking on per-post engagement would remove them.""")

md("""## 5. Summary

| Lever tested | Largest effect | Significance | Verdict |
|---|---|---|---|
| Platform (E3) | 2.2% spread | p = 0.56 | No effect |
| Audience size x platform (M4) | 2.6% vs baseline | p = 0.18 / 0.98 | No effect |
| Audience size vs total engagement (H4) | rho = -0.03 | p = 0.30 | No effect |
| Post volume vs total engagement (H4) | rho = 0.89 | p < 1e-100 | Dominant driver |

Deliverables: `Entropy_Phase2_SQL_Queries.pdf`, `images/Entropy_{E3,M4,H4}_output.jpeg`, `Entropy_Phase2_Logic_Explanation.pdf`, `Entropy_Phase2_Insight_Report.pdf`.""")

code("con.close()")

nb["cells"] = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out = "Entropy_01_SQL_Analysis.ipynb"
nbf.write(nb, out)
subprocess.run(["python", "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", out], check=True)
print("notebook executed")
