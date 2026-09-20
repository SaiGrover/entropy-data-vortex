# Round 3 - Signal Tracking

**Competition:** Data Vortex | AARUUSH'26  
**Theme:** Rebuilding the Social Engine  
**Team:** Entropy  
**Members:** Saanvi Grover & Aditya Sharma

---

## Assigned topic

**Public Reaction to a Major Software Update.**

**Event tracked:** the **iOS 27 / iPadOS 27 / macOS 27** release (14 September 2026), with the **Android 17** release (18 September 2026) as a comparison.

## What was built

A live monitoring pipeline: collect public reaction from four platforms with no paid APIs, score it with the **Round 2 sentiment model** (reused unchanged), and locate the moments where opinion turned - with statistical evidence and named causes.

| Deliverable (per rulebook) | File |
|---|---|
| Self-collected live dataset | `data/Entropy_round3_collected_posts.csv` (5,498 rows) |
| Scraping / extraction code | `Entropy_collect_data.py` |
| Real-time analysis notebook | `Entropy_02_Realtime_Analysis.ipynb` + `reports/Entropy_r3_analysis_notebook.pdf` |
| Round 3 analytical report | `reports/Entropy_round3_analytical_report.pdf` (+ `.tex` source) |

## Dataset

| | |
|---|---|
| Window | 8 Sep 2026 01:10 UTC to 20 Sep 2026 10:44 UTC (294.9 hours) |
| Collected (in-window, de-duplicated) | **5,498** posts and comments, over two snapshots |
| Analysis set (mentions a tracked release, English) | **1,403** from **1,132 distinct authors** |
| Sources | Reddit 718, Mastodon 513, Hacker News 138, Lemmy 34 |
| Event timeline | 390 news articles (used only to date real events) |
| Requests | 417 across both runs (31 failed after retries, all logged) |

**Schema:** `source, source_detail, kind, post_id, parent_id, created_utc, title, text, author_hash, score, n_replies, url, query, lang, collected_at, text_full`

**Privacy:** author names are replaced by a salted SHA-256 hash; no personal identifiers are stored. Only public, read-only endpoints are used, one request at a time, with a descriptive User-Agent.

## Sources and how they were accessed

| Source | Endpoint | Engagement available |
|---|---|---|
| Reddit | `www.reddit.com/r/*/search.rss`, `/comments/*.rss` | No - RSS omits scores |
| Hacker News | `hn.algolia.com/api/v1/search` (stories + threads) | points, comments |
| Mastodon | `{instance}/api/v1/timelines/tag/{tag}` (4 instances) | favourites + boosts |
| Lemmy | `{instance}/api/v3/search` (3 instances) | score, comments |
| Google News | `news.google.com/rss/search` | n/a (event timeline) |

Three obstacles shaped the collector. Reddit returns HTTP 403 for anonymous JSON and an interstitial page for `old.reddit.com/*.json`, so the Atom interface is used. Anonymous feeds are rate limited to roughly one request per minute, so Reddit runs in a slow lane (45 s between calls, backoff on 429) while other sources run at 1.2 s. And RSS hides popularity, so a second pass searched with `sort=top` and expanded those threads, lifting Reddit comments from 31 to **688**.

## Applying the Round 2 model

The saved ensemble (TF-IDF 0.25 + MiniLM embeddings 0.20 + three fine-tuned MiniLM seeds 0.55) is loaded unchanged. Three details were handled explicitly:

1. **Library compatibility** - the pickles were written by a newer scikit-learn that no longer sets `multi_class` on `LogisticRegression`; the attribute is restored to the trained value rather than retraining.
2. **Operating point** - the artefact carries a neutral bias of 1.05 that `predict()` applies but `predict_proba()` does not, so the bias is applied here.
3. **Truncation** - the fine-tuned component was trained with `max_len = 50` tokens, but the median post here is 74 tokens and 68% exceed 50, so long posts are split into overlapping 34-word windows and averaged.

**In-domain validation** on 150 randomly drawn, hand-labelled posts:

| Scoring configuration | Accuracy | Macro-F1 |
|---|---|---|
| As-is (truncated, no bias) | 0.653 | 0.632 |
| Neutral bias only | 0.673 | 0.653 |
| **Chunked + neutral bias (used)** | **0.687** | **0.666** |

Round 2 scored 0.723 on tweets; the residual gap is genuine domain shift. Chunking changes 12% of labels across a 400-post sample.

## Headline findings

1. **The launch soured rather than failed.** Net sentiment: **+0.05 pre-launch -> -0.12 in the first 24h -> -0.17 -> -0.37 after 72h.**
2. **Three statistically significant shifts** (Holm-corrected): pre-launch to launch (p = 0.0002), settling to later (p = 0.00001), and a sharp 12-hour turn at **15 Sep 00:00** (+0.16 to -0.26, p < 0.0001).
3. **Not a sampling artefact.** On Mastodon alone, net sentiment falls +0.43 to -0.17; positives drop 57% to 24% (p = 0.0002) and negatives rise 14% to 41% (p = 3.6e-8).
4. **Volume and engagement peak at different moments.** The release hour is the volume peak (36 posts/h, z = 97); the largest engagement peak came four days later from one Hacker News thread about **Android 17** (1,135 points, z = 183).
5. **Reliability, not design, drives complaints.** Bugs/crashes -0.67, notifications -0.61, privacy -0.42, install process -0.30, Siri -0.27 - while UI/design is the *least* negative theme at -0.10.
6. **Negative posts earn more engagement** (median 2 vs 1, Kruskal-Wallis p = 0.046), the same pattern found in Round 1.

## Reproduce

```bash
python Entropy_collect_data.py                          # full collection (~40 min; Reddit slow lane)
python Entropy_collect_data.py --append --reddit-top 12 # add a later snapshot + popularity pass
jupyter nbconvert --to notebook --execute --inplace Entropy_02_Realtime_Analysis.ipynb
cd reports && pdflatex Entropy_round3_analytical_report.tex   # twice for cross-references
```

The notebook imports the Round 2 model from `../Round2-Semantic-Recovery/model` via `Entropy_nlp_utils.SentimentEnsemble`.

## File structure

```
Round3-Signal-Tracking/
|-- Entropy_collect_data.py                    # Deliverable 2: collection script
|-- Entropy_02_Realtime_Analysis.ipynb         # Deliverable 3: analysis notebook (executed)
|-- Entropy_README_Round3.md                   # This file
|-- data/
|   |-- Entropy_round3_collected_posts.csv     # Deliverable 1: the live dataset
|   |-- Entropy_round3_news_timeline.csv       # news articles used to explain spikes
|   |-- Entropy_round3_collection_manifest.json
|   |-- raw/request_log.json.gz                # every HTTP request with status
|-- images/                                    # 7 analysis figures
|-- outputs/
|   |-- Entropy_round3_scored_posts.csv        # analysis set + model sentiment and probabilities
|   |-- Entropy_round3_metrics.json            # every number quoted in the report
|   |-- Entropy_round3_validation_sample.csv   # 150 hand-labelled posts (in-domain validation)
|   |-- Entropy_round3_sentiment_bins.csv
|   |-- Entropy_round3_activity_hourly.csv
|   |-- Entropy_round3_entity_sentiment.csv
|-- reports/
|   |-- Entropy_round3_analytical_report.pdf   # Deliverable 4
|   |-- Entropy_round3_analytical_report.tex   # LaTeX source
|   |-- Entropy_r3_common.tex                  # shared preamble
|   |-- Entropy_r3_analysis_notebook.pdf       # notebook exported to PDF for submission
```

## Limitations

- Reddit RSS exposes no scores, so engagement analysis uses Hacker News, Mastodon and Lemmy (584 scored posts).
- In-domain macro-F1 is 0.666 with a wide 95% interval ([0.578, 0.745]); only 15 of the 150 validation posts are Positive. Reported *levels* are noisier than reported *changes*.
- Validation labels come from a single annotator, so there is no inter-annotator agreement figure.
- Platform mix shifts across the window; the within-platform comparison is the correction.
- English-only analysis; X, TikTok and YouTube need paid API access and are out of scope.

## Tools

Python 3, urllib (no scraping framework), pandas, numpy, scipy, scikit-learn, matplotlib, Jupyter, LaTeX.
