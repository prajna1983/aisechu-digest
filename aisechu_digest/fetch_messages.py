"""
fetch_messages.py
-----------------
Fetches messages from the public Telegram channel web preview at t.me/s/AISecHub.
Filters to the last 24 hours and returns structured message objects.
"""

import re
import time
import requests
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Optional

CHANNEL = "AISecHub"
BASE_URL = f"https://t.me/s/{CHANNEL}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class TelegramMessage:
    message_id: int
    timestamp: datetime
    text: str
    links: List[str] = field(default_factory=list)
    preview_title: Optional[str] = None
    preview_description: Optional[str] = None
    preview_url: Optional[str] = None


def _parse_page(html: str) -> List[TelegramMessage]:
    """Parse a Telegram channel HTML page and return message objects."""
    soup = BeautifulSoup(html, "html.parser")
    messages = []

    for wrap in soup.select(".tgme_widget_message_wrap"):
        msg_div = wrap.select_one(".tgme_widget_message")
        if not msg_div:
            continue

        # Message ID from data-post attribute e.g. "AISecHub/1234"
        data_post = msg_div.get("data-post", "")
        try:
            message_id = int(data_post.split("/")[-1])
        except (ValueError, IndexError):
            continue

        # Timestamp
        time_tag = wrap.select_one("time[datetime]")
        if not time_tag:
            continue
        try:
            ts = datetime.fromisoformat(time_tag["datetime"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, KeyError):
            continue

        # Message text (preserve newlines)
        text_div = wrap.select_one(".tgme_widget_message_text")
        if text_div:
            # Replace <br> with newline
            for br in text_div.find_all("br"):
                br.replace_with("\n")
            raw_text = text_div.get_text(separator=" ").strip()
        else:
            raw_text = ""

        # Extract all hyperlinks from the message text area
        links = []
        if text_div:
            for a_tag in text_div.find_all("a", href=True):
                href = a_tag["href"]
                if href.startswith("http"):
                    links.append(href)

        # Link preview (often used when sharing articles)
        preview_title = None
        preview_description = None
        preview_url = None

        preview_div = wrap.select_one(".tgme_widget_message_link_preview")
        if preview_div:
            pt = preview_div.select_one(".link_preview_title")
            pd = preview_div.select_one(".link_preview_description")
            pa = preview_div.select_one("a[href]")
            preview_title = pt.get_text(strip=True) if pt else None
            preview_description = pd.get_text(strip=True) if pd else None
            if pa:
                preview_url = pa["href"]
                if preview_url not in links and preview_url.startswith("http"):
                    links.append(preview_url)

        messages.append(TelegramMessage(
            message_id=message_id,
            timestamp=ts,
            text=raw_text,
            links=links,
            preview_title=preview_title,
            preview_description=preview_description,
            preview_url=preview_url,
        ))

    return messages


def fetch_last_24h(hours: int = 24, max_pages: int = 10) -> List[TelegramMessage]:
    """
    Fetch messages from the last `hours` hours by paginating backwards.
    Returns messages sorted oldest-first.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_messages: List[TelegramMessage] = []
    url = BASE_URL
    visited_ids = set()

    print(f"[fetch] Fetching messages from the last {hours}h (cutoff: {cutoff.strftime('%Y-%m-%d %H:%M UTC')})")

    for page_num in range(max_pages):
        print(f"[fetch] Page {page_num + 1}: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[fetch] Request error: {e}")
            break

        page_messages = _parse_page(resp.text)
        if not page_messages:
            print("[fetch] No messages parsed on this page — stopping.")
            break

        # Deduplicate
        new_messages = [m for m in page_messages if m.message_id not in visited_ids]
        for m in new_messages:
            visited_ids.add(m.message_id)

        # Keep only messages within our time window
        recent = [m for m in new_messages if m.timestamp >= cutoff]
        all_messages.extend(recent)

        # Find the oldest message on this page
        oldest_on_page = min(page_messages, key=lambda m: m.timestamp)

        if oldest_on_page.timestamp < cutoff:
            # We've gone far enough back — no need to fetch more
            print(f"[fetch] Reached messages older than cutoff — done.")
            break

        # Paginate: use the smallest message ID seen for ?before=
        min_id = min(m.message_id for m in page_messages)
        url = f"{BASE_URL}?before={min_id}"
        time.sleep(0.5)  # be polite

    # Sort oldest-first and deduplicate again
    seen = set()
    unique = []
    for m in sorted(all_messages, key=lambda m: m.timestamp):
        if m.message_id not in seen:
            seen.add(m.message_id)
            unique.append(m)

    print(f"[fetch] Total messages in window: {len(unique)}")
    return unique


if __name__ == "__main__":
    msgs = fetch_last_24h(hours=24)
    for m in msgs:
        print(f"[{m.timestamp.strftime('%H:%M')}] {m.text[:80]}...")
