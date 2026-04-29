"""
Countercurrent.ai — Layer 1: Ingestion Hub
Multi-source data extraction via Apify.

Actor IDs verified April 2026:
  Web:       apify/website-content-crawler
  Reddit:    trudax/reddit-scraper
  Twitter:   apidojo/tweet-scraper
  TikTok:    clockworks/tiktok-scraper
  YouTube:   apify/youtube-scraper
  Instagram: apify/instagram-scraper
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, asdict

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

# ── Schema ────────────────────────────────────────────────────────────────────

@dataclass
class Signal:
    id: str
    title: str
    content: str
    source: str
    url: str
    timestamp: str
    category: Optional[str]
    client_tag: Optional[str]
    raw_meta: dict


def _make_id(url: str, timestamp: str) -> str:
    return hashlib.sha256(f"{url}{timestamp}".encode()).hexdigest()[:16]


def _clean_title(raw: str, fallback_content: str = "", max_len: int = 120) -> str:
    """Return a clean title, falling back to first line of content."""
    if raw and raw.strip() and raw.strip().lower() not in ["none", "null", "(no title)"]:
        return raw.strip()[:max_len]
    for line in fallback_content.splitlines():
        line = line.strip()
        if len(line) > 15:
            return line[:max_len]
    return "(no title)"


# ── Apify Client ──────────────────────────────────────────────────────────────

class ApifyIngestionClient:

    def __init__(self, api_token: Optional[str] = None):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise EnvironmentError(
                "APIFY_API_TOKEN not found. Set it in your .env file."
            )
        self.client = ApifyClient(token)

    # ── Web ───────────────────────────────────────────────────────────────────

    def scrape_web(
        self,
        start_urls: list[str],
        max_pages_per_url: int = 3,
        client_tag: Optional[str] = None,
    ) -> list[Signal]:
        print(f"[Web] Crawling {len(start_urls)} URL(s)...")

        run_input = {
            "startUrls": [{"url": u} for u in start_urls],
            "maxCrawlPages": max_pages_per_url * len(start_urls),
            "crawlerType": "playwright:firefox",
            "removeElementsCssSelector": "nav, footer, header, .ads, .sidebar, .cookie-banner",
        }

        run = self.client.actor("apify/website-content-crawler").call(run_input=run_input)
        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        signals = []
        for item in items:
            ts  = item.get("loadedTime") or datetime.now(tz=timezone.utc).isoformat()
            url = item.get("url", "")
            raw_content = item.get("text") or item.get("markdown") or ""
            raw_title   = (
                item.get("title")
                or item.get("og:title")
                or item.get("metadata", {}).get("title", "")
            )
            signals.append(Signal(
                id=_make_id(url, ts),
                title=_clean_title(raw_title, raw_content),
                content=raw_content[:6000],
                source="web",
                url=url,
                timestamp=ts,
                category=None,
                client_tag=client_tag,
                raw_meta={"domain": item.get("domain")},
            ))

        print(f"[Web] ✓ {len(signals)} signals")
        return signals

    # ── Reddit ────────────────────────────────────────────────────────────────

    def scrape_reddit(
        self,
        subreddits: list[str],
        search_terms: list[str],
        max_items: int = 30,
        client_tag: Optional[str] = None,
    ) -> list[Signal]:
        """Actor: trudax/reddit-scraper (verified, high success rate)"""
        print(f"[Reddit] Scraping {subreddits}...")

        run_input = {
            "searches": [
                {"query": term, "subreddit": sub}
                for sub in subreddits
                for term in search_terms
            ],
            "maxItems": max_items,
            "type": "posts",
            "sort": "hot",
        }

        run = self.client.actor("trudax/reddit-scraper").call(run_input=run_input)
        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        signals = []
        for item in items:
            ts = datetime.fromtimestamp(
                item.get("created_utc", datetime.now().timestamp()), tz=timezone.utc
            ).isoformat()
            body    = item.get("selftext") or item.get("body") or ""
            content = f"{item.get('title', '')}\n\n{body}".strip()
            url     = item.get("url", "")

            signals.append(Signal(
                id=_make_id(url, ts),
                title=_clean_title(item.get("title", ""), content),
                content=content[:4000],
                source="reddit",
                url=url,
                timestamp=ts,
                category=None,
                client_tag=client_tag,
                raw_meta={
                    "subreddit":    item.get("subreddit"),
                    "score":        item.get("score"),
                    "num_comments": item.get("num_comments"),
                    "author":       item.get("author"),
                },
            ))

        print(f"[Reddit] ✓ {len(signals)} signals")
        return signals

    # ── Twitter / X ───────────────────────────────────────────────────────────

    def scrape_twitter(
        self,
        search_terms: list[str],
        max_items: int = 20,
        client_tag: Optional[str] = None,
    ) -> list[Signal]:
        """Actor: apidojo/tweet-scraper (most popular Twitter actor on Apify)"""
        print(f"[Twitter/X] Scraping: {search_terms}")

        run_input = {
            "searchTerms": search_terms,
            "maxItems":    max_items,
            "queryType":   "Top",
        }

        run = self.client.actor("apidojo/tweet-scraper").call(run_input=run_input)
        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        signals = []
        for item in items:
            ts   = item.get("createdAt") or datetime.now(tz=timezone.utc).isoformat()
            url  = item.get("url") or f"https://twitter.com/i/web/status/{item.get('id','')}"
            text = item.get("text") or item.get("full_text") or ""

            signals.append(Signal(
                id=_make_id(url, ts),
                title=_clean_title("", text),
                content=text[:4000],
                source="twitter",
                url=url,
                timestamp=ts,
                category=None,
                client_tag=client_tag,
                raw_meta={
                    "author":   item.get("author", {}).get("userName") or item.get("user", {}).get("screen_name"),
                    "likes":    item.get("likeCount") or item.get("favorite_count"),
                    "retweets": item.get("retweetCount") or item.get("retweet_count"),
                    "lang":     item.get("lang"),
                },
            ))

        print(f"[Twitter/X] ✓ {len(signals)} signals")
        return signals

    # ── TikTok ────────────────────────────────────────────────────────────────

    def scrape_tiktok(
        self,
        hashtags: list[str],
        max_items: int = 20,
        client_tag: Optional[str] = None,
    ) -> list[Signal]:
        """Actor: clockworks/tiktok-scraper (undisputed leader for TikTok on Apify)"""
        print(f"[TikTok] Scraping hashtags: {hashtags}")

        signals = []
        for tag in hashtags:
            run_input = {
                "hashtags":       [tag.lstrip("#")],
                "resultsPerPage": max_items,
            }
            run   = self.client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            for item in items:
                ts  = item.get("createTimeISO") or datetime.now(tz=timezone.utc).isoformat()
                url = item.get("webVideoUrl") or item.get("videoUrl") or ""
                text = item.get("text") or item.get("desc") or ""

                signals.append(Signal(
                    id=_make_id(url, ts),
                    title=_clean_title("", text),
                    content=text[:2000],
                    source="tiktok",
                    url=url,
                    timestamp=ts,
                    category=None,
                    client_tag=client_tag,
                    raw_meta={
                        "author": item.get("authorMeta", {}).get("name") or item.get("author"),
                        "plays":  item.get("playCount"),
                        "likes":  item.get("diggCount"),
                        "shares": item.get("shareCount"),
                        "hashtag": tag,
                    },
                ))

        print(f"[TikTok] ✓ {len(signals)} signals")
        return signals

    # ── YouTube ───────────────────────────────────────────────────────────────

    def scrape_youtube(
        self,
        search_terms: list[str],
        max_items: int = 15,
        client_tag: Optional[str] = None,
    ) -> list[Signal]:
        """Actor: apify/youtube-scraper (official Apify actor)"""
        print(f"[YouTube] Scraping: {search_terms}")

        run_input = {
            "searchKeywords": search_terms,
            "maxResults":     max_items,
            "maxComments":    5,
        }

        run   = self.client.actor("apify/youtube-scraper").call(run_input=run_input)
        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        signals = []
        for item in items:
            ts  = item.get("date") or datetime.now(tz=timezone.utc).isoformat()
            url = item.get("url") or item.get("videoUrl") or ""

            description   = item.get("description") or item.get("text") or ""
            comments      = item.get("comments") or []
            comments_text = "\n".join(c.get("text", "") for c in comments[:5] if c.get("text"))
            content       = f"{description}\n\n--- Top comments ---\n{comments_text}".strip()
            raw_title     = item.get("title") or item.get("name") or ""

            signals.append(Signal(
                id=_make_id(url, ts),
                title=_clean_title(raw_title, content),
                content=content[:5000],
                source="youtube",
                url=url,
                timestamp=ts,
                category=None,
                client_tag=client_tag,
                raw_meta={
                    "channel":  item.get("channelName"),
                    "views":    item.get("viewCount"),
                    "likes":    item.get("likes"),
                    "duration": item.get("duration"),
                },
            ))

        print(f"[YouTube] ✓ {len(signals)} signals")
        return signals

    # ── Instagram ─────────────────────────────────────────────────────────────

    def scrape_instagram(
        self,
        hashtags: list[str],
        max_items: int = 20,
        client_tag: Optional[str] = None,
    ) -> list[Signal]:
        """Actor: apify/instagram-scraper (official Apify actor, most trusted)"""
        print(f"[Instagram] Scraping hashtags: {hashtags}")

        signals = []
        for tag in hashtags:
            run_input = {
                "directUrls":   [f"https://www.instagram.com/explore/tags/{tag.lstrip('#')}/"],
                "resultsType":  "posts",
                "resultsLimit": max_items,
            }
            run   = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            for item in items:
                ts      = item.get("timestamp") or datetime.now(tz=timezone.utc).isoformat()
                url     = item.get("url") or item.get("shortCode") or ""
                caption = item.get("caption") or item.get("text") or ""

                signals.append(Signal(
                    id=_make_id(url, ts),
                    title=_clean_title("", caption),
                    content=caption[:3000],
                    source="instagram",
                    url=url,
                    timestamp=ts,
                    category=None,
                    client_tag=client_tag,
                    raw_meta={
                        "author":   item.get("ownerUsername"),
                        "likes":    item.get("likesCount"),
                        "comments": item.get("commentsCount"),
                        "hashtag":  tag,
                        "type":     item.get("type"),
                    },
                ))

        print(f"[Instagram] ✓ {len(signals)} signals")
        return signals


# ── Orchestrator ──────────────────────────────────────────────────────────────

class IngestionOrchestrator:

    def __init__(self, output_path: str = "data/signals.jsonl"):
        self.client      = ApifyIngestionClient()
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def _load_existing_ids(self) -> set[str]:
        ids = set()
        if os.path.exists(self.output_path):
            with open(self.output_path) as f:
                for line in f:
                    try:
                        ids.add(json.loads(line)["id"])
                    except Exception:
                        pass
        return ids

    def _save_signals(self, signals: list[Signal]) -> int:
        existing    = self._load_existing_ids()
        new_signals = [s for s in signals if s.id not in existing]

        with open(self.output_path, "a") as f:
            for sig in new_signals:
                f.write(json.dumps(asdict(sig), ensure_ascii=False) + "\n")

        print(f"[Save] {len(new_signals)} new / {len(signals) - len(new_signals)} dupes skipped")
        return len(new_signals)

    def run(
        self,
        web_config:       Optional[dict] = None,
        reddit_config:    Optional[dict] = None,
        twitter_config:   Optional[dict] = None,
        tiktok_config:    Optional[dict] = None,
        youtube_config:   Optional[dict] = None,
        instagram_config: Optional[dict] = None,
        client_tag:       Optional[str]  = None,
    ) -> list[Signal]:

        all_signals: list[Signal] = []

        if web_config:
            all_signals += self.client.scrape_web(**web_config, client_tag=client_tag)
        if reddit_config:
            all_signals += self.client.scrape_reddit(**reddit_config, client_tag=client_tag)
        if twitter_config:
            all_signals += self.client.scrape_twitter(**twitter_config, client_tag=client_tag)
        if tiktok_config:
            all_signals += self.client.scrape_tiktok(**tiktok_config, client_tag=client_tag)
        if youtube_config:
            all_signals += self.client.scrape_youtube(**youtube_config, client_tag=client_tag)
        if instagram_config:
            all_signals += self.client.scrape_instagram(**instagram_config, client_tag=client_tag)

        total = self._save_signals(all_signals)
        print(f"\n✅ Done — {total} new signals saved to {self.output_path}")
        return all_signals


# ── CLI ───────────────────────────────────────────────────────────────────────
# Edite os termos de busca, hashtags e subreddits para o seu projeto.
# Valores baixos de max_items para economizar créditos do Apify.

if __name__ == "__main__":
    orchestrator = IngestionOrchestrator(output_path="data/signals.jsonl")

    orchestrator.run(

        # WEB — referências de cultura e publicidade
        web_config={
            "start_urls": [
                "https://www.trendwatching.com",
                "https://www.contagious.com/news-and-views",
                "https://www.campaignlive.com",
                "https://www.dandad.org/en/d-ad-news-opinion/",
                "https://www.dazeddigital.com",
                "https://www.thefader.com",
                "https://hbr.org/topic/subject/marketing",
                "https://www.warc.com/newsandopinion",
            ],
            "max_pages_per_url": 2,
        },

        # REDDIT
        reddit_config={
            "subreddits": [
                "advertising", "marketing", "socialmedia",
                "GenZ", "branding", "digitalmarketing",
            ],
            "search_terms": [
                "brand culture", "creator economy",
                "brand authenticity", "cultural marketing",
            ],
            "max_items": 20,
        },

        # TWITTER / X
        twitter_config={
            "search_terms": [
                "#brandpurpose", "#culturalmarketing",
                "#creatoreconomy", "brand strategy 2025",
            ],
            "max_items": 15,
        },

        # TIKTOK
        tiktok_config={
            "hashtags": [
                "#brandtok", "#marketingtok",
                "#adtok", "#culturaltok",
            ],
            "max_items": 15,
        },

        # YOUTUBE
        youtube_config={
            "search_terms": [
                "brand strategy 2025",
                "Gen Z consumer behavior",
                "cultural marketing trends",
            ],
            "max_items": 10,
        },

        # INSTAGRAM
        instagram_config={
            "hashtags": [
                "#brandstrategy", "#culturalmarketing",
                "#creativeagency",
            ],
            "max_items": 15,
        },

        client_tag="Atlantic_General",
    )
