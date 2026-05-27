#!/usr/bin/env python3
"""
run_digest.py
-------------
Main entry point. Run this script to generate the AISecHub daily digest.

Usage:
    python run_digest.py

Environment variables:
    ANTHROPIC_API_KEY   (required) Your Anthropic API key
    DIGEST_HOURS        (optional) How many hours back to look, default 24
    DIGEST_OUTPUT_DIR   (optional) Where to save HTML reports, default ./reports/
"""

import os
import sys
import json
import subprocess
import webbrowser
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

SGT = ZoneInfo("Asia/Singapore")


def check_dependencies():
    """Ensure required packages are installed."""
    required = ["requests", "bs4", "anthropic"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[setup] Installing missing packages: {', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + missing
        )
        print("[setup] Done.\n")


def main():
    check_dependencies()

    # ── Config ──
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it before running:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    hours = int(os.environ.get("DIGEST_HOURS", "24"))
    output_dir = Path(os.environ.get("DIGEST_OUTPUT_DIR", "./reports"))
    output_dir.mkdir(parents=True, exist_ok=True)

    date_tag = datetime.now(SGT).strftime("%Y-%m-%d")
    output_path = output_dir / f"aisechu_digest_{date_tag}.html"

    print("=" * 55)
    print("  AISecHub Daily Digest Generator")
    print("=" * 55)
    print(f"  Window : last {hours} hours")
    print(f"  Output : {output_path}")
    print()

    # ── Step 1: Fetch messages ──
    from fetch_messages import fetch_last_24h
    messages = fetch_last_24h(hours=hours)

    if not messages:
        print("\nNo messages found in the last 24 hours. The channel may be quiet,")
        print("or the page structure may have changed. Try increasing DIGEST_HOURS.")
        sys.exit(0)

    # ── Step 2: Analyze with Claude ──
    from analyze_messages import analyze
    analysis = analyze(messages, api_key=api_key)

    # Save raw analysis as JSON (useful for debugging)
    json_path = output_dir / f"aisechu_analysis_{date_tag}.json"
    with open(json_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"[main] Analysis JSON saved: {json_path}")

    # ── Step 3: Generate HTML report ──
    from generate_report import generate_html
    generate_html(analysis, output_path=str(output_path))

    # ── Step 4: Archive management — prune files older than 90 days ──
    from archive_manager import run_archive
    retained_digests = run_archive(output_dir)

    # ── Step 5: Regenerate the browsable archive index ──
    from generate_index import generate_index
    generate_index(retained_digests, output_dir)

    index_path = output_dir / "index.html"

    print()
    print("=" * 55)
    print(f"  Today's digest : {output_path}")
    print(f"  Archive index  : {index_path}")
    print("=" * 55)
    print()

    # Open the archive index in browser (it links to today's digest at the top)
    try:
        webbrowser.open(index_path.resolve().as_uri())
        print("[main] Opening archive index in your browser...")
    except Exception:
        print(f"[main] Open manually: file://{index_path.resolve()}")


if __name__ == "__main__":
    main()
