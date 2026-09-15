"""Run the three Phase 2 queries, save output screenshots (JPEG) and insight charts."""
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

DB = "Entropy_social_engine.db"
QUERIES = {
    "E3": "queries/Entropy_E3_average_engagement_by_platform.sql",
    "M4": "queries/Entropy_M4_platform_behaviour_high_follower_users.sql",
    "H4": "queries/Entropy_H4_follower_to_engagement_anomaly.sql",
}
TITLES = {
    "E3": "E3 - Average Engagement by Platform",
    "M4": "M4 - Platform Behaviour by High-Follower Users (>= 30,000 followers)",
    "H4": "H4 - Follower-to-Engagement Anomaly (< 5,000 followers, top 10% engagement)",
}

con = sqlite3.connect(DB)
results = {}


def render_table(df, title, path):
    n_rows, n_cols = df.shape
    cell_text = [[f"{v:,}" if isinstance(v, (int, np.integer)) else
                  (f"{v:,.2f}" if isinstance(v, (float, np.floating)) else str(v))
                  for v in row] for row in df.itertuples(index=False)]
    col_chars = [max(len(str(c)), *(len(r[i]) for r in cell_text)) + 2 for i, c in enumerate(df.columns)]
    total_chars = sum(col_chars)
    fig_w = min(max(0.085 * total_chars, 7), 20)
    fig_h = 0.3 * (n_rows + 1) + 1.1
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
    ax.axis("off")
    ax.set_title(f"{title}\nsqlite3 | {n_rows} row(s) returned", fontsize=10.5, fontweight="bold",
                 loc="left", pad=6, family="monospace")
    tbl = ax.table(cellText=cell_text, colLabels=list(df.columns), cellLoc="center",
                   colWidths=[c / total_chars for c in col_chars], bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if r == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", weight="bold", family="monospace")
        else:
            cell.set_facecolor("#f7f9fc" if r % 2 else "white")
            cell.set_text_props(family="monospace")
    fig.tight_layout()
    fig.savefig(path, format="jpeg", bbox_inches="tight", pil_kwargs={"quality": 92})
    plt.close(fig)


for key, path in QUERIES.items():
    sql = open(path, encoding="utf-8").read()
    df = pd.read_sql_query(sql, con)
    results[key] = df
    render_table(df, TITLES[key], f"images/Entropy_{key}_output.jpeg")
    print(f"{key}: {len(df)} rows -> images/Entropy_{key}_output.jpeg")

# ---------- supporting statistics ----------
user_eng = pd.read_sql_query("""
    SELECT u.user_id, u.follower_count, COUNT(p.post_id) AS post_count,
           SUM(COALESCE(p.likes,0)+p.shares+p.comments) AS total_engagement
    FROM users u JOIN posts p ON p.user_id = u.user_id GROUP BY u.user_id
""", con)
user_eng["avg_per_post"] = user_eng.total_engagement / user_eng.post_count
user_eng["decile"] = pd.qcut(user_eng.total_engagement.rank(ascending=False, method="first"), 10, labels=False) + 1
top = user_eng[user_eng.decile == 1]
low = user_eng[user_eng.follower_count < 5000]
n_users, n_low, n_top = len(user_eng), len(low), len(top)
p_low = n_low / n_users
observed = int(((user_eng.decile == 1) & (user_eng.follower_count < 5000)).sum())
expected = p_low * n_top
binom_p = stats.binomtest(observed, n_top, p_low).pvalue
rho_post, p_post = stats.spearmanr(user_eng.post_count, user_eng.total_engagement)
rho_fol, p_fol = stats.spearmanr(user_eng.follower_count, user_eng.total_engagement)
rho_fol_avg, p_fol_avg = stats.spearmanr(user_eng.follower_count, user_eng.avg_per_post)

# E3 / M4 significance
posts = pd.read_sql_query("""
    SELECT p.platform, u.follower_count, p.likes+p.shares+p.comments AS eng
    FROM posts p JOIN users u ON u.user_id=p.user_id
    WHERE p.platform IS NOT NULL AND p.likes IS NOT NULL
""", con)
kw_all = stats.kruskal(*[g.eng.values for _, g in posts.groupby("platform")])
hf = posts[posts.follower_count >= 30000]
kw_hf = stats.kruskal(*[g.eng.values for _, g in hf.groupby("platform")])
mw_hf = stats.mannwhitneyu(hf.eng, posts[posts.follower_count < 30000].eng)

summary = {
    "users": n_users, "low_follower_users": n_low, "low_follower_share_pct": round(100 * p_low, 2),
    "top_decile_users": n_top, "observed_anomalies": observed, "expected_anomalies": round(expected, 1),
    "binomial_p": round(binom_p, 3),
    "mean_posts_all": round(user_eng.post_count.mean(), 2), "mean_posts_top_decile": round(top.post_count.mean(), 2),
    "mean_posts_anomalies": round(top[top.follower_count < 5000].post_count.mean(), 2),
    "mean_avg_per_post_all": round(user_eng.avg_per_post.mean(), 1),
    "mean_avg_per_post_anomalies": round(top[top.follower_count < 5000].avg_per_post.mean(), 1),
    "spearman_posts_vs_total": (round(rho_post, 3), f"{p_post:.2e}"),
    "spearman_followers_vs_total": (round(rho_fol, 3), round(p_fol, 3)),
    "spearman_followers_vs_avg": (round(rho_fol_avg, 3), round(p_fol_avg, 3)),
    "kruskal_platform_all": (round(kw_all.statistic, 2), round(kw_all.pvalue, 3)),
    "kruskal_platform_high_followers": (round(kw_hf.statistic, 2), round(kw_hf.pvalue, 3)),
    "mannwhitney_high_vs_low_followers": (int(mw_hf.statistic), round(mw_hf.pvalue, 3)),
    "high_follower_users": int((user_eng.follower_count >= 30000).sum()),
    "E3_spread_pct": round(100 * (results["E3"].avg_total_engagement.max() - results["E3"].avg_total_engagement.min()) / results["E3"].avg_total_engagement.mean(), 2),
}
for k, v in summary.items():
    print(f"{k}: {v}")

# ---------- insight charts ----------
BLUE, GREY, RED = "#2E86C1", "#95A5A6", "#C0392B"

# E3
e3 = results["E3"].sort_values("avg_total_engagement", ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
bars = ax.bar(e3.platform, e3.avg_total_engagement, color=BLUE)
ax.axhline(posts.eng.mean(), color=RED, ls="--", lw=1.2, label=f"Overall mean = {posts.eng.mean():,.0f}")
for b, v in zip(bars, e3.avg_total_engagement):
    ax.text(b.get_x() + b.get_width() / 2, v + 15, f"{v:,.0f}", ha="center", fontsize=9)
ax.set_ylim(3800, 4120)
ax.set_ylabel("Avg total engagement per post")
ax.set_title(f"E3: Platform averages sit within {summary['E3_spread_pct']}% of each other (Kruskal-Wallis p = {kw_all.pvalue:.2f})")
ax.legend(loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("images/Entropy_E3_insight_chart.png"); plt.close(fig)

# M4
m4 = results["M4"].sort_values("avg_engagement_high_followers", ascending=False)
x = np.arange(len(m4)); w = 0.38
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
ax.bar(x - w / 2, m4.avg_engagement_high_followers, w, color=BLUE, label=">= 30,000 followers")
ax.bar(x + w / 2, m4.avg_engagement_all_users, w, color=GREY, label="All users")
ax.set_xticks(x, m4.platform)
ax.set_ylim(3800, 4250)
ax.set_ylabel("Avg engagement per post")
ax.set_title(f"M4: High-follower cohort vs platform baseline (max gap {m4.cohort_minus_baseline.abs().max():.0f}, ~{100*m4.cohort_minus_baseline.abs().max()/4000:.1f}%)")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("images/Entropy_M4_insight_chart.png"); plt.close(fig)

# H4: scatter followers vs total engagement with anomaly region + expected vs observed inset
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), dpi=150, gridspec_kw={"width_ratios": [1.6, 1]})
ax = axes[0]
thr = user_eng[user_eng.decile == 1].total_engagement.min()
ax.scatter(user_eng.follower_count, user_eng.total_engagement, s=6, color=GREY, alpha=0.5, label="All users")
anom = user_eng[(user_eng.decile == 1) & (user_eng.follower_count < 5000)]
ax.scatter(anom.follower_count, anom.total_engagement, s=22, color=RED, label=f"H4 anomalies (n={len(anom)})")
ax.axhline(thr, color=BLUE, ls="--", lw=1, label=f"Top-10% threshold = {thr:,.0f}")
ax.axvline(5000, color=BLUE, ls=":", lw=1)
ax.set_xlabel("Follower count"); ax.set_ylabel("Total engagement (all posts)")
ax.set_title(f"Followers vs total engagement (Spearman rho = {rho_fol:.3f}, p = {p_fol:.2f})")
ax.legend(fontsize=8, loc="upper right"); ax.spines[["top", "right"]].set_visible(False)
ax = axes[1]
ax.bar(["Expected by chance", "Observed"], [expected, observed], color=[GREY, RED])
for i, v in enumerate([expected, observed]):
    ax.text(i, v + 0.3, f"{v:.1f}" if i == 0 else f"{v}", ha="center", fontsize=10, fontweight="bold")
ax.set_ylim(0, max(expected, observed) * 1.3)
ax.set_title(f"Low-follower users in top decile\n(binomial p = {binom_p:.2f})")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("images/Entropy_H4_insight_chart.png"); plt.close(fig)

# H4 driver chart: post count explains total engagement
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
ax.scatter(user_eng.post_count, user_eng.total_engagement, s=6, color=GREY, alpha=0.5, label="All users")
ax.scatter(anom.post_count, anom.total_engagement, s=22, color=RED, label="H4 anomalies")
ax.set_xlabel("Number of posts"); ax.set_ylabel("Total engagement")
ax.set_title(f"What actually drives 'top 10%': post volume (Spearman rho = {rho_post:.2f})")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("images/Entropy_H4_post_volume_chart.png"); plt.close(fig)

pd.Series({k: str(v) for k, v in summary.items()}).to_csv("images/summary_stats.txt", sep="\t", header=False)
print("charts written")
