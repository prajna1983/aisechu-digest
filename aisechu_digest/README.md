# AISecHub Daily Digest

A one-command tool that turns the high-volume **AISecHub** Telegram channel into a clean, categorized, AI-powered daily digest — complete with charts, summaries, and embedded hyperlinks.

---

## What it does

Every time you run it, the tool:

1. **Fetches** the last 24 hours of messages from `t.me/s/AISecHub` (no login required — it uses the public web preview)
2. **Analyzes** them with Claude (Anthropic API) to categorize topics, write summaries, and extract key insights
3. **Generates** a beautiful self-contained HTML report and opens it in your browser

---

## Setup (one-time, ~3 minutes)

### 1 · Python

You need Python 3.10 or later. Check with:

```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/).

### 2 · Anthropic API key

The tool uses Claude to analyze and summarize the messages.

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in (or create a free account)
3. Navigate to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)

Set it as an environment variable:

```bash
# macOS / Linux — add this to your ~/.zshrc or ~/.bash_profile to make it permanent
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Then reload your terminal (or run `source ~/.zshrc`).

### 3 · Install Python packages

The script installs them automatically on first run, but you can also do it manually:

```bash
pip3 install requests beautifulsoup4 anthropic
```

---

## Running the digest

```bash
cd path/to/aisechu_digest
python3 run_digest.py
```

The HTML report opens in your browser automatically and is also saved to `./reports/aisechu_digest_YYYY-MM-DD.html`.

---

## Options (environment variables)

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `DIGEST_HOURS` | `24` | How many hours back to fetch |
| `DIGEST_OUTPUT_DIR` | `./reports` | Where to save HTML reports |

Example — fetch the last 48 hours and save to your Desktop:

```bash
DIGEST_HOURS=48 DIGEST_OUTPUT_DIR=~/Desktop python3 run_digest.py
```

---

## Running it automatically every morning

To get a fresh digest every day at 7:00 AM, add a cron job:

```bash
# Open your crontab
crontab -e

# Add this line (adjust paths to match your setup)
0 7 * * * cd /path/to/aisechu_digest && ANTHROPIC_API_KEY=sk-ant-... python3 run_digest.py >> ~/aisechu_digest.log 2>&1
```

---

## Report structure

The generated HTML report includes:

- **Stats bar** — total messages, categories, links shared, key insights
- **Charts** — category distribution (donut) + posting activity by hour (bar)
- **Top Insights** — macro trends Claude identified across all posts
- **Category cards** — each with a narrative summary and individual item cards with embedded links
- **Most-Referenced Domains** — shows which sources the channel links to most

---

## Troubleshooting

**"No messages found"**
The channel might be temporarily quiet, or Telegram may have changed their web page structure. Try `DIGEST_HOURS=48 python3 run_digest.py` to look further back.

**"ANTHROPIC_API_KEY not set"**
Make sure you ran `export ANTHROPIC_API_KEY=...` in the same terminal session, or that it's in your `~/.zshrc`.

**Rate limits or API errors**
Claude API has generous free-tier limits. If you hit them, wait a minute and retry.

---

## Files

```
aisechu_digest/
├── run_digest.py          ← Main entry point — run this
├── fetch_messages.py      ← Scrapes t.me/s/AISecHub
├── analyze_messages.py    ← Claude-powered categorization & summarization
├── generate_report.py     ← HTML report builder
├── README.md              ← This file
└── reports/               ← Generated HTML digests (created on first run)
```
