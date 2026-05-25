"""
generate_report.py
------------------
Generates a self-contained, beautiful HTML digest report from the analysis data.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AISecHub Daily Digest — {date}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: #0f1117;
      --surface: #1a1d27;
      --surface2: #22263a;
      --border: #2e3250;
      --accent: #6c63ff;
      --accent2: #00d4aa;
      --accent3: #ff6584;
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
      line-height: 1.6;
    }}

    /* ── Header ── */
    .header {{
      background: linear-gradient(135deg, #1a1d27 0%, #0f1117 60%, #0d1b2e 100%);
      border-bottom: 1px solid var(--border);
      padding: 32px 0 24px;
      text-align: center;
    }}
    .header-inner {{
      max-width: 960px;
      margin: 0 auto;
      padding: 0 24px;
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
    .channel-badge:hover {{ background: rgba(108,99,255,0.25); }}
    h1 {{
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: -0.5px;
      background: linear-gradient(90deg, #e8eaf6 30%, #6c63ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 8px;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: 14px;
    }}

    /* ── Stats bar ── */
    .stats-bar {{
      max-width: 960px;
      margin: 24px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
    }}
    .stat-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      text-align: center;
    }}
    .stat-value {{
      font-size: 2rem;
      font-weight: 700;
      color: var(--accent2);
      display: block;
    }}
    .stat-label {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 4px;
    }}

    /* ── Main layout ── */
    .main {{
      max-width: 960px;
      margin: 0 auto;
      padding: 0 24px 60px;
    }}
    .section-title {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: var(--muted);
      margin: 40px 0 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .section-title::after {{
      content: "";
      flex: 1;
      height: 1px;
      background: var(--border);
    }}

    /* ── Charts row ── */
    .charts-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}
    @media (max-width: 680px) {{ .charts-row {{ grid-template-columns: 1fr; }} }}
    .chart-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
    }}
    .chart-card h3 {{
      font-size: 13px;
      font-weight: 600;
      color: var(--muted);
      margin-bottom: 16px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .chart-wrap {{ position: relative; height: 220px; }}

    /* ── Insights ── */
    .insights-list {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .insight-item {{
      background: var(--surface);
      border-left: 3px solid var(--accent);
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      font-size: 14px;
      color: var(--text);
      line-height: 1.6;
    }}

    /* ── Category cards ── */
    .categories-grid {{
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .cat-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      transition: border-color 0.2s;
    }}
    .cat-card:hover {{ border-color: var(--accent); }}
    .cat-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 18px 24px 14px;
      border-bottom: 1px solid var(--border);
    }}
    .cat-emoji {{
      font-size: 22px;
      width: 40px;
      height: 40px;
      background: var(--surface2);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .cat-name {{ font-size: 16px; font-weight: 600; }}
    .cat-count {{
      margin-left: auto;
      background: rgba(108,99,255,0.2);
      color: var(--accent);
      border-radius: 20px;
      padding: 3px 12px;
      font-size: 12px;
      font-weight: 600;
    }}
    .cat-summary {{
      padding: 14px 24px 10px;
      font-size: 14px;
      color: #b0bcd4;
      line-height: 1.65;
    }}
    .cat-items {{
      padding: 10px 24px 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .item-card {{
      background: var(--surface2);
      border-radius: 10px;
      padding: 14px 16px;
      border: 1px solid transparent;
      transition: border-color 0.2s;
    }}
    .item-card:hover {{ border-color: var(--border); }}
    .item-title {{
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 6px;
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }}
    .item-title a {{
      color: var(--link);
      text-decoration: none;
    }}
    .item-title a:hover {{ text-decoration: underline; }}
    .item-detail {{
      font-size: 13px;
      color: var(--muted);
      line-height: 1.55;
    }}
    .item-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }}
    .tag {{
      background: rgba(255,255,255,0.06);
      color: var(--muted);
      border-radius: 6px;
      padding: 2px 8px;
      font-size: 11px;
    }}

    /* ── Domains ── */
    .domain-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .domain-chip {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 6px 14px;
      font-size: 13px;
      color: var(--accent2);
    }}

    /* ── Footer ── */
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
  <div class="header-inner">
    <a class="channel-badge" href="https://t.me/AISecHub" target="_blank">
      ✈️ t.me/AISecHub
    </a>
    <h1>AISecHub Daily Digest</h1>
    <p class="subtitle">{date} &nbsp;·&nbsp; Last 24 hours &nbsp;·&nbsp; Powered by Claude</p>
  </div>
</header>

<div class="stats-bar">
  <div class="stat-card">
    <span class="stat-value">{total_messages}</span>
    <span class="stat-label">Messages</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{num_categories}</span>
    <span class="stat-label">Categories</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{total_links}</span>
    <span class="stat-label">Links Shared</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{num_insights}</span>
    <span class="stat-label">Key Insights</span>
  </div>
</div>

<main class="main">

  <div class="section-title">📊 Activity & Distribution</div>
  <div class="charts-row">
    <div class="chart-card">
      <h3>Messages by Category</h3>
      <div class="chart-wrap">
        <canvas id="categoryChart"></canvas>
      </div>
    </div>
    <div class="chart-card">
      <h3>Posting Activity (UTC hour)</h3>
      <div class="chart-wrap">
        <canvas id="activityChart"></canvas>
      </div>
    </div>
  </div>

  <div class="section-title">💡 Top Insights</div>
  <div class="insights-list">
    {insights_html}
  </div>

  <div class="section-title">📂 Categories</div>
  <div class="categories-grid">
    {categories_html}
  </div>

  {domains_section}

</main>

<footer>
  Generated {generated_at} UTC &nbsp;·&nbsp; Source: <a href="https://t.me/AISecHub" style="color:var(--link)">AISecHub</a> on Telegram
</footer>

<script>
const PALETTE = [
  "#6c63ff","#00d4aa","#ff6584","#ffd166","#06d6a0",
  "#118ab2","#ef476f","#ffc43d","#1b998b","#e9c46a"
];

// Category distribution chart
const catData = {cat_data_json};
new Chart(document.getElementById("categoryChart"), {{
  type: "doughnut",
  data: {{
    labels: catData.labels,
    datasets: [{{
      data: catData.values,
      backgroundColor: PALETTE.slice(0, catData.labels.length),
      borderWidth: 2,
      borderColor: "#1a1d27",
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{
        position: "right",
        labels: {{ color: "#8892b0", font: {{ size: 11 }}, boxWidth: 12, padding: 10 }}
      }}
    }}
  }}
}});

// Activity by hour chart
const actData = {activity_data_json};
new Chart(document.getElementById("activityChart"), {{
  type: "bar",
  data: {{
    labels: actData.hours,
    datasets: [{{
      label: "Messages",
      data: actData.counts,
      backgroundColor: "rgba(108,99,255,0.7)",
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: "#8892b0", font: {{ size: 10 }} }}, grid: {{ color: "#2e3250" }} }},
      y: {{ ticks: {{ color: "#8892b0", font: {{ size: 10 }}, stepSize: 1 }}, grid: {{ color: "#2e3250" }} }}
    }}
  }}
}});
</script>
</body>
</html>
"""


def _make_category_html(cat: Dict) -> str:
    items_html = ""
    for item in cat.get("key_items", []):
        url = item.get("url")
        title = item.get("title", "")
        if url:
            title_html = f'<a href="{url}" target="_blank" rel="noopener">{title} ↗</a>'
        else:
            title_html = title

        tags_html = "".join(
            f'<span class="tag">{t}</span>' for t in item.get("tags", [])
        )

        items_html += f"""
        <div class="item-card">
          <div class="item-title">{title_html}</div>
          <div class="item-detail">{item.get("detail", "")}</div>
          {"<div class='item-tags'>" + tags_html + "</div>" if tags_html else ""}
        </div>"""

    return f"""
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-emoji">{cat.get("emoji", "📌")}</div>
        <div class="cat-name">{cat.get("name", "")}</div>
        <div class="cat-count">{cat.get("message_count", 0)} msgs</div>
      </div>
      <div class="cat-summary">{cat.get("summary", "")}</div>
      <div class="cat-items">{items_html}</div>
    </div>"""


def generate_html(analysis: Dict[str, Any], output_path: str | None = None) -> str:
    """
    Build the HTML report from analysis data.
    Returns the HTML string and optionally writes it to output_path.
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %-d %Y")
    generated_at = now.strftime("%Y-%m-%d %H:%M")

    categories = analysis.get("categories", [])
    stats = analysis.get("stats", {})
    insights = analysis.get("top_insights", [])

    # Insights HTML
    insights_html = "\n".join(
        f'<div class="insight-item">🔹 {ins}</div>' for ins in insights
    )

    # Categories HTML
    categories_html = "\n".join(_make_category_html(c) for c in categories)

    # Domains section
    domains = stats.get("most_linked_domains", [])
    if domains:
        chips = "".join(f'<span class="domain-chip">🔗 {d}</span>' for d in domains)
        domains_section = f"""
    <div class="section-title">🌐 Most-Referenced Domains</div>
    <div class="domain-chips">{chips}</div>"""
    else:
        domains_section = ""

    # Chart data
    cat_labels = [c.get("name", "") for c in categories]
    cat_values = [c.get("message_count", 0) for c in categories]
    cat_data_json = json.dumps({"labels": cat_labels, "values": cat_values})

    activity = stats.get("activity_by_hour", {})
    hours = [f"{h:02d}" for h in range(24)]
    counts = [activity.get(h, activity.get(str(h).zfill(2), 0)) for h in range(24)]
    activity_data_json = json.dumps({"hours": hours, "counts": counts})

    html = HTML_TEMPLATE.format(
        date=date_str,
        total_messages=analysis.get("total_messages", 0),
        num_categories=len(categories),
        total_links=stats.get("total_links", 0),
        num_insights=len(insights),
        insights_html=insights_html,
        categories_html=categories_html,
        domains_section=domains_section,
        generated_at=generated_at,
        cat_data_json=cat_data_json,
        activity_data_json=activity_data_json,
    )

    if output_path:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[report] Saved to: {output_path}")

    return html
