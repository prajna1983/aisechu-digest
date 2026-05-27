"""
generate_index.py
-----------------
Generates reports/index.html — a browsable archive page listing all retained
daily digests with their stats and a quick-open link.
"""

import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

SGT = ZoneInfo("Asia/Singapore")
from typing import List, Dict, Any


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AISecHub Digest Archive</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: #0f1117;
      --surface: #1a1d27;
      --surface2: #22263a;
      --border: #2e3250;
      --accent: #6c63ff;
      --accent2: #00d4aa;
      --text: #e8eaf6;
      --muted: #8892b0;
      --link: #79c0ff;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }}

    /* ── Header ── */
    .header {{
      background: linear-gradient(135deg, #1a1d27 0%, #0f1117 60%, #0d1b2e 100%);
      border-bottom: 1px solid var(--border);
      padding: 32px 24px 24px;
      text-align: center;
    }}
    .channel-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(108,99,255,0.15);
      border: 1px solid rgba(108,99,255,0.4);
      border-radius: 24px;
      padding: 6px 16px;
      font-size: 13px;
      color: var(--accent);
      margin-bottom: 16px;
      text-decoration: none;
    }}
    h1 {{
      font-size: 2rem;
      font-weight: 700;
      background: linear-gradient(90deg, #e8eaf6 30%, #6c63ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 8px;
    }}
    .subtitle {{ color: var(--muted); font-size: 14px; }}

    /* ── Summary stats ── */
    .stats-bar {{
      max-width: 900px;
      margin: 24px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 16px;
    }}
    .stat-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      text-align: center;
    }}
    .stat-value {{ font-size: 2rem; font-weight: 700; color: var(--accent2); display: block; }}
    .stat-label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }}

    /* ── Trend chart ── */
    .main {{ max-width: 900px; margin: 0 auto; padding: 0 24px 60px; }}
    .section-title {{
      font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;
      color: var(--muted); margin: 36px 0 16px;
      display: flex; align-items: center; gap: 8px;
    }}
    .section-title::after {{ content: ""; flex: 1; height: 1px; background: var(--border); }}
    .chart-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
    }}
    .chart-card h3 {{
      font-size: 13px; font-weight: 600; color: var(--muted);
      margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .chart-wrap {{ position: relative; height: 200px; }}

    /* ── Digest cards grid ── */
    .digests-grid {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .digest-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px 24px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: start;
      transition: border-color 0.2s, transform 0.15s;
      text-decoration: none;
      color: inherit;
    }}
    .digest-card:hover {{
      border-color: var(--accent);
      transform: translateY(-1px);
    }}
    .digest-card.today {{ border-color: var(--accent2); }}
    .digest-date {{
      font-size: 16px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .today-badge {{
      background: rgba(0,212,170,0.2);
      color: var(--accent2);
      border: 1px solid rgba(0,212,170,0.4);
      border-radius: 12px;
      padding: 2px 10px;
      font-size: 11px;
      font-weight: 600;
    }}
    .digest-insights {{
      font-size: 13px;
      color: var(--muted);
      line-height: 1.5;
      margin-top: 6px;
    }}
    .digest-insight-item {{ margin-top: 4px; }}
    .digest-insight-item::before {{ content: "→ "; color: var(--accent); }}
    .digest-mini-stats {{
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .mini-stat {{
      text-align: center;
      min-width: 60px;
    }}
    .mini-stat-value {{
      font-size: 20px;
      font-weight: 700;
      color: var(--accent2);
      display: block;
    }}
    .mini-stat-label {{
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}
    .digest-cats {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }}
    .cat-tag {{
      background: rgba(108,99,255,0.12);
      color: var(--accent);
      border-radius: 6px;
      padding: 3px 10px;
      font-size: 11px;
    }}
    .open-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--accent);
      color: white;
      border-radius: 10px;
      padding: 8px 18px;
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      white-space: nowrap;
      align-self: center;
    }}
    .open-btn:hover {{ background: #5a52e0; }}

    /* ── Empty state ── */
    .empty {{
      text-align: center;
      color: var(--muted);
      padding: 60px 0;
      font-size: 15px;
    }}

    footer {{
      text-align: center;
      color: var(--muted);
      font-size: 12px;
      padding: 24px;
      border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>

<header class="header">
  <a class="channel-badge" href="https://t.me/AISecHub" target="_blank">✈️ t.me/AISecHub</a>
  <h1>AISecHub Digest Archive</h1>
  <p class="subtitle">Rolling 3-month archive &nbsp;·&nbsp; Updated daily &nbsp;·&nbsp; Powered by Claude</p>
</header>

<div class="stats-bar">
  <div class="stat-card">
    <span class="stat-value">{total_digests}</span>
    <span class="stat-label">Digests Archived</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{total_messages_all}</span>
    <span class="stat-label">Messages Processed</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{total_links_all}</span>
    <span class="stat-label">Links Catalogued</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{archive_span}</span>
    <span class="stat-label">Days of History</span>
  </div>
</div>

<main class="main">

  {trend_section}

  <div class="section-title">📅 All Digests</div>
  <div class="digests-grid">
    {cards_html}
  </div>

</main>

<footer>
  Archive updated {generated_at} SGT &nbsp;·&nbsp; Digests older than 90 days are automatically removed
</footer>

<script>
{chart_script}
</script>
</body>
</html>
"""


def _make_card(entry: Dict, is_today: bool) -> str:
    s = entry.get("summary", {})
    insights = s.get("top_insights", [])
    cats = s.get("top_categories", [])

    insights_html = "".join(
        f'<div class="digest-insight-item">{i}</div>'
        for i in insights[:2]
    ) if insights else '<div style="color:var(--muted);font-size:13px">No insights preview available</div>'

    cats_html = "".join(f'<span class="cat-tag">{c}</span>' for c in cats)

    today_badge = '<span class="today-badge">Today</span>' if is_today else ""
    today_class = " today" if is_today else ""

    return f"""
    <a class="digest-card{today_class}" href="{entry['html_file']}">
      <div>
        <div class="digest-date">
          {entry['display_date']}
          {today_badge}
        </div>
        <div class="digest-cats">{cats_html}</div>
        <div class="digest-insights">{insights_html}</div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:12px">
        <div class="digest-mini-stats">
          <div class="mini-stat">
            <span class="mini-stat-value">{s.get('total_messages', '—')}</span>
            <span class="mini-stat-label">Msgs</span>
          </div>
          <div class="mini-stat">
            <span class="mini-stat-value">{s.get('total_links', '—')}</span>
            <span class="mini-stat-label">Links</span>
          </div>
        </div>
        <span class="open-btn">Open ↗</span>
      </div>
    </a>"""


def generate_index(digests: List[Dict], reports_dir: Path) -> None:
    """Generate reports/index.html from the list of retained digests."""
    now = datetime.now(SGT)
    today_str = now.strftime("%Y-%m-%d")
    generated_at = now.strftime("%Y-%m-%d %H:%M")

    total_messages_all = sum(d.get("summary", {}).get("total_messages", 0) for d in digests)
    total_links_all = sum(d.get("summary", {}).get("total_links", 0) for d in digests)

    if digests:
        oldest = min(d["date"] for d in digests)
        archive_span = (now - oldest).days + 1
    else:
        archive_span = 0

    # Cards
    if digests:
        cards_html = "\n".join(
            _make_card(d, is_today=(d["date_str"] == today_str))
            for d in digests
        )
    else:
        cards_html = '<div class="empty">No digests yet. Run <code>python3 run_digest.py</code> to create your first one.</div>'

    # Trend chart: messages per day (last 30 entries max)
    trend_digests = list(reversed(digests[:30]))  # oldest-first for chart
    chart_script = ""
    trend_section = ""

    if len(trend_digests) > 1:
        labels = [d["date_str"][5:] for d in trend_digests]  # MM-DD
        msg_data = [d.get("summary", {}).get("total_messages", 0) for d in trend_digests]
        link_data = [d.get("summary", {}).get("total_links", 0) for d in trend_digests]

        chart_data_json = {
            "labels": labels,
            "messages": msg_data,
            "links": link_data,
        }

        import json as _json
        chart_script = f"""
const trendData = {_json.dumps(chart_data_json)};
new Chart(document.getElementById("trendChart"), {{
  type: "line",
  data: {{
    labels: trendData.labels,
    datasets: [
      {{
        label: "Messages",
        data: trendData.messages,
        borderColor: "#6c63ff",
        backgroundColor: "rgba(108,99,255,0.1)",
        tension: 0.3,
        fill: true,
        pointRadius: 4,
      }},
      {{
        label: "Links",
        data: trendData.links,
        borderColor: "#00d4aa",
        backgroundColor: "rgba(0,212,170,0.08)",
        tension: 0.3,
        fill: true,
        pointRadius: 4,
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ labels: {{ color: "#8892b0", font: {{ size: 12 }} }} }}
    }},
    scales: {{
      x: {{ ticks: {{ color: "#8892b0", font: {{ size: 10 }}, maxTicksLimit: 15 }}, grid: {{ color: "#2e3250" }} }},
      y: {{ ticks: {{ color: "#8892b0", font: {{ size: 10 }} }}, grid: {{ color: "#2e3250" }} }}
    }}
  }}
}});"""

        trend_section = f"""
  <div class="section-title">📈 Activity Trend (last {len(trend_digests)} days)</div>
  <div class="chart-card">
    <h3>Messages &amp; Links per Day</h3>
    <div class="chart-wrap"><canvas id="trendChart"></canvas></div>
  </div>"""

    html = INDEX_TEMPLATE.format(
        total_digests=len(digests),
        total_messages_all=total_messages_all,
        total_links_all=total_links_all,
        archive_span=archive_span,
        trend_section=trend_section,
        cards_html=cards_html,
        generated_at=generated_at,
        chart_script=chart_script,
    )

    index_path = reports_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[index] Archive index saved: {index_path}")
