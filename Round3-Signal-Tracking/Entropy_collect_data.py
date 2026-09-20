"""
Team Entropy - Data Vortex Round 3 (Signal Tracking)
Topic: Public Reaction to a Major Software Update
       primary   iOS 27 / iPadOS 27 / macOS 27 (released 14 September 2026)
       comparison Android 17 (released 18 September 2026)

Collects public posts and comments from four free, key-less public APIs, plus a news
timeline used to explain spikes:

    reddit      www.reddit.com Atom feeds (search + comment threads).  The JSON API
                serves an interstitial page to anonymous clients and api.reddit.com
                returns 403, so the RSS/Atom interface is used instead.  Anonymous
                feeds are rate limited to roughly one request per minute, hence the
                dedicated slow lane below.
    hackernews  Algolia search API (stories + their full comment threads)
    mastodon    public hashtag timelines on four instances
    lemmy       /api/v3/search on three instances
    googlenews  RSS search - event timeline only, never counted as public reaction

Usage:
    python Entropy_collect_data.py                     # full collection (~40 min)
    python Entropy_collect_data.py --skip-reddit       # fast run, no Reddit slow lane
    python Entropy_collect_data.py --max-pages 1       # smoke test

Politeness and ethics: read-only public endpoints, one request at a time, a delay
between calls, a descriptive User-Agent, retries with backoff.  Author names are
replaced by a salted hash, so no personal identifiers are stored.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA, RAW = ROOT / "data", ROOT / "data" / "raw"
USER_AGENT = "EntropyDataVortex/1.0 (AARUUSH26 student research project; team Entropy)"
DELAY, REDDIT_DELAY = 1.2, 45.0
SALT = "entropy-round3"
WINDOW_START = "2026-09-08T00:00:00+00:00"

PRIMARY_QUERIES = ["iOS 27", "iPadOS 27", "macOS 27", "Apple Intelligence"]
COMPARISON_QUERIES = ["Android 17"]
REDDIT_SEARCHES = [("apple", "iOS 27"), ("apple", "Apple Intelligence"), ("ios", "iOS 27"), ("iphone", "iOS 27"),
                   ("ipad", "iPadOS 27"), ("macos", "macOS 27"), ("technology", "iOS 27"),
                   ("android", "Android 17"), ("GooglePixel", "Android 17"), (None, "iOS 27"), (None, "Android 17")]
REDDIT_LISTINGS = ["apple", "ios", "android"]
MASTODON = {
    "mastodon.social": ["ios27", "ipados27", "macos27", "appleintelligence", "android17", "iphone", "apple"],
    "mstdn.social": ["ios27", "macos27", "android17", "apple"],
    "fosstodon.org": ["ios27", "android17", "apple"],
    "hachyderm.io": ["ios27", "android17", "apple"],
}
LEMMY = ["lemmy.world", "lemmy.ml", "programming.dev"]
NS = {"a": "http://www.w3.org/2005/Atom"}
SESSION_LOG: list[dict] = []


def anon(author: str | None) -> str:
    if not author:
        return "unknown"
    return "u_" + hashlib.sha256((SALT + str(author)).encode()).hexdigest()[:12]


def iso(ts: float) -> str:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()


_REDDIT_BOILERPLATE = re.compile(
    r"submitted by\s*/?u?/?\S*|\[link\]|\[comments\]|/u/\w+|/r/\w+", re.IGNORECASE)


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>|</p>", " ", text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def clean_feed_text(text: str) -> str:
    """Remove the 'submitted by /u/x [link] [comments]' footer Reddit adds to every Atom entry."""
    text = _REDDIT_BOILERPLATE.sub(" ", strip_html(text))
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch(url: str, tries: int = 3, timeout: int = 30, delay: float = DELAY) -> bytes | None:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
            SESSION_LOG.append({"url": url, "status": 200, "bytes": len(body), "at": iso(time.time())})
            time.sleep(delay)
            return body
        except Exception as exc:  # noqa: BLE001 - log and continue; partial collection is acceptable
            status = getattr(exc, "code", type(exc).__name__)
            SESSION_LOG.append({"url": url, "status": str(status), "bytes": 0, "at": iso(time.time())})
            print(f"    ! {status} attempt {attempt + 1}: {url[:100]}", flush=True)
            time.sleep(delay * (attempt + 2))
    return None


def fetch_json(url: str):
    body = fetch(url)
    if body is None:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        print(f"    ! non-JSON response: {url[:100]}", flush=True)
        return None


def row(**kw) -> dict:
    base = dict(source="", source_detail="", kind="", post_id="", parent_id="", created_utc="",
                title="", text="", author_hash="", score=None, n_replies=None, url="", query="", lang="",
                collected_at=iso(time.time()))
    base.update(kw)
    return base


# --------------------------------------------------------------------------- Reddit (Atom)
def reddit_feed(url: str) -> list[ET.Element]:
    body = fetch(url, tries=3, timeout=40, delay=REDDIT_DELAY)
    if not body:
        return []
    try:
        return ET.fromstring(body).findall("a:entry", NS)
    except ET.ParseError:
        print("    ! Reddit returned HTML instead of a feed", flush=True)
        return []


def reddit_entry(entry: ET.Element, query: str) -> dict:
    eid = entry.findtext("a:id", "", NS)
    content = clean_feed_text(entry.findtext("a:content", "", NS))
    link = entry.find("a:link", NS)
    author = entry.find("a:author/a:name", NS)
    category = entry.find("a:category", NS)
    return row(source="reddit", source_detail=(category.get("label") if category is not None else ""),
               kind="comment" if eid.startswith("t1_") else "post", post_id=eid,
               created_utc=entry.findtext("a:published", entry.findtext("a:updated", "", NS), NS),
               title=entry.findtext("a:title", "", NS) if eid.startswith("t3_") else "",
               text=content, author_hash=anon(author.text if author is not None else None),
               url=link.get("href") if link is not None else "", query=query)


def reddit_search(sub: str | None, query: str, sort: str = "new", period: str = "month") -> list[dict]:
    params = {"q": query, "sort": sort, "t": period, "limit": "100"}
    if sub:
        params["restrict_sr"] = "1"
    base = f"https://www.reddit.com/r/{sub}/search.rss" if sub else "https://www.reddit.com/search.rss"
    return [reddit_entry(e, query) for e in reddit_feed(f"{base}?{urllib.parse.urlencode(params)}")]


def reddit_comments(post_id: str) -> list[dict]:
    short = post_id.split("_")[-1]
    out = []
    for e in reddit_feed(f"https://www.reddit.com/comments/{short}.rss?limit=200&sort=top"):
        r = reddit_entry(e, "comment_thread")
        if r["kind"] == "comment" and len(r["text"]) >= 15:
            r["parent_id"] = post_id
            out.append(r)
    return out


# --------------------------------------------------------------------------- Hacker News
def hn_stories(query: str, since: int, max_pages: int) -> list[dict]:
    out = []
    for page in range(max_pages):
        data = fetch_json("https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(
            {"query": query, "tags": "story", "numericFilters": f"created_at_i>{since}", "hitsPerPage": 100, "page": page}))
        if not data:
            break
        for h in data.get("hits", []):
            out.append(row(source="hackernews", source_detail="story", kind="post", post_id="hn_" + str(h["objectID"]),
                           created_utc=h["created_at"], title=h.get("title") or "", text=h.get("story_text") or "",
                           author_hash=anon(h.get("author")), score=int(h.get("points") or 0),
                           n_replies=int(h.get("num_comments") or 0),
                           url=f"https://news.ycombinator.com/item?id={h['objectID']}", query=query))
        if page + 1 >= data.get("nbPages", 0):
            break
    return out


def hn_comments(story_id: str, max_pages: int = 5) -> list[dict]:
    out = []
    for page in range(max_pages):
        data = fetch_json("https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(
            {"tags": f"comment,story_{story_id}", "hitsPerPage": 100, "page": page}))
        if not data:
            break
        for h in data.get("hits", []):
            text = strip_html(h.get("comment_text") or "")
            if text:
                out.append(row(source="hackernews", source_detail="comment", kind="comment",
                               post_id="hn_" + str(h["objectID"]), parent_id="hn_" + str(h.get("parent_id") or story_id),
                               created_utc=h["created_at"], text=text, author_hash=anon(h.get("author")),
                               url=f"https://news.ycombinator.com/item?id={h['objectID']}", query="comment_thread"))
        if page + 1 >= data.get("nbPages", 0):
            break
    return out


# --------------------------------------------------------------------------- Mastodon
def mastodon_tag(instance: str, tag: str, max_pages: int) -> list[dict]:
    out, max_id = [], None
    for _ in range(max_pages):
        params = {"limit": "40"}
        if max_id:
            params["max_id"] = max_id
        data = fetch_json(f"https://{instance}/api/v1/timelines/tag/{tag}?{urllib.parse.urlencode(params)}")
        if not data:
            break
        for s in data:
            text = strip_html(s.get("content", ""))
            if text:
                out.append(row(source="mastodon", source_detail=instance, kind="post", post_id="m_" + str(s["id"]),
                               created_utc=s["created_at"], text=text,
                               author_hash=anon((s.get("account") or {}).get("acct")),
                               score=int(s.get("favourites_count", 0)) + int(s.get("reblogs_count", 0)),
                               n_replies=int(s.get("replies_count", 0)), url=s.get("url", ""),
                               query="#" + tag, lang=s.get("language") or ""))
        max_id = data[-1]["id"] if data else None
        if not max_id or len(data) < 40:
            break
    return out


# --------------------------------------------------------------------------- Lemmy
def lemmy_search(instance: str, query: str, max_pages: int) -> list[dict]:
    out = []
    for page in range(1, max_pages + 1):
        data = fetch_json(f"https://{instance}/api/v3/search?" + urllib.parse.urlencode(
            {"q": query, "type_": "All", "sort": "New", "limit": 50, "page": page}))
        if not data:
            break
        posts, comments = data.get("posts", []), data.get("comments", [])
        for p in posts:
            post, counts = p["post"], p.get("counts", {})
            out.append(row(source="lemmy", source_detail=instance + "/" + p.get("community", {}).get("name", ""),
                           kind="post", post_id="l_" + str(post["id"]), created_utc=post["published"],
                           title=post.get("name", ""), text=post.get("body", "") or "",
                           author_hash=anon(p.get("creator", {}).get("name")), score=int(counts.get("score", 0)),
                           n_replies=int(counts.get("comments", 0)), url=post.get("ap_id", ""), query=query))
        for c in comments:
            com, counts = c["comment"], c.get("counts", {})
            out.append(row(source="lemmy", source_detail=instance + "/" + c.get("community", {}).get("name", ""),
                           kind="comment", post_id="lc_" + str(com["id"]), created_utc=com["published"],
                           text=com.get("content", ""), author_hash=anon(c.get("creator", {}).get("name")),
                           score=int(counts.get("score", 0)), url=com.get("ap_id", ""), query=query))
        if not posts and not comments:
            break
    return out


# --------------------------------------------------------------------------- Google News (event timeline)
def google_news(query: str) -> list[dict]:
    body = fetch("https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}))
    if not body:
        return []
    out = []
    for item in ET.fromstring(body).iter("item"):
        pub = item.findtext("pubDate") or ""
        try:
            ts = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            ts = pub
        src = item.find("source")
        out.append({"query": query, "published_utc": ts, "title": item.findtext("title") or "",
                    "publisher": src.text if src is not None else "", "url": item.findtext("link") or ""})
    return out


# --------------------------------------------------------------------------- driver
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=6)
    ap.add_argument("--comment-threads", type=int, default=14, help="Reddit threads to expand (slow lane)")
    ap.add_argument("--hn-threads", type=int, default=30)
    ap.add_argument("--skip-reddit", action="store_true")
    ap.add_argument("--window-start", default=WINDOW_START)
    ap.add_argument("--append", action="store_true",
                    help="merge this run into the existing dataset instead of replacing it (second snapshot)")
    ap.add_argument("--reddit-top", type=int, default=0,
                    help="also search Reddit by popularity (sort=top) and expand that many threads")
    args = ap.parse_args()

    DATA.mkdir(exist_ok=True)
    started = iso(time.time())
    rows: list[dict] = []
    queries = PRIMARY_QUERIES + COMPARISON_QUERIES

    if not args.skip_reddit:
        print("[1/5] Reddit (Atom feeds, slow lane ~45 s/request)", flush=True)
        for sub, q in REDDIT_SEARCHES:
            got = reddit_search(sub, q)
            print(f"  {'r/' + sub if sub else 'site-wide':16s} {q:20s} {len(got):4d}", flush=True)
            rows += got
        for sub in REDDIT_LISTINGS:
            got = [reddit_entry(e, "new_listing") for e in reddit_feed(f"https://www.reddit.com/r/{sub}/new.rss?limit=100")]
            print(f"  r/{sub:15s} {'new listing':20s} {len(got):4d}", flush=True)
            rows += got

        if args.reddit_top:
            print(f"[1b/5] Reddit popularity pass (sort=top, this week)", flush=True)
            for sub, q in REDDIT_SEARCHES[:8]:
                got = reddit_search(sub, q, sort="top", period="week")
                print(f"  {'r/' + sub if sub else 'site-wide':16s} {q:20s} {len(got):4d} (top)", flush=True)
                rows += got

        posts = {r["post_id"]: r for r in rows if r["source"] == "reddit" and r["kind"] == "post"}
        relevant = [r for r in posts.values()
                    if re.search(r"ios\s?27|ipados\s?27|macos\s?27|apple intelligence|android\s?17|update|siri",
                                 (r["title"] + " " + r["text"]).lower())]
        # Feeds do not expose scores, but a sort=top search returns posts in popularity
        # order, so entries seen in that pass are expanded first.
        top_ids = [r["post_id"] for r in rows if r.get("query") and r["kind"] == "post" and r["source"] == "reddit"]
        rank = {pid: i for i, pid in enumerate(top_ids)}
        relevant.sort(key=lambda r: (rank.get(r["post_id"], 10**6), r["created_utc"]))
        n_threads = args.comment_threads + (args.reddit_top or 0)
        print(f"[2/5] Reddit comment threads for {min(n_threads, len(relevant))} posts", flush=True)
        for r in relevant[:n_threads]:
            got = reddit_comments(r["post_id"])
            print(f"  {r['source_detail']:14s} {len(got):4d} comments | {r['title'][:55]}", flush=True)
            rows += got
    else:
        print("[1-2/5] Reddit skipped (--skip-reddit)", flush=True)

    print("[3/5] Hacker News", flush=True)
    since = int(datetime.fromisoformat(args.window_start).timestamp())
    hn_posts = []
    for q in queries:
        got = hn_stories(q, since, 2)
        print(f"  stories {q:20s} {len(got):4d}", flush=True)
        hn_posts += got
    rows += hn_posts
    seen = set()
    for r in sorted(hn_posts, key=lambda r: -(r["n_replies"] or 0))[:args.hn_threads]:
        sid = r["post_id"].replace("hn_", "")
        if r["n_replies"] and sid not in seen:
            seen.add(sid)
            got = hn_comments(sid)
            print(f"  comments {r['title'][:55]:57s} {len(got):4d}", flush=True)
            rows += got

    print("[4/5] Mastodon and Lemmy", flush=True)
    for instance, tags in MASTODON.items():
        for tag in tags:
            got = mastodon_tag(instance, tag, args.max_pages)
            print(f"  {instance:18s} #{tag:18s} {len(got):4d}", flush=True)
            rows += got
    for instance in LEMMY:
        for q in queries:
            got = lemmy_search(instance, q, 2)
            print(f"  {instance:18s} {q:20s} {len(got):4d}", flush=True)
            rows += got

    print("[5/5] Google News timeline", flush=True)
    events = []
    for q in queries:
        got = google_news(q)
        print(f"  {q:20s} {len(got):4d} articles", flush=True)
        events += got

    import pandas as pd

    df = pd.DataFrame(rows)
    df["text_full"] = (df.title.fillna("") + " " + df.text.fillna("")).str.strip()
    df = df[df.text_full.str.len() >= 15]
    df["created_utc"] = pd.to_datetime(df.created_utc, format="mixed", utc=True, errors="coerce")
    df = df.dropna(subset=["created_utc"])
    before_window = len(df)
    df = df[df.created_utc >= pd.Timestamp(args.window_start)]
    out_csv = DATA / "Entropy_round3_collected_posts.csv"
    new_rows = len(df)
    if args.append and out_csv.exists():
        prev = pd.read_csv(out_csv)
        prev["created_utc"] = pd.to_datetime(prev.created_utc, format="mixed", utc=True, errors="coerce")
        if "collected_at" not in prev.columns:
            prev["collected_at"] = ""
        df = pd.concat([prev, df], ignore_index=True)
        print(f"append mode: {len(prev)} existing + {new_rows} fetched", flush=True)
    df = (df.drop_duplicates(subset=["source", "post_id"])
            .drop_duplicates(subset=["text_full", "author_hash"])
            .sort_values("created_utc").reset_index(drop=True))
    df.to_csv(out_csv, index=False)

    ev = pd.DataFrame(events)
    if not ev.empty:
        ev["published_utc"] = pd.to_datetime(ev.published_utc, format="mixed", utc=True, errors="coerce")
        ev = ev.dropna(subset=["published_utc"])
        ev = ev[ev.published_utc >= pd.Timestamp(args.window_start)].drop_duplicates(subset=["title"]).sort_values("published_utc")
        ev.to_csv(DATA / "Entropy_round3_news_timeline.csv", index=False)

    manifest = {
        "collected_by": "Team Entropy (Saanvi Grover, Aditya Sharma)",
        "topic": "Public reaction to a major software update: iOS 27 / iPadOS 27 / macOS 27, with Android 17 as comparison",
        "started_utc": started, "finished_utc": iso(time.time()),
        "queries": queries, "reddit_searches": [[s, q] for s, q in REDDIT_SEARCHES],
        "mastodon": MASTODON, "lemmy": LEMMY,
        "requests": len(SESSION_LOG), "failed_requests": sum(1 for r in SESSION_LOG if r["status"] != 200),
        "rows_raw": len(rows), "rows_fetched_this_run": int(new_rows), "rows_final": int(len(df)),
        "append_mode": bool(args.append), "reddit_popularity_pass": int(args.reddit_top),
        "window_start": args.window_start,
        "by_source_kind": df.groupby(["source", "kind"]).size().unstack(fill_value=0).to_dict(),
        "engagement_available": {"reddit": False, "hackernews": True, "mastodon": True, "lemmy": True},
        "time_span": {"first": str(df.created_utc.min()), "last": str(df.created_utc.max())},
        "unique_authors": int(df.author_hash.nunique()), "news_articles": int(len(ev)),
    }
    (DATA / "Entropy_round3_collection_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    RAW.mkdir(parents=True, exist_ok=True)
    with gzip.open(RAW / "request_log.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(SESSION_LOG, fh)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    sys.exit(main())
