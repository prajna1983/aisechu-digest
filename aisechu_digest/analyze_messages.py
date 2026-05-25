"""
analyze_messages.py
-------------------
Uses the Anthropic Claude API to:
  1. Categorize messages into meaningful groups
  2. Summarize each category with key insights
  3. Extract notable links and their context
"""

import json
import os
from typing import List, Dict, Any
import anthropic

from fetch_messages import TelegramMessage

# Predefined categories for AISecHub (AI + Security focused channel).
# Claude may also create/rename these dynamically — these are hints.
CATEGORY_HINTS = [
    "AI Research & Papers",
    "Cybersecurity Vulnerabilities & CVEs",
    "AI Safety & Alignment",
    "Security Tools & Releases",
    "Threat Intelligence",
    "AI & ML Security",
    "Industry News & Policy",
    "Tutorials & Learning Resources",
    "Miscellaneous",
]


def _build_message_block(messages: List[TelegramMessage]) -> str:
    """Serialize messages into a compact text block for the prompt."""
    lines = []
    for m in messages:
        links_str = ", ".join(m.links) if m.links else "none"
        preview = ""
        if m.preview_title:
            preview = f" [Preview: {m.preview_title}]"
        lines.append(
            f"MSG#{m.message_id} [{m.timestamp.strftime('%Y-%m-%d %H:%M UTC')}]\n"
            f"TEXT: {m.text[:600]}{preview}\n"
            f"LINKS: {links_str}"
        )
    return "\n\n---\n\n".join(lines)


def analyze(messages: List[TelegramMessage], api_key: str | None = None) -> Dict[str, Any]:
    """
    Send messages to Claude for analysis.
    Returns a structured dict with categories, summaries, and insights.
    """
    if not messages:
        return {"categories": [], "total_messages": 0, "insights": {}}

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "No Anthropic API key found. Set ANTHROPIC_API_KEY environment variable "
            "or pass api_key= to analyze()."
        )

    client = anthropic.Anthropic(api_key=key)
    msg_block = _build_message_block(messages)

    system_prompt = """You are an expert analyst for an AI and cybersecurity intelligence channel.
Your job is to process a batch of raw Telegram messages from the AISecHub channel and produce a structured daily digest.

Return ONLY valid JSON — no markdown, no explanation, just the JSON object.

The JSON must match this exact schema:
{
  "categories": [
    {
      "name": "<category name>",
      "emoji": "<single relevant emoji>",
      "summary": "<2-4 sentence narrative summary of the main themes in this category>",
      "key_items": [
        {
          "title": "<short 1-line title>",
          "detail": "<1-2 sentence explanation>",
          "url": "<URL if available, else null>",
          "tags": ["<tag1>", "<tag2>"]
        }
      ],
      "message_count": <int>
    }
  ],
  "top_insights": [
    "<1-2 sentence high-level insight or trend observed across all messages>"
  ],
  "stats": {
    "total_links": <int>,
    "most_linked_domains": ["<domain1>", "<domain2>", "<domain3>"],
    "activity_by_hour": {
      "00": <count>, "01": <count>, ..., "23": <count>
    }
  }
}

Guidelines:
- Create 4–8 meaningful categories based on actual content (use the channel's AI + security focus)
- Each category should have at least 1 key_item
- Summaries should be insightful and written for a security/AI professional
- Include real URLs from the messages in key_items whenever available
- top_insights should highlight 3–5 macro trends or notable observations
- activity_by_hour: count messages per UTC hour (use 0 for hours with no messages)
- most_linked_domains: extract the domain (e.g. "arxiv.org") from links"""

    user_prompt = f"""Here are {len(messages)} messages from the AISecHub Telegram channel posted in the last 24 hours.
Analyze them and return the structured JSON digest.

MESSAGES:
{msg_block}

Hint — common categories for this channel: {', '.join(CATEGORY_HINTS)}
"""

    print(f"[analyze] Sending {len(messages)} messages to Claude for analysis...")
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[analyze] JSON parse error: {e}\nRaw response:\n{raw[:500]}")
        raise

    result["total_messages"] = len(messages)
    print(f"[analyze] Done — {len(result.get('categories', []))} categories identified.")
    return result


# Add missing import used inside analyze()
import re
