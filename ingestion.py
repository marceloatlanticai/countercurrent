"""
Countercurrent.ai — Ingestion: Multi-Source Hub (WNBA x NY Liberty)
Includes: Reddit, YouTube, TikTok, RSS, BlueSky and Discord Logs.
"""

import os
import json
import hashlib
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, asdict

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

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
    if raw and raw.strip() and raw.strip().lower() not in ["none", "null", "(no title)"]:
        return raw.strip()[:max_len]
    return fallback_content.splitlines()[0][:max_len] if fallback_content else "(no title)"

# ── 1. RSS & BlueSky (BlueSky uses RSS for public profiles) ──────────────────

def scrape_rss(feeds, max_items_per_feed=5, client_tag=None):
    print(f"[RSS/BlueSky] Lendo {len(feeds)} feeds...")
    signals = []
    import re
    for feed_url, feed_name in feeds:
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "Countercurrent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            
            for item in root.findall(".//item")[:max_items_per_feed]:
                title = (item.findtext("title") or "").strip()
                url = item.findtext("link") or ""
                desc = item.findtext("description") or ""
                content = re.sub(r"<[^>]+>", "", desc).strip()[:4000]
                ts = item.findtext("pubDate") or datetime.now(tz=timezone.utc).isoformat()
                
                signals.append(Signal(
                    id=_make_id(url, ts), title=_clean_title(title, content),
                    content=content, source="rss", url=url, timestamp=ts,
                    category=None, client_tag=client_tag,
                    raw_meta={"feed_name": feed_name}
                ))
        except Exception as e:
            print(f"[RSS] Erro em '{feed_name}': {e}")
    return signals

# ── 2. Discord Log Processor (Simulated via File) ────────────────────────────

def process_discord_logs(file_path, client_tag=None):
    """Processes a .txt log from a Discord channel."""
    if not os.path.exists(file_path):
        return []
    print(f"[Discord] Lendo logs de {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ts = datetime.now(tz=timezone.utc).isoformat()
    return [Signal(
        id=_make_id(file_path, ts),
        title=f"Discord Conversation: {os.path.basename(file_path)}",
        content=content[:5000],
        source="discord",
        url="local://discord-log",
        timestamp=ts,
        category="community_insight",
        client_tag=client_tag,
        raw_meta={"file": file_path}
    )]

# ── 3. Orchestrator ──────────────────────────────────────────────────────────

class IngestionOrchestrator:
    def __init__(self, output_path="data/signals.jsonl"):
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def _save(self, signals):
        with open(self.output_path, "a") as f:
            for sig in signals:
                f.write(json.dumps(asdict(sig), ensure_ascii=False) + "\n")
        print(f"✅ {len(signals)} signals salvos.")

    def run_ny_liberty_mission(self):
        all_signals = []
        
        # BlueSky & RSS Feeds
        all_signals += scrape_rss([
            ("https://bsky.app/profile/wnba.bsky.social/rss", "BlueSky: WNBA Official"),
            ("https://bsky.app/profile/nyliberty.bsky.social/rss", "BlueSky: NY Liberty"),
            ("https://www.espn.com/espn/rss/wnba/news", "ESPN WNBA"),
            ("https://hypebae.com/feed", "Hypebae Culture")
        ], client_tag="NY_Liberty_Pinterest")

        # Discord (If you have a log file in data/discord_liberty.txt)
        all_signals += process_discord_logs("data/discord_liberty.txt", client_tag="NY_Liberty_Pinterest")

        # (Aqui você pode manter as chamadas de Reddit, TikTok e YouTube do seu arquivo anterior)
        # ...
        
        self._save(all_signals)

if __name__ == "__main__":
    IngestionOrchestrator().run_ny_liberty_mission()
