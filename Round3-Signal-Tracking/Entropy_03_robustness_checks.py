"""
Round 3 - Signal Tracking: robustness checks and baselines.

Team Entropy | Saanvi Grover & Aditya Sharma | Data Vortex, AARUUSH'26

These checks are deliberately kept out of the main analysis notebook: each one
interrogates a claim the notebook already makes, rather than producing a new
claim of its own, and each must be re-runnable on its own after the notebook has
been re-executed.

    python Entropy_03_robustness_checks.py

Reads  : outputs/Entropy_round3_scored_posts.csv
         outputs/Entropy_round3_validation_sample.csv
         data/Entropy_round3_news_timeline.csv
Writes : outputs/Entropy_round3_robustness.json      every number quoted below
         outputs/Entropy_round3_annotation_round2.csv  blank sheet for a 2nd annotator
         images/Entropy_r3_fig8_periods_ci.png
         images/Entropy_r3_fig9_alerting.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
IMG = HERE / "images"
SEED, N_BOOT = 42, 8000
LABELS = ["Negative", "Neutral", "Positive"]
PERIODS = ["Pre-launch (8-14 Sep)", "Launch +0-24h", "Settling +24-72h", "Later (72h+)"]
LAUNCH = pd.Timestamp("2026-09-14 17:00", tz="UTC")

BG, FG, MUT = "#0b120f", "#eef2ee", "#9bb0a2"
SAGE, SAND, CLAY, TEAL = "#7fb582", "#d9b26a", "#d9705e", "#5ea38f"
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "axes.edgecolor": "#3a4a40",
    "xtick.color": MUT, "ytick.color": MUT, "grid.color": "#22322a",
    "font.size": 10, "axes.titlesize": 12, "axes.grid": True, "grid.alpha": .6,
})

rng = np.random.default_rng(SEED)


def net_ci(counts, n_boot=N_BOOT):
    """Bootstrap a 95% interval for net sentiment from a bin's three class counts."""
    neg, neu, pos = counts
    n = neg + neu + pos
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0
    draws = rng.multinomial(n, [neg / n, neu / n, pos / n], size=n_boot)
    vals = (draws[:, 2] - draws[:, 0]) / n
    return (pos - neg) / n, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)), int(n)


def counts_of(series):
    return tuple(int((series == c).sum()) for c in LABELS)


def main() -> None:
    scored = pd.read_csv(OUT / "Entropy_round3_scored_posts.csv")
    scored["created_utc"] = pd.to_datetime(scored.created_utc, format="mixed", utc=True)
    res: dict = {}

    # ---------------------------------------------------------------- 1. levels
    # The headline trend quotes a level for each period. A level is only a claim
    # if its interval excludes zero - otherwise it is "indistinguishable from
    # neutral", which is a different sentence.
    periods = {}
    for per in PERIODS:
        net, lo, hi, n = net_ci(counts_of(scored.loc[scored.period == per, "sentiment"]))
        periods[per] = {"n": n, "net": round(net, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4),
                        "distinguishable_from_zero": bool(lo > 0 or hi < 0)}
        print(f"{per:24} n={n:4}  net {net:+.3f}  [{lo:+.3f}, {hi:+.3f}]"
              f"  {'' if (lo > 0 or hi < 0) else '<- includes zero'}")
    res["period_levels"] = periods

    # differences between periods, which is where the actual finding lives
    def boot_net(per):
        neg, neu, pos = counts_of(scored.loc[scored.period == per, "sentiment"])
        n = neg + neu + pos
        draws = rng.multinomial(n, [neg / n, neu / n, pos / n], size=N_BOOT)
        return (draws[:, 2] - draws[:, 0]) / n

    base = boot_net(PERIODS[0])
    diffs = {}
    for per in PERIODS[1:]:
        d = base - boot_net(per)
        lo, hi = np.percentile(d, [2.5, 97.5])
        diffs[per] = {"drop_from_baseline": round(float(d.mean()), 4),
                      "ci_low": round(float(lo), 4), "ci_high": round(float(hi), 4),
                      "significant": bool(lo > 0)}
        print(f"  baseline -> {per:22} drop {d.mean():+.3f}  [{lo:+.3f}, {hi:+.3f}]")
    res["period_differences"] = diffs

    # ------------------------------------------------- 2. is this a pile-on?
    # Any sentiment-shift claim invites the question "was that a few loud
    # accounts?". Authors are salted hashes, so this costs nothing to answer.
    vc = scored.author_hash.value_counts()
    neg = scored[scored.sentiment == "Negative"]
    vcn = neg.author_hash.value_counts()
    res["author_concentration"] = {
        "posts": int(len(scored)), "authors": int(len(vc)),
        "posts_per_author": round(len(scored) / len(vc), 3),
        "busiest_author_posts": int(vc.iloc[0]),
        "top10_share_of_corpus": round(float(vc.head(10).sum() / len(scored)), 4),
        "negative_posts": int(len(neg)), "negative_authors": int(len(vcn)),
        "top10_share_of_negatives": round(float(vcn.head(10).sum() / len(neg)), 4),
        "share_of_authors_posting_once": round(float((vc == 1).mean()), 4),
    }
    print(f"\nauthors {len(vc)} for {len(scored)} posts; {len(vcn)} distinct authors behind "
          f"{len(neg)} negative posts; top-10 hold {vc.head(10).sum() / len(scored):.1%} of the corpus")

    # ------------------------------------------- 3. an off-the-shelf baseline
    # Beating a lexicon tool in-domain is the comparison a reviewer asks for.
    val = pd.read_csv(OUT / "Entropy_round3_validation_sample.csv")
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        vader = SentimentIntensityAnalyzer()

        def vader_label(text):
            c = vader.polarity_scores(str(text))["compound"]
            return "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral"

        vpred = val.text_full.map(vader_label)
        res["vader_baseline"] = {
            "n": int(len(val)),
            "macro_f1": round(float(f1_score(val.human_label, vpred, average="macro")), 4),
            "accuracy": round(float((vpred == val.human_label).mean()), 4),
            "per_class_f1": {c: round(float(f1_score(val.human_label, vpred, average=None,
                                                     labels=[c])[0]), 4) for c in LABELS},
        }
        final = val.merge(scored[["post_id", "sentiment"]], on="post_id",
                          how="left", suffixes=("_asis", "_final"))
        ours = {
            "shipped_macro_f1": round(float(f1_score(final.human_label, final.sentiment_final,
                                                     average="macro")), 4),
            "shipped_accuracy": round(float((final.sentiment_final == final.human_label).mean()), 4),
            "as_is_macro_f1": round(float(f1_score(val.human_label, val.sentiment, average="macro")), 4),
        }
        res["our_model_on_same_labels"] = ours
        print(f"\nVADER  macro-F1 {res['vader_baseline']['macro_f1']:.3f}  "
              f"acc {res['vader_baseline']['accuracy']:.3f}")
        print(f"ours   macro-F1 {ours['shipped_macro_f1']:.3f}  acc {ours['shipped_accuracy']:.3f}"
              f"  (as-is scoring would be {ours['as_is_macro_f1']:.3f})")
    except ImportError:
        res["vader_baseline"] = {"error": "vaderSentiment not installed"}
        print("\nVADER not installed - skipping the lexicon baseline")

    # --------------------------------------------- 4. would it have alerted?
    # Analysis after the fact is not monitoring. Replay a rule over the timeline
    # and report when it fires against when the news actually broke.
    bins = (scored.set_index("created_utc").resample("12h")
            .agg(neg=("sentiment", lambda s: (s == "Negative").sum()),
                 neu=("sentiment", lambda s: (s == "Neutral").sum()),
                 pos=("sentiment", lambda s: (s == "Positive").sum())))
    bins["n"] = bins.neg + bins.neu + bins.pos
    bins["net"] = np.where(bins.n > 0, (bins.pos - bins.neg) / bins.n.clip(lower=1), np.nan)
    THRESH, MIN_N, CONSEC = -0.15, 20, 2
    fired, run = None, 0
    for ts, r in bins.iterrows():
        if r.n >= MIN_N and r.net <= THRESH:
            run += 1
            if run >= CONSEC and fired is None:
                fired = ts
        else:
            run = 0
    res["alerting"] = {
        "rule": f"net sentiment <= {THRESH} for {CONSEC} consecutive 12h bins with n >= {MIN_N}",
        "first_fired": str(fired) if fired is not None else None,
        "launch": str(LAUNCH),
        "hours_after_launch": round(float((fired - LAUNCH).total_seconds() / 3600), 1)
        if fired is not None else None,
        "bins_evaluated": int(bins.n.ge(MIN_N).sum()),
        "false_alarms_pre_launch": int(((bins.index < LAUNCH) & (bins.n >= MIN_N)
                                        & (bins.net <= THRESH)).sum()),
    }
    print(f"\nalert rule fires {res['alerting']['first_fired']} "
          f"({res['alerting']['hours_after_launch']} h after launch); "
          f"{res['alerting']['false_alarms_pre_launch']} pre-launch bins breached the threshold")

    # ------------------------------------------------- 5. what the topics are
    if "nmf_topic" in scored.columns:
        topics = {}
        for t, grp in scored.groupby("nmf_topic"):
            net, lo, hi, n = net_ci(counts_of(grp.sentiment))
            topics[str(int(t))] = {"n": n, "net": round(net, 4),
                                   "ci_low": round(lo, 4), "ci_high": round(hi, 4)}
        res["nmf_topics"] = topics
        print(f"\n{len(topics)} NMF topics scored")

    # ------------------------- 6. two independent human annotators, and kappa
    # The original 150 labels came from one annotator. Two humans then labelled
    # the same posts independently, without seeing those labels or the model's.
    # Where they agree, that agreement becomes the reference standard - which is
    # a better yardstick than any single person's judgement, including ours.
    def norm(col):
        return col.astype(str).str.strip().str.capitalize()

    sheets = {}
    for who in ("saanvi", "aditya"):
        f = OUT / f"Entropy_round3_annotation_{who}.csv"
        if f.exists():
            df = pd.read_csv(f)
            df["label"] = norm(df.human_label)
            sheets[who] = df.loc[df.label.isin(LABELS), ["post_id", "label"]]

    if len(sheets) == 2:
        (n1, a1), (n2, a2) = sheets.items()
        both = a1.merge(a2, on="post_id", suffixes=("_1", "_2"))
        kappa = float(cohen_kappa_score(both.label_1, both.label_2))
        agree = both[both.label_1 == both.label_2]
        gold = agree.rename(columns={"label_1": "gold"})[["post_id", "gold"]]

        # every scorer is now measured against the human consensus
        shipped = scored[["post_id", "sentiment", "text_full"]]
        g = gold.merge(shipped, on="post_id", how="inner")
        asis = val[["post_id", "sentiment"]].rename(columns={"sentiment": "asis"})
        g = g.merge(asis, on="post_id", how="left")

        def macro(truth, pred):
            return round(float(f1_score(truth, pred, average="macro")), 4)

        cons = {
            "annotators": [n1, n2],
            "n_double_labelled": int(len(both)),
            "cohens_kappa": round(kappa, 4),
            "raw_agreement": round(float((both.label_1 == both.label_2).mean()), 4),
            "n_consensus": int(len(gold)),
            "n_disagreements_excluded": int(len(both) - len(gold)),
            "consensus_balance": {k: int(v) for k, v in gold.gold.value_counts().items()},
            "model_macro_f1": macro(g.gold, g.sentiment),
            "model_accuracy": round(float((g.gold == g.sentiment).mean()), 4),
            "as_is_macro_f1": macro(g.gold, g.asis),
        }

        # is the shipped scoring actually better than plain truncation here?
        rng2 = np.random.default_rng(SEED)
        diffs = []
        for _ in range(4000):
            idx = rng2.integers(0, len(g), len(g))
            sam = g.iloc[idx]
            if sam.gold.nunique() < 3:
                continue
            diffs.append(macro(sam.gold, sam.sentiment) - macro(sam.gold, sam.asis))
        diffs = np.array(diffs)
        cons["shipped_minus_as_is"] = {
            "point": round(float(cons["model_macro_f1"] - cons["as_is_macro_f1"]), 4),
            "ci_low": round(float(np.percentile(diffs, 2.5)), 4),
            "ci_high": round(float(np.percentile(diffs, 97.5)), 4),
            "distinguishable": bool(np.percentile(diffs, 2.5) > 0 or np.percentile(diffs, 97.5) < 0),
        }

        # how far each human sits from the original single-annotator labels
        first = val[["post_id", "human_label"]].copy()
        first["label"] = norm(first.human_label)
        cons["kappa_vs_first_annotator"] = {
            w: round(float(cohen_kappa_score(
                sheets[w].merge(first, on="post_id").label_x,
                sheets[w].merge(first, on="post_id").label_y)), 4)
            for w in sheets
        }

        if "vader_baseline" in res and "error" not in res["vader_baseline"]:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            vv = SentimentIntensityAnalyzer()

            def vlab(t):
                c = vv.polarity_scores(str(t))["compound"]
                return "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral"

            cons["vader_macro_f1"] = macro(g.gold, g.text_full.map(vlab))

        res["human_consensus"] = cons
        gold.merge(scored[["post_id", "text_full", "sentiment"]], on="post_id").to_csv(
            OUT / "Entropy_round3_consensus_labels.csv", index=False)
        print(f"\nkappa({n1}, {n2}) = {kappa:.3f} on {len(both)} posts "
              f"({cons['raw_agreement']:.1%} raw agreement)")
        print(f"consensus set {len(gold)} posts ({cons['n_disagreements_excluded']} disagreements set aside)")
        print(f"model vs consensus: macro-F1 {cons['model_macro_f1']:.4f} "
              f"(as-is {cons['as_is_macro_f1']:.4f}, VADER {cons.get('vader_macro_f1', float('nan')):.4f})")
        d = cons["shipped_minus_as_is"]
        print(f"shipped - as-is: {d['point']:+.4f} [{d['ci_low']:+.4f}, {d['ci_high']:+.4f}] "
              f"{'(distinguishable)' if d['distinguishable'] else '(indistinguishable from zero)'}")
    else:
        sheet = val[["post_id", "source", "created_utc", "text_full"]].copy()
        sheet["human_label"] = ""
        sheet["annotator"] = ""
        sheet.sample(frac=1.0, random_state=SEED).reset_index(drop=True).to_csv(
            OUT / "Entropy_round3_annotation_round2.csv", index=False)
        res["human_consensus"] = {
            "status": "pending",
            "note": "fill outputs/Entropy_round3_annotation_<name>.csv for two annotators and re-run",
        }
        print("\nfewer than two annotation sheets found - wrote a blank one")

    # --------------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    xs = np.arange(len(PERIODS))
    nets = [periods[p]["net"] for p in PERIODS]
    los = [periods[p]["net"] - periods[p]["ci_low"] for p in PERIODS]
    his = [periods[p]["ci_high"] - periods[p]["net"] for p in PERIODS]
    cols = [SAND if not periods[p]["distinguishable_from_zero"] else
            (CLAY if periods[p]["net"] < 0 else SAGE) for p in PERIODS]
    # markers are drawn separately: errorbar takes one face colour, and each
    # period needs its own (sand = interval crosses zero)
    ax.errorbar(xs, nets, yerr=[los, his], fmt="none", capsize=6, lw=1.8, ecolor="#5f7568")
    for i, p in enumerate(PERIODS):
        ax.scatter([xs[i]], [periods[p]["net"]], s=75, color=cols[i], zorder=3)
        # above the whisker, not below: the lowest period sits on the x axis
        ax.annotate(f"n={periods[p]['n']}", (xs[i], periods[p]["ci_high"]),
                    textcoords="offset points", xytext=(0, 9), ha="center",
                    color=MUT, fontsize=8.5)
    ax.axhline(0, color="#5f7568", lw=1, ls="--")
    ax.set_xticks(xs)
    ax.set_xticklabels(["Pre-launch", "+0-24h", "+24-72h", "72h+"])
    ax.set_ylabel("net sentiment (pos - neg)")
    ax.set_title("Net sentiment by period, with 95% bootstrap intervals\n"
                 "the pre-launch interval crosses zero: the baseline is not measurably positive",
                 fontsize=10.5, color=FG, loc="left")
    fig.tight_layout()
    fig.savefig(IMG / "Entropy_r3_fig8_periods_ci.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    ok = bins[bins.n >= MIN_N]
    ax.plot(ok.index, ok.net, color=SAGE, lw=2, marker="o", ms=4, label="net sentiment / 12h")
    ax.axhline(THRESH, color=CLAY, lw=1.3, ls=":", label=f"alert threshold ({THRESH})")
    ax.axvline(LAUNCH, color=SAND, lw=1.3, ls="--", label="iOS 27 ships")
    if fired is not None:
        ax.axvline(fired, color=TEAL, lw=1.8, label=f"rule fires ({res['alerting']['hours_after_launch']:.0f} h later)")
    ax.axhline(0, color="#5f7568", lw=.9)
    ax.set_ylabel("net sentiment")
    ax.set_title("Replaying a monitoring rule over the collected window", fontsize=10.5, color=FG, loc="left")
    ax.legend(fontsize=8.5, facecolor=BG, edgecolor="#3a4a40", labelcolor=FG)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(IMG / "Entropy_r3_fig9_alerting.png", dpi=170)
    plt.close(fig)

    (OUT / "Entropy_round3_robustness.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT / 'Entropy_round3_robustness.json'} and 2 figures")


if __name__ == "__main__":
    main()
