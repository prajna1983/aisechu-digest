"""
archive_manager.py
------------------
Manages the rolling 3-month archive of daily digests.

- Scans the reports/ folder for digest files
- Deletes any HTML + JSON pairs older than RETENTION_DAYS (default: 90)
- Returns a structured list of all retained digests for index generation
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

RETENTION_DAYS = 90
DATE_PATTERN = re.compile(r"aisechu_digest_(\d{4}-\d{2}-\d{2})\.html$")


def _parse_date(filename: str) -> Optional[datetime]:
    m = DATE_PATTERN.search(filename)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _load_summary(json_path: Path) -> Dict[str, Any]:
    """Load key stats from the analysis JSON for the index card."""
    try:
        with open(json_path) as f:
            data = json.load(f)
        categories = data.get("categories", [])
        stats = data.get("stats", {})
        return {
            "total_messages": data.get("total_messages", 0),
            "num_categories": len(categories),
            "total_links": stats.get("total_links", 0),
            "top_categories": [c.get("name", "") for c in categories[:4]],
            "top_insights": data.get("top_insights", [])[:2],
        }
    except Exception:
        return {}


def run_archive(reports_dir: Path, retention_days: int = RETENTION_DAYS) -> List[Dict[str, Any]]:
    """
    Prune files older than retention_days and return metadata for all kept digests,
    sorted newest-first.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    retained = []
    deleted = []

    html_files = sorted(reports_dir.glob("aisechu_digest_*.html"))

    for html_file in html_files:
        date = _parse_date(html_file.name)
        if date is None:
            continue

        json_file = reports_dir / html_file.name.replace("aisechu_digest_", "aisechu_analysis_").replace(".html", ".json")

        if date < cutoff:
            # Delete both HTML and JSON
            html_file.unlink(missing_ok=True)
            json_file.unlink(missing_ok=True)
            deleted.append(html_file.name)
        else:
            summary = _load_summary(json_file) if json_file.exists() else {}
            retained.append({
                "date": date,
                "date_str": date.strftime("%Y-%m-%d"),
                "display_date": date.strftime("%A, %B %-d %Y"),
                "html_file": html_file.name,
                "summary": summary,
            })

    if deleted:
        print(f"[archive] Pruned {len(deleted)} digest(s) older than {retention_days} days: {', '.join(deleted)}")
    else:
        print(f"[archive] No files to prune (retention: {retention_days} days).")

    print(f"[archive] {len(retained)} digest(s) retained in archive.")

    # Newest first
    retained.sort(key=lambda x: x["date"], reverse=True)
    return retained
